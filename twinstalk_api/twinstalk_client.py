'''

TwinsTalk Client
1. Start publisher and subscriber node
2. Add configuration connection
3. Wait connection complete
4. Pub configuration string
5. Wait agent environment complete
6. Delete configuration connection
7. Finished

'''

import time
from pub_sub_app import node_api2 as node_api, node_pb2_grpc, node_pb2
from pub_sub_app import Publisher2 as Publisher
from pub_sub_app import Subscriber2 as Subscriber
from configuration_parser.client_parser import Client_Parser as Parser
from config import CONTROLLER_IP, CONTROLLER_PORT

import threading
import grpc
import json
import sys

ignore_topic = {"configuration"}

class TwinsTalk_Client:
    def __init__(self, configuration, interval = 40):
        self.configuration = configuration
        self.interval = interval

        config = Parser(configuration).result
        self.pub_config = config["pub_config"]
        self.sub_config = config["sub_config"]
        self.connection = config["connection"]
        self.server_list = config["server_list"]

        self.pub_node_id = config["pub_config"]["node_config"]["node_id"]
        self.sub_node_id = config["sub_config"]["node_config"]["node_id"]

        self.stop_flag = threading.Event()

    def _wait_agent_environment_setting(self):
        print("Waiting agent environment setting......")

        topic_dict = self.pub_config["topic_config"]["topic_info"]
        pub_node_id = self.pub_node_id
        sub_node_id = f"sub/agent/{self.configuration['client_name']}"

        while not self.stop_flag.wait(0.5):
            ready = True
            for topic in topic_dict.keys():
                if topic in ignore_topic:
                    continue

                pub_topic_name = f"{pub_node_id}:{topic}"
                sub_topic_name = f"{sub_node_id}:{topic}_I"
                if not self.pub.has_connection(pub_topic_name, sub_topic_name):
                    ready = False
                    break

            if ready:
                print("All of Connections are ready!")
                return True

    def _init_client_environment(self):
        print("Initializing client environment....")

        pub_node = node_api.Node(self.pub_config["node_config"])
        self.pub = Publisher.Publisher(
            pub_node, self.pub_config["topic_config"])

        time.sleep(1.5)

        sub_node = node_api.Node(self.sub_config["node_config"])
        self.sub = Subscriber.Subscriber(
            sub_node, self.sub_config["topic_config"])

        print("----------------------------------")

    def _init_agent_environment(self):
        print("Initializing agent environment....")

        print("Adding configuration connection......")
        connection_id = self.pub.add_connection(
            pub_node_id=self.connection["pub_node_id"],
            sub_node_id=self.connection["sub_node_id"],
            pub_topic_name=self.connection["pub_topic_name"],
            sub_topic_name=self.connection["sub_topic_name"],
            topic_type="str"
        )

        if connection_id == "-1":
            print(
                f"Add Connection Failed: 'pub/client/configuration' -> 'sub/agent/configuration'")
            sys.exit()

        print("Publish configuration to agent:", self.configuration)
        self.pub.data_writer("configuration", json.dumps(self.configuration))

        self._wait_agent_environment_setting()

        print("Deleting configuration connection......")
        self.pub.delete_connection(connection_id)

        print("----------------------------------")

    def _check_server_alive(self):
        print("Checking server status......")

        channel = grpc.insecure_channel('{}:{}'.format(CONTROLLER_IP, CONTROLLER_PORT))
        server_stub = node_pb2_grpc.ControlStub(channel)

        all_alive = True
        for node_id in self.server_list:
            node = node_pb2.Node(node_id = node_id)
            response = server_stub.CheckNodeStatus(node)
            if not response.isAlive: 
                all_alive = False
                print(f"Server: {node_id} is currently offline.")
            else:
                print(f"Server: {node_id} is available.")

        if not all_alive:
            print("The program will end because some servers are currently unavailable.")
            sys.exit()
        
        print("----------------------------------")
    
    def terminate(self):
        self.pub.terminate()
        self.sub.terminate()

    def run(self):
        self._check_server_alive()
        self._init_client_environment()
        self._init_agent_environment()

        print("Environment is ready.")

        timer = threading.Timer(self.interval, self.terminate)
        timer.start()