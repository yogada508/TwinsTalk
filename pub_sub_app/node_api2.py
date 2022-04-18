import uuid

# cat /proc/sys/kernel/pid_max 
# 32768
import os
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.absolute()))
import collections
import threading
import multiprocessing
import time
import logging

#============================================================
# import grpc protobuf
#============================================================
from concurrent import futures
print(sys.path)
import grpc
import node_pb2
import node_pb2_grpc
import ntp_pb2
import ntp_pb2_grpc
import interceptor

class Node():

    def __init__(self, node_config, update_timing=1):

        # initial variable
        if 'server_ip' not in node_config:
            print('server_ip not in node_config')
            exit(1)
        if 'server_port' not in node_config:
            print('server_port not in node_config')
            exit(1)
        if 'node_id' not in node_config:
            print('node_id not in node_config')
            exit(1)
        if 'node_name' not in node_config:
            print('node_name not in node_config')
            exit(1)
        if 'node_domain' not in node_config:
            print('node_domain not in node_config')
            exit(1)

        self.server_ip = node_config['server_ip']
        self.server_port = node_config['server_port']

        if node_config['node_id']:
            self.node_id = node_config['node_id']
        else:
            self.node_id = self.get_node_id()

        self.node_name = node_config['node_name']
        self.node_domain = node_config['node_domain']
        self.update_timing = update_timing

        # store subscriber class and process
        self.subscriber = {}

        # store ntp time offset
        self.delay = 0.0
        self.register()

    def get_node_id(self):

        mac = uuid.getnode()
        pid = os.getpid()

        return '{:02x}{}'.format(mac, pid)

    def connect_to_server(self):

        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.server_ip, self.server_port))
        self.intercept_channel = grpc.intercept_channel(
            self.channel, interceptor.NodeInterceptor())
        self.server_stub = node_pb2_grpc.ControlStub(self.intercept_channel)
        self.ntp_stub = ntp_pb2_grpc.NtpStub(self.channel)

    def register(self):
        try:
            with grpc.insecure_channel('{}:{}'.format(self.server_ip, self.server_port)) as channel:
                server_stub = node_pb2_grpc.ControlStub(channel)
                node_info = node_pb2.NodeInfo(node_id=self.node_id,
                                              node_name=self.node_name,
                                              node_domain=self.node_domain)
                responses = server_stub.Register(node_info)
        except Exception as e:
            print(e)

    def deregister(self):
        try:
            with grpc.insecure_channel('{}:{}'.format(self.server_ip, self.server_port)) as channel:
                server_stub = node_pb2_grpc.ControlStub(channel)
                node = node_pb2.Node(node_id=self.node_id)
                responses = server_stub.Deregister(node)
        except Exception as e:
            print(e)

    def subscribe(self, topic_name):
        print("subscribe", topic_name, self.subscriber)
        if topic_name in self.subscriber:
            return self.subscriber[topic_name].subscribe()
        return None

    def update_node_status(self, server_stub):
        try:
            # update node status (alive)
            node_status = node_pb2.NodeStatus(node_id=self.node_id)
            responses = server_stub.UpdateStatus(node_status, timeout=1)

        except Exception as e:
            logging.debug('Node (update_node_status): ', e)

    def ntp_sync(self, ntp_stub):
        MILLI = 1000
        MICRO = 1000000
        #delta = 25
        try:
            request = ntp_pb2.NtpRequest()
            start = round(time.time() * MICRO)
            reply = ntp_stub.Query(request, timeout=1)
            m = (round(time.time() * MICRO) - start) / 2
            self.delay = (reply.message - start - m)
            #print("self.delay: ", self.delay)
        except Exception as e:
            logging.debug('Node (ntp_sync): ', e)

    '''
    def get_topic_info(self, request_node_id, topic_name, topic_type):
        
        request_topic_info = node_pb2.RequestTopicInfo(request_node_id=request_node_id, topic_name=topic_name, topic_type=topic_type)

        try:
            responses = self.server_stub.GetTopicInfo(request_topic_info)
            topic_info = {'TopicName': responses.topic_name, 'TopicType': responses.topic_type, 'TopicIP': responses.topic_ip, 'TopicPort': responses.topic_port}
            print('TopicName={}, TopicType={}, TopicIP={}, TopicPort={}'.format(responses.topic_name,
                                                                                responses.topic_type,
                                                                                responses.topic_ip,
                                                                                responses.topic_port))

            return topic_info
        except Exception as e:
            print(e)
    '''
