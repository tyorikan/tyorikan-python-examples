from __future__ import print_function

import logging
import threading
from typing import Sequence, Tuple

import grpc
import genai_pb2
import genai_pb2_grpc


def wait_for_metadata(response_future, event):
    metadata: Sequence[Tuple[str, str]] = response_future.initial_metadata()
    for key, value in metadata:
        print("Client received initial metadata: key=%s value=%s" % (key, value))
    event.set()


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = genai_pb2_grpc.GeneratorStub(channel)

        event_for_delay = threading.Event()

        response_future_delay = stub.GenAIResponse(
            genai_pb2.MessageRequest(
                prompt="""
            あんたは、おかんのように口うるさいのが特徴や。
            質問: Google Cloud のプロダクトの Cloud Run と Spanner を詳しく説明してや！
            形式：マークダウン形式じゃなく、読みやすい素の文字列で返すんやで！
                """
            ),
            wait_for_ready=True,
        )
        # Fire RPC and wait for metadata
        thread_with_delay = threading.Thread(
            target=wait_for_metadata,
            args=(response_future_delay, event_for_delay),
            daemon=True,
        )
        thread_with_delay.start()

        # Wait on client side with 7 seconds timeout
        timeout = 5
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
