# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import genai_pb2 as genai__pb2

GRPC_GENERATED_VERSION = '1.66.1'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in genai_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class GeneratorStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GenAIResponse = channel.unary_stream(
                '/genai.Generator/GenAIResponse',
                request_serializer=genai__pb2.MessageRequest.SerializeToString,
                response_deserializer=genai__pb2.MessageResponse.FromString,
                _registered_method=True)


class GeneratorServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GenAIResponse(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GeneratorServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GenAIResponse': grpc.unary_stream_rpc_method_handler(
                    servicer.GenAIResponse,
                    request_deserializer=genai__pb2.MessageRequest.FromString,
                    response_serializer=genai__pb2.MessageResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'genai.Generator', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('genai.Generator', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Generator(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GenAIResponse(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/genai.Generator/GenAIResponse',
            genai__pb2.MessageRequest.SerializeToString,
            genai__pb2.MessageResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
