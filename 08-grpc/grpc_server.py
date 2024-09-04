from concurrent import futures
import logging

import grpc
import genai_pb2
import genai_pb2_grpc

import vertexai
from vertexai.generative_models import GenerativeModel
import os

vertexai.init(project=os.environ["GOOGLE_CLOUD_PROJECT"], location="asia-northeast1")
model = GenerativeModel(
    "gemini-1.5-flash-001",
)

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}


class GenAI(genai_pb2_grpc.GeneratorServicer):
    def GenAIResponse(self, request, context):
        try:
            responses = model.generate_content(
                [request.prompt],
                generation_config=generation_config,
                stream=True,
            )

            # Sending actual response.
            for response in responses:
                yield genai_pb2.MessageResponse(message=response.text)
        except ValueError as e:
            yield genai_pb2.MessageResponse(
                message="LLM からのデータ取得に失敗しました"
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
