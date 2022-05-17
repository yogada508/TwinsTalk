import sys 
sys.path.append("..")
from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher
from pub_sub_app import Subscriber2 as Subscriber
from pub_sub_app import node_pb2
from pub_sub_app import node_pb2_grpc
import grpc

import time
import threading


class Agent():
    def __init__(self, config):
        self.pub_to_server_config = config["pub_to_server_config"]
        self.pub_to_client_config = config["pub_to_client_config"]
        self.sub_config = config["sub_config"]
        self.connections = config["connections"]
        self.pub_to_server_table = {}
        self.pub_to_client_table = {}

        self.init_table()

    # odf and idf route table
    def init_table(self):
        for pub_topic in self.pub_to_server_config["topic_config"]["topic_info"]:
            sub_topic = pub_topic[:-1] + "I"
            self.pub_to_server_table[pub_topic] = sub_topic

        for pub_topic in self.pub_to_client_config["topic_config"]["topic_info"]:
            sub_topic = pub_topic[:-1] + "I"
            self.pub_to_client_table[pub_topic] = sub_topic

    # start pub node (to server)
    def start_publisher_to_server(self):
        node_config, topic_config = self.pub_to_server_config[
            "node_config"], self.pub_to_server_config["topic_config"]
        node = node_api.Node(node_config)
        pub = Publisher.Publisher(node, topic_config)

        self.pub_to_server = pub

    # start pub node (to client)
    def start_publisher_to_client(self):
        node_config, topic_config = self.pub_to_client_config[
            "node_config"], self.pub_to_client_config["topic_config"]
        node = node_api.Node(node_config)
        pub = Publisher.Publisher(node, topic_config)

        self.node = node
        self.pub_to_client = pub

    # start sub node
    def start_subscriber(self):
        node_config, topic_config = self.sub_config["node_config"], self.sub_config["topic_config"]
        node = node_api.Node(node_config)
        sub = Subscriber.Subscriber(node, topic_config)

        self.sub = sub

    # create connection (client -> agent, agent -> server, agent -> client)
    def set_connection(self):
        server_ip = (self.pub_to_server_config)["node_config"]["server_ip"]
        server_port = (self.pub_to_server_config)["node_config"]["server_port"]
        server_address = f"{server_ip}:{server_port}"

        connection_ids = []
        with grpc.insecure_channel(server_address) as channel:
            stub = node_pb2_grpc.ControlStub(channel)

            for conn in self.connections:
                subNodeID_tokens = conn["sub_node_id"].split("/")
                if "client" in subNodeID_tokens:
                    self.client_id = conn["sub_node_id"]

                # connections for client -> agent and agent -> client
                if "agent" in subNodeID_tokens or "client" in subNodeID_tokens:
                    
                    ConnectionInfo = node_pb2.ConnectionInfo(
                        pub_node_id=conn["pub_node_id"],
                        sub_node_id=conn["sub_node_id"],
                        pub_topic_name=conn["pub_topic_name"],
                        sub_topic_name=conn["sub_topic_name"],
                        topic_type=conn["topic_type"]
                    )

                    response = stub.AddConnection(ConnectionInfo)
                    connection_id = response.connection_id

                    if connection_id != -1:
                        connection_ids.append(connection_id)
                    else:
                        print("add connection fail:", conn)

                # connections for agent -> server
                elif "server" in subNodeID_tokens:
                    connection_id = self.pub_to_server.add_connection(
                        pub_node_id=conn["pub_node_id"],
                        sub_node_id=conn["sub_node_id"],
                        pub_topic_name=conn["pub_topic_name"],
                        sub_topic_name=conn["sub_topic_name"],
                        topic_type=conn["topic_type"]
                    )

                    if connection_id != -1:
                        connection_ids.append(connection_id)
                    else:
                        print("add connection fail:", conn)

        print(connection_ids)

    def check_client_status(self):
        server_ip = (self.pub_to_server_config)["node_config"]["server_ip"]
        server_port = (self.pub_to_server_config)["node_config"]["server_port"]
        server_address = f"{server_ip}:{server_port}"

        with grpc.insecure_channel(server_address) as channel:
            self.stub = node_pb2_grpc.ControlStub(channel)
            response = self.stub.CheckNodeStatus(
                node_pb2.Node(node_id= self.client_id)
            )
            if response.isAlive:
                return True
            else:
                return False
            

    def start(self):

        self.start_publisher_to_server()

        self.start_publisher_to_client()

        self.start_subscriber()
        time.sleep(1)

        print("Starting add connection!")
        self.set_connection()

        # read and write data
        try:
            while True:
                if not self.check_client_status():
                    raise BaseException("Client Offline")
                
                self.sub.updata_data()
                for pub_topic, sub_topic in self.pub_to_server_table.items():
                    proto_data = self.sub.read_topic(sub_topic)
                    if proto_data is not None:
                        print(f"pub to server {pub_topic}")
                        self.pub_to_server.data_writer(
                            pub_topic, proto_data.data)

                for pub_topic, sub_topic in self.pub_to_client_table.items():
                    proto_data = self.sub.read_topic(sub_topic)
                    if proto_data is not None:
                        print(f"pub to client {pub_topic}")
                        self.pub_to_client.data_writer(
                            pub_topic, proto_data.data)

                time.sleep(1)

        except Exception as e:
            print("[Error]: agent:", e)

        finally:
            self.pub_to_client.terminate()
            self.pub_to_server.terminate()
            self.sub.terminate()
