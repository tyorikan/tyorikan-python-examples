from concurrent import futures
import logging

import grpc
import genai_pb2
import genai_pb2_grpc

import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    Content,
    Part,
    HarmCategory,
    HarmBlockThreshold,
)
import os

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


class GenAI(genai_pb2_grpc.GeneratorServicer):
    def __init__(self):
        super().__init__()
        self.history = []

    def GenAIResponse(self, request, context):
        try:
            # TODO DB から取得して append する
            self.history.append(
                Content(role="user", parts=[Part.from_text(request.prompt)])
            )

            responses = model.generate_content(
                contents=self.history,
                generation_config=generation_config,
                stream=True,
            )

            # Sending actual response.
            fulltext = ""
            for response in responses:
                yield genai_pb2.MessageResponse(message=response.text)
                fulltext += response.text

            # TODO DB に追加する
            self.history.append(Content(role="model", parts=[Part.from_text(fulltext)]))

        except ValueError as e:
            yield genai_pb2.MessageResponse(
                message="LLM からのデータ取得に失敗しました - " + str(e)
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
