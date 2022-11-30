import sys
sys.path.append("../..")

from twinstalk_api.twinstalk_server import TwinsTalk_Server
from config import CONTROLLER_IP, CONTROLLER_PORT
import json
import time

# =========== Yolo module ============
import os
# ==============================================

# =========== configure this section ===========
SERVER_IP = "140.113.193.17"
PUB_PORT = 54320
SUB_PORT = 12344
PUB_SERVER_NAME = "pub/server/Yolo"
SUB_SERVER_NAME = "sub/server/Yolo"
PUB_TOPIC_INFO = {
    "resultImage": "bytes"
}
SUB_TOPIC_INFO = {
    "enhancedImage": "bytes"
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

    # save image
    img_name = "enhanced.jpg"
    with open(f"/home/johnson/Desktop/yolov4/darknet/{img_name}", "wb") as f:
        f.write(client_data["enhancedImage"])

    cmd = "docker exec --workdir /workspace/darknet yolov4 ./darknet detector test data/obj.data yolov4-obj.cfg backup_mix/yolov4-obj_best.weights"
    src_img = "enhanced.jpg"
    args = "-gpus -dont_show"
    os.system(f"{cmd} {src_img} {args}")

    result_file = open(f"/home/johnson/Desktop/yolov4/darknet/predictions.jpg", "rb")
    data = result_file.read()

    result_data = {
        "resultImage": data
    }

    print(f"calculation time: {time.time()-start_time:.4f}")

    return result_data

if __name__ == '__main__':
    tt_server = TwinsTalk_Server(config, myfunc)
    tt_server.run()