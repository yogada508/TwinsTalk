import json
import socket

SERVER_IP = "140.113.28.158"
SERVER_PORT = "55555"
AGENT_IP = "127.0.0.1"

class ConfigurationParser():
    def __init__(self, config):
        self.config = config
        self.parse_result = {}
        self._parse()
    
    def set_config(self, config):
        self.config = config
        self._parse()
    
    def get_parse_result(self):
        return self.parse_result
    
    def _get_free_port(self):
        sock = socket.socket()
        sock.bind(('', 0))
        return sock.getsockname()[1]
        
    def _parse(self):
        client_name = self.config["client_name"]
        pub_node_id = f"pub/agent/{client_name}"
        sub_node_id = f"sub/agent/{client_name}"
        client_sub_node_id = f"sub/client/{client_name}"

        idf = {}
        odf = {}
        connections = []

        odf_pattern = "{}_O"  # f"{topic_name}_O"
        idf_pattern = "{}_I"  # f"{topic_name}_I"

        for node in self.config["node"]:

            # publisher ODF
            for inp in node["input"]:
                odf_name = odf_pattern.format(inp['topic_name'])
                idf_name = idf_pattern.format(inp['topic_name'])
                if odf_name not in odf: odf[odf_name] = inp["data_type"]
                if idf_name not in idf: idf[idf_name] = inp["data_type"]

                # connection
                server_node_id = f"sub/server/{node['calculator']}"
                connections.append({
                    "pub_node_id": pub_node_id,
                    "pub_topic_name": f"{pub_node_id}:{odf_name}",
                    "sub_node_id": server_node_id,
                    "sub_topic_name": f"{server_node_id}:{inp['topic_name']}",
                    "topic_type": inp["data_type"]
                })
                
            # subscriber IDF
            for out in node["output"]:
                odf_name = odf_pattern.format(out['topic_name'])
                idf_name = idf_pattern.format(out['topic_name'])
                if odf_name not in odf: odf[odf_name] = out["data_type"]
                if idf_name not in idf: idf[idf_name] = out["data_type"]
        
        # connection
        for out in self.config["output"]:
            odf_name = odf_pattern.format(out['topic_name'])
            connections.append({
                "pub_node_id": pub_node_id,
                "pub_topic_name": f"{pub_node_id}:{odf_name}",
                "sub_node_id": client_sub_node_id,
                "sub_topic_name": f"{client_sub_node_id}:{out['topic_name']}",
                "topic_type": out["data_type"]
            })

        # pub
        pub_config = {
            "node_config": {
                "server_ip": SERVER_IP,
                "server_port": SERVER_PORT,
                "node_id": pub_node_id,
                "node_name": pub_node_id,
                "node_domain": "domain1"
            },
            "topic_config": {
                "mode": 0,
                "ip": AGENT_IP,
                "port": self._get_free_port(),
                "topic_info": odf 
            }
        }

        # sub
        sub_config = {
            "node_config": {
                "server_ip": SERVER_IP,
                "server_port": SERVER_PORT,
                "node_id": sub_node_id,
                "node_name": sub_node_id,
                "node_domain": "domain1"
            },
            "topic_config": {
                "mode": 0,
                "ip": AGENT_IP,
                "port": self._get_free_port(),
                "topic_info": idf 
            }
        }

        self.parse_result =  {
            "pub_config": pub_config,
            "sub_config": sub_config,
            "connections": connections
        }