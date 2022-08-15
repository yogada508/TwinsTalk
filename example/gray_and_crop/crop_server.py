import sys
sys.path.append("../..")

from twinstalk_api.twinstalk_server import TwinsTalk_Server
from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher
from config import CONTROLLER_IP, CONTROLLER_PORT, AGENT_IP
import time

from crop_cal import crop


# =========== configure this section ===========
SERVER_IP = "140.113.28.158"
PUB_PORT = 12333
SUB_PORT = 12444
PUB_SERVER_NAME = "pub/server/crop"
SUB_SERVER_NAME = "sub/server/crop"
PUB_TOPIC_INFO = {
    "croppedVideo": "bytes"
}
SUB_TOPIC_INFO = {
    "grayVideo": "bytes",
}
# ==============================================

pub_config = {
    "node_config": {
        "server_ip": CONTROLLER_IP,
        "server_port": CONTROLLER_PORT,
        "node_id": PUB_SERVER_NAME,
        "node_name": PUB_SERVER_NAME,
        "node_domain": "domain1"
    },
    "topic_config": {
        "mode": 1,
        "ip": SERVER_IP,
        "port": PUB_PORT,
        "topic_info": PUB_TOPIC_INFO
    }
}

sub_config = {
    "node_config": {
        "server_ip": CONTROLLER_IP,
        "server_port": CONTROLLER_PORT,
        "node_id": SUB_SERVER_NAME,
        "node_name": SUB_SERVER_NAME,
        "node_domain": "domain1"
    },
    "topic_config": {
        "mode": 0,
        "ip": SERVER_IP,
        "port": SUB_PORT,
        "topic_info": SUB_TOPIC_INFO
    }
}

config = {
    "pub_config": pub_config,
    "sub_config": sub_config
}


# User defined fuction
# The return value must contain all of the pub_topic's data
def myfunc(client_data):
    '''
    Args: 
        client_data: A dictionary that keeps the data of sub_topic
                    use client_data["topic_name"] to access data
    Returns:
        result_data: A dictionary that keeps the data of pub_topic
    '''
    
    gray_video = client_data["grayVideo"]
    print(f"[INFO] crop_server got grayVideo, size = {sys.getsizeof(gray_video)}", )

    cropped_video = crop(gray_video)

    result_data = {
        "croppedVideo": cropped_video
    }

    return result_data

if __name__ == '__main__':
    tt_server = TwinsTalk_Server(config, myfunc)
    tt_server.run()

    # pub_node = node_api.Node(config["pub_config"]["node_config"])
    # pub = Publisher.Publisher(pub_node, config["pub_config"]["topic_config"])
    # while True:
    #     time.sleep(1)