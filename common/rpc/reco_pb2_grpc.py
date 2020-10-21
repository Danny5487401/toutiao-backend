# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import reco_pb2 as reco__pb2


class UserRecommendStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.user_recommend = channel.unary_unary(
                '/UserRecommend/user_recommend',
                request_serializer=reco__pb2.UserRequest.SerializeToString,
                response_deserializer=reco__pb2.ArticleResponse.FromString,
                )


class UserRecommendServicer(object):
    """Missing associated documentation comment in .proto file."""

    def user_recommend(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UserRecommendServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'user_recommend': grpc.unary_unary_rpc_method_handler(
                    servicer.user_recommend,
                    request_deserializer=reco__pb2.UserRequest.FromString,
                    response_serializer=reco__pb2.ArticleResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'UserRecommend', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class UserRecommend(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def user_recommend(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/UserRecommend/user_recommend',
            reco__pb2.UserRequest.SerializeToString,
            reco__pb2.ArticleResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)