from grpc_tools import protoc
import grpc_tools
protoc.main((
    '',
    '-I./protos',
    '--python_out=./pub_sub_app',
    '--grpc_python_out=./pub_sub_app',
    '--python_out=./pub_sub_platform',
    '--grpc_python_out=./pub_sub_platform',
    '--experimental_allow_proto3_optional',
    './protos/pubsub.proto',
))

protoc.main((
    '',
    '-I./protos',
    '--python_out=./pub_sub_app',
    '--grpc_python_out=./pub_sub_app',
    '--python_out=./pub_sub_platform',
    '--grpc_python_out=./pub_sub_platform',
    '--experimental_allow_proto3_optional',
    './protos/node.proto',
))

protoc.main((
    '',
    '-I./protos',
    '--python_out=./pub_sub_app',
    '--grpc_python_out=./pub_sub_app',
    '--python_out=./pub_sub_platform',
    '--grpc_python_out=./pub_sub_platform',
    '--experimental_allow_proto3_optional',
    './protos/ntp.proto',
))