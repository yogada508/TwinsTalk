import sys
sys.path.append("..")

from pub_sub_app import node_api2 as node_api
from pub_sub_app import Subscriber2 as Subscriber
from configuration_parser.agent_parser import Agent_Parser as Parser
from config import CONTROLLER_IP, CONTROLLER_PORT, AGENT_IP, CONFIGURATION_PORT

import grpc
import json
import threading
from multiprocessing import Process
import agent
import time

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
        "port": CONFIGURATION_PORT
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
    agent_process = []

    try:
        while True:
            try:
                sub.updata_data()
                config_data = sub.read_topic("configuration")
                if config_data:
                    print("get config data", config_data.data)

                    config = json.loads(config_data.data)
                    parse_result = Parser(config).get_parse_result()
                    process = Process(
                        target=run_agent, args=(parse_result,))
                    agent_process.append(process)
                    process.start()
                time.sleep(0.5)

            except Exception as e:
                print(e)

    except Exception as e:
        print(e)

    finally:
        for t in agent_process:
            t.join()


if __name__ == '__main__':
    main()