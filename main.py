from pub_sub_app import node_api2 as node_api
from pub_sub_app import Subscriber2 as Subscriber
from configuration_parser.agent_parser import Agent_Parser as Parser

import grpc
import json
import threading
import agent
import time

CONTROLLER_IP = "140.113.193.15"
CONTROLLER_PORT = 55555

AGENT_IP = "140.113.193.15"
CONFIG_PORT = 54321

# to listening configuration file
sub_config = {
    "node_config": {
        'server_ip': CONTROLLER_IP,
        'server_port': CONTROLLER_PORT,
        'node_id': "sub/agent/config",
        'node_name': "sub/agent/config",
        'node_domain': 'Domain1',
    },
    "topic_config": {
        "topic_info": {
            "configuration": "str"
        },
        "mode": 0,
        "ip": AGENT_IP,
        "port": CONFIG_PORT
    }
}


def start_config_sub():
    node = node_api.Node(sub_config["node_config"])
    sub = Subscriber.Subscriber(node, sub_config["topic_config"])

    return sub


def run_agent(config):
    ag = agent.Agent(config)
    ag.start()


def main():
    sub = start_config_sub()
    agent_threads = []

    try:
        while True:
            try:
                sub.updata_data()
                config_data = sub.read_topic("configuration")
                if config_data:
                    print("get config data", config_data.data)

                    config = json.loads(config_data.data)
                    parse_result = Parser(config).get_parse_result()
                    thread = threading.Thread(
                        target=run_agent, args=(parse_result,))
                    agent_threads.append(thread)
                    thread.start()
                time.sleep(0.5)

            except Exception as e:
                print(e)

    except Exception as e:
        print(e)

    finally:
        for t in agent_threads:
            t.join()


if __name__ == '__main__':
    main()

    # RequestAddConnection = node_pb2.RequestAddConnection(pub_node_id=pub_node_id, sub_node_id=sub_node_id, pub_topic_name=pub_topic_name, sub_topic_name=sub_topic_name, topic_type=topic_type)

    # connection_id = None
    # with grpc.insecure_channel(SERVER_ADDRESS) as channel:
    #     stub = node_pb2_grpc.ControlStub(channel)
    #     response = stub.AddConnection(RequestAddConnection)
    #     # time.sleep(2)
    #     connection_id = response.connection_id
    #     print(connection_id)

    # if connection_id:
    #     RequestDelConnection = node_pb2.RequestDelConnection(connection_id = str(connection_id))
    #     with grpc.insecure_channel(SERVER_ADDRESS) as channel:
    #         stub = node_pb2_grpc.ControlStub(channel)
    #         stub.DeleteConnection(RequestDelConnection)
