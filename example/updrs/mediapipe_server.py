import sys
sys.path.append("../..")

from twinstalk_api.twinstalk_server import TwinsTalk_Server
from config import CONTROLLER_IP, CONTROLLER_PORT
import json
from example.updrs.mediapipe_hand import hand_detection
import time

# =========== configure this section ===========
SERVER_IP = "140.113.28.159"
PUB_PORT = 54321
SUB_PORT = 12345
PUB_SERVER_NAME = "pub/server/mediapipe"
SUB_SERVER_NAME = "sub/server/mediapipe"
PUB_TOPIC_INFO = {
    "annotation": "bytes"
}
SUB_TOPIC_INFO = {
    "videoName": "str",
    "videoData": "bytes"
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

    start_time = time.time()

    # save video
    video_name = client_data["videoName"]
    with open(video_name, "wb") as f:
        f.write(client_data["videoData"])
    
    # video_name = client_data["videoName"]
    # video_data = client_data["videoData"]

    img_list,record_right,record_left,right_lost,left_lost,img_lost = hand_detection(video_name)

    data = {
        "right_hand": record_right,
        "left_hand": record_left,
        "right_lost": right_lost,
        "left_lost": left_lost
    }

    result_data = {
        "annotation": json.dumps(data).encode("utf-8")
    }

    print(f"calculation time: {time.time()-start_time:.4f}")

    return result_data

if __name__ == '__main__':
    tt_server = TwinsTalk_Server(config, myfunc)
    tt_server.run()