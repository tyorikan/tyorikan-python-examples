from __future__ import print_function

import logging
import os
import threading
from typing import Sequence, Tuple

import genai_pb2
import genai_pb2_grpc
import grpc


def wait_for_metadata(response_future, event):
    metadata: Sequence[Tuple[str, str]] = response_future.initial_metadata()
    for key, value in metadata:
        print("Client received initial metadata: key=%s value=%s" % (key, value))
    event.set()


def run():
    with grpc.insecure_channel("localhost:50051") if os.environ.get(
        "GRPC_ADDR"
    ) is None else grpc.secure_channel(
        os.environ["GRPC_ADDR"],
        grpc.ssl_channel_credentials(),
    ) as channel:
        stub = genai_pb2_grpc.GeneratorStub(channel)

        while True:
            event_for_delay = threading.Event()
            prompt = input(
                "プロンプトを入力してください（終わりたいときは exit と入力して）："
            )
            if prompt == "exit":
                break

            response_future_delay = stub.GenAIResponse(
                genai_pb2.MessageRequest(prompt=prompt),
                wait_for_ready=True,
            )
            # Fire RPC and wait for metadata
            thread_with_delay = threading.Thread(
                target=wait_for_metadata,
                args=(response_future_delay, event_for_delay),
                daemon=True,
            )
            thread_with_delay.start()

            # Wait on client side with 10 seconds timeout
            timeout = 10
            check_status(response_future_delay, event_for_delay.wait(timeout))


def check_status(response_future, wait_success):
    if wait_success:
        for response in response_future:
            print(response.message)
    else:
        print("Timed out before receiving any initial metadata!")
        response_future.cancel()


if __name__ == "__main__":
    logging.basicConfig()
    run()
