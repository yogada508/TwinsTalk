'''

TwinsTalk Cleint
1. Start publisher and subscriber node
2. Add configuration connection
3. Wait connection complete
4. Pub configuration string
5. Wait agent environment complete
6. Delete configuration connection
7. Finished

'''

import time
from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher
from pub_sub_app import Subscriber2 as Subscriber
from configuration_parser.client_parser import Client_Parser as Parser
import threading
import json
import sys


class TwinsTalk_Client:
    def __init__(self, configuration):
        self.configuration = configuration

        config = Parser(configuration).result
        self.pub_config = config["pub_config"]
        self.sub_config = config["sub_config"]
        self.connection = config["connection"]

        self.pub_node_id = config["pub_config"]["node_config"]["node_id"]
        self.sub_node_id = config["sub_config"]["node_config"]["node_id"]

        self.stop_flag = threading.Event()

    def _wait_configuration_connection(self):
        print("Waiting for 'configuration' connection...")

        pub_topic_name = self.connection["pub_topic_name"]
        sub_topic_name = self.connection["sub_topic_name"]
        while not self.stop_flag.wait(0.5):
            if self.pub.has_connection(pub_topic_name, sub_topic_name):
                print(f"Connected: {pub_topic_name} and {sub_topic_name}")
                return

    def _wait_agent_environment_setting(self):
        print("Waiting agent environment setting......")

        topic_dict = self.pub_config["topic_config"]["topic_info"]
        pub_node_id = self.pub_node_id
        sub_node_id = f"sub/agent/{self.configuration['client_name']}"

        while not self.stop_flag.wait(0.5):
            ready = True
            for topic in topic_dict.keys():
                if topic == "configuration":
                    continue

                pub_topic_name = f"{pub_node_id}:{topic}"
                sub_topic_name = f"{sub_node_id}:{topic}_I"
                if not self.pub.has_connection(pub_topic_name, sub_topic_name):
                    ready = False
                    # print(f"Not Connected: '{pub_topic_name}' and '{sub_topic_name}'")
                    break
                # else:
                #     print(f"Connected: '{pub_topic_name}' -> '{sub_topic_name}'")

            if ready:
                print("All of Connections are ready!")
                return True
            # else:
            #     print("Some connections haven't been established.")
            #     print("Rechecking...")
            #     print("---")

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

        self._wait_configuration_connection()

        print("Publish configuration to agent:", self.configuration)
        self.pub.data_writer("configuration", json.dumps(self.configuration))

        self._wait_agent_environment_setting()

        print("Deleting configuration connection......")
        self.pub.delete_connection(connection_id)

        print("----------------------------------")

    def run(self):
        self._init_client_environment()
        self._init_agent_environment()

        print("Environment is ready.")
