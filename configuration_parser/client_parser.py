import sys
sys.path.append("..")
import json
import socket
from config import CONTROLLER_IP, CONTROLLER_PORT, CLIENT_IP

class Client_Parser():
    def __init__(self, configuration):
        self.configuration = configuration
        self._parse()

    def result(self):
        return self.parse_result

    def _get_free_port(self):
        sock = socket.socket()
        sock.bind(('', 0))
        return sock.getsockname()[1]

    def _parse(self):
        client_name = self.configuration["client_name"]
        pub_node_id = f"pub/client/{client_name}"
        sub_node_id = f"sub/client/{client_name}"

        idf = {}
        odf = {}
        connection = {}
        server_list = [] # all servers that need to be checked for liveness

        for inp in self.configuration["input"]:
            odf[inp["topic_name"]] = inp["data_type"]

        for out in self.configuration["output"]:
            idf[out["topic_name"]] = out["data_type"]
        
        for node in self.configuration["node"]:
            server_list.append(f"sub/server/{node['calculator']}")
            server_list.append(f"pub/server/{node['calculator']}")

        # add configuration topic
        odf["configuration"] = "str"

        # add configuration connection
        connection = {
            "pub_node_id": pub_node_id,
            "pub_topic_name": f"{pub_node_id}:configuration",
            "sub_node_id": "sub/agent/config",
            "sub_topic_name": "sub/agent/config:configuration",
            "topic_type": "str"
        }

        # publiser (to agent)
        pub_config = {
            "node_config": {
                "server_ip": CONTROLLER_IP,
                "server_port": CONTROLLER_PORT,
                "node_id": pub_node_id,
                "node_name": pub_node_id,
                "node_domain": "domain1"
            },
            "topic_config": {
                "mode": 1,
                "ip": CLIENT_IP,
                "port": self._get_free_port(),
                "topic_info": odf
            }
        }

        # subscriber
        sub_config = {
            "node_config": {
                "server_ip": CONTROLLER_IP,
                "server_port": CONTROLLER_PORT,
                "node_id": sub_node_id,
                "node_name": sub_node_id,
                "node_domain": "domain1"
            },
            "topic_config": {
                "mode": 1,
                "ip": CLIENT_IP,
                "port": self._get_free_port(),
                "topic_info": idf
            }
        }

        self.result = {
            "pub_config": pub_config,
            "sub_config": sub_config,
            "connection": connection,
            "server_list": server_list
        }
