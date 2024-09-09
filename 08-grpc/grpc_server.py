import logging
import os
from concurrent import futures

import genai_pb2
import genai_pb2_grpc
import grpc
import vertexai
from google.cloud import firestore
from vertexai.generative_models import (
    Content,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)

vertexai.init(project=os.environ["GOOGLE_CLOUD_PROJECT"], location="asia-northeast1")
model = GenerativeModel(
    model_name="gemini-1.5-flash-001",
    system_instruction="あなたは最高に明るく、ポジティブで面白い人です。たまに面白いことを話しつつ簡潔に会話してください。",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    },
)

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

# Firestore クライアントの初期化
db = firestore.Client(project=os.environ["GOOGLE_CLOUD_PROJECT"])


class GenAI(genai_pb2_grpc.GeneratorServicer):
    def GenAIResponse(self, request, context):
        try:
            history = []

            # Firestore から過去の会話を取得
            client_id = request.uuid
            history = self.load_history(client_id)

            history.append(Content(role="user", parts=[Part.from_text(request.prompt)]))
            # 会話を Firestore に保存
            self.save_history(client_id, "user", request.prompt)

            responses = model.generate_content(
                contents=history,
                generation_config=generation_config,
                stream=True,
            )

            # Sending actual response.
            fulltext = ""
            for response in responses:
                yield genai_pb2.MessageResponse(message=response.text)
                fulltext += response.text

            # 会話を Firestore に保存
            self.save_history(client_id, "model", fulltext)

        except ValueError as e:
            yield genai_pb2.MessageResponse(
                message="LLM からのデータ取得に失敗しました - " + str(e)
            )

    def load_history(self, client_id):
        # Firestore から client_id に紐づく過去の会話を取得
        docs = (
            db.collection("clients")
            .document(client_id)
            .collection("messages")
            .order_by("timestamp")
            .stream()
        )
        history = []
        for doc in docs:
            data = doc.to_dict()
            history.append(
                Content(role=data["role"], parts=[Part.from_text(data["message"])])
            )
        return history

    def save_history(self, client_id, role, message):
        # Firestore に client_id に紐づけて会話を保存
        db.collection("clients").document(client_id).collection("messages").add(
            {
                "role": role,
                "message": message,
                "timestamp": firestore.SERVER_TIMESTAMP,
            }
        )


def serve():
    port = os.environ.get("PORT") or "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    genai_pb2_grpc.add_GeneratorServicer_to_server(GenAI(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
