# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import node_pb2 as node__pb2


class ControlStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Register = channel.unary_unary(
                '/node.Control/Register',
                request_serializer=node__pb2.NodeInfo.SerializeToString,
                response_deserializer=node__pb2.Empty.FromString,
                )
        self.Deregister = channel.unary_unary(
                '/node.Control/Deregister',
                request_serializer=node__pb2.Node.SerializeToString,
                response_deserializer=node__pb2.Empty.FromString,
                )
        self.UpdateStatus = channel.unary_unary(
                '/node.Control/UpdateStatus',
                request_serializer=node__pb2.NodeStatus.SerializeToString,
                response_deserializer=node__pb2.Empty.FromString,
                )
        self.CheckNodeStatus = channel.unary_unary(
                '/node.Control/CheckNodeStatus',
                request_serializer=node__pb2.Node.SerializeToString,
                response_deserializer=node__pb2.NodeAlive.FromString,
                )
        self.AddTopic = channel.unary_unary(
                '/node.Control/AddTopic',
                request_serializer=node__pb2.TopicInfo.SerializeToString,
                response_deserializer=node__pb2.Empty.FromString,
                )
        self.DeleteTopic = channel.unary_unary(
                '/node.Control/DeleteTopic',
                request_serializer=node__pb2.Topic.SerializeToString,
                response_deserializer=node__pb2.Empty.FromString,
                )
        self.UpdateTopicStatus = channel.unary_unary(
                '/node.Control/UpdateTopicStatus',
                request_serializer=node__pb2.TopicStatus.SerializeToString,
                response_deserializer=node__pb2.Empty.FromString,
                )
        self.UpdateTopicState = channel.unary_unary(
                '/node.Control/UpdateTopicState',
                request_serializer=node__pb2.Topic.SerializeToString,
                response_deserializer=node__pb2.TopicAlive.FromString,
                )
        self.AddSubscribeTopic = channel.unary_unary(
                '/node.Control/AddSubscribeTopic',
                request_serializer=node__pb2.SubscribeTopic.SerializeToString,
                response_deserializer=node__pb2.Empty.FromString,
                )
        self.UpdateSubscribeTopicStatus = channel.unary_unary(
                '/node.Control/UpdateSubscribeTopicStatus',
                request_serializer=node__pb2.SubscribeTopicStatus.SerializeToString,
                response_deserializer=node__pb2.Empty.FromString,
                )
        self.DeleteSubscribeTopic = channel.unary_unary(
                '/node.Control/DeleteSubscribeTopic',
                request_serializer=node__pb2.SubscribeTopicInfo.SerializeToString,
                response_deserializer=node__pb2.Empty.FromString,
                )
        self.GetConnection = channel.unary_unary(
                '/node.Control/GetConnection',
                request_serializer=node__pb2.RequestConnection.SerializeToString,
                response_deserializer=node__pb2.ResponseConnection.FromString,
                )
        self.DeleteConnection = channel.unary_unary(
                '/node.Control/DeleteConnection',
                request_serializer=node__pb2.ConnectionID.SerializeToString,
                response_deserializer=node__pb2.Empty.FromString,
                )
        self.AddConnection = channel.unary_unary(
                '/node.Control/AddConnection',
                request_serializer=node__pb2.ConnectionInfo.SerializeToString,
                response_deserializer=node__pb2.ConnectionID.FromString,
                )


class ControlServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Deregister(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckNodeStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddTopic(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteTopic(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateTopicStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateTopicState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddSubscribeTopic(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateSubscribeTopicStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteSubscribeTopic(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetConnection(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteConnection(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddConnection(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ControlServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=node__pb2.NodeInfo.FromString,
                    response_serializer=node__pb2.Empty.SerializeToString,
            ),
            'Deregister': grpc.unary_unary_rpc_method_handler(
                    servicer.Deregister,
                    request_deserializer=node__pb2.Node.FromString,
                    response_serializer=node__pb2.Empty.SerializeToString,
            ),
            'UpdateStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateStatus,
                    request_deserializer=node__pb2.NodeStatus.FromString,
                    response_serializer=node__pb2.Empty.SerializeToString,
            ),
            'CheckNodeStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.CheckNodeStatus,
                    request_deserializer=node__pb2.Node.FromString,
                    response_serializer=node__pb2.NodeAlive.SerializeToString,
            ),
            'AddTopic': grpc.unary_unary_rpc_method_handler(
                    servicer.AddTopic,
                    request_deserializer=node__pb2.TopicInfo.FromString,
                    response_serializer=node__pb2.Empty.SerializeToString,
            ),
            'DeleteTopic': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteTopic,
                    request_deserializer=node__pb2.Topic.FromString,
                    response_serializer=node__pb2.Empty.SerializeToString,
            ),
            'UpdateTopicStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateTopicStatus,
                    request_deserializer=node__pb2.TopicStatus.FromString,
                    response_serializer=node__pb2.Empty.SerializeToString,
            ),
            'UpdateTopicState': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateTopicState,
                    request_deserializer=node__pb2.Topic.FromString,
                    response_serializer=node__pb2.TopicAlive.SerializeToString,
            ),
            'AddSubscribeTopic': grpc.unary_unary_rpc_method_handler(
                    servicer.AddSubscribeTopic,
                    request_deserializer=node__pb2.SubscribeTopic.FromString,
                    response_serializer=node__pb2.Empty.SerializeToString,
            ),
            'UpdateSubscribeTopicStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateSubscribeTopicStatus,
                    request_deserializer=node__pb2.SubscribeTopicStatus.FromString,
                    response_serializer=node__pb2.Empty.SerializeToString,
            ),
            'DeleteSubscribeTopic': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteSubscribeTopic,
                    request_deserializer=node__pb2.SubscribeTopicInfo.FromString,
                    response_serializer=node__pb2.Empty.SerializeToString,
            ),
            'GetConnection': grpc.unary_unary_rpc_method_handler(
                    servicer.GetConnection,
                    request_deserializer=node__pb2.RequestConnection.FromString,
                    response_serializer=node__pb2.ResponseConnection.SerializeToString,
            ),
            'DeleteConnection': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteConnection,
                    request_deserializer=node__pb2.ConnectionID.FromString,
                    response_serializer=node__pb2.Empty.SerializeToString,
            ),
            'AddConnection': grpc.unary_unary_rpc_method_handler(
                    servicer.AddConnection,
                    request_deserializer=node__pb2.ConnectionInfo.FromString,
                    response_serializer=node__pb2.ConnectionID.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'node.Control', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Control(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/Register',
            node__pb2.NodeInfo.SerializeToString,
            node__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Deregister(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/Deregister',
            node__pb2.Node.SerializeToString,
            node__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/UpdateStatus',
            node__pb2.NodeStatus.SerializeToString,
            node__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CheckNodeStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/CheckNodeStatus',
            node__pb2.Node.SerializeToString,
            node__pb2.NodeAlive.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddTopic(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/AddTopic',
            node__pb2.TopicInfo.SerializeToString,
            node__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteTopic(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/DeleteTopic',
            node__pb2.Topic.SerializeToString,
            node__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateTopicStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/UpdateTopicStatus',
            node__pb2.TopicStatus.SerializeToString,
            node__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateTopicState(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/UpdateTopicState',
            node__pb2.Topic.SerializeToString,
            node__pb2.TopicAlive.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddSubscribeTopic(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/AddSubscribeTopic',
            node__pb2.SubscribeTopic.SerializeToString,
            node__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateSubscribeTopicStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/UpdateSubscribeTopicStatus',
            node__pb2.SubscribeTopicStatus.SerializeToString,
            node__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteSubscribeTopic(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/DeleteSubscribeTopic',
            node__pb2.SubscribeTopicInfo.SerializeToString,
            node__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetConnection(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/GetConnection',
            node__pb2.RequestConnection.SerializeToString,
            node__pb2.ResponseConnection.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteConnection(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/DeleteConnection',
            node__pb2.ConnectionID.SerializeToString,
            node__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddConnection(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/node.Control/AddConnection',
            node__pb2.ConnectionInfo.SerializeToString,
            node__pb2.ConnectionID.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
