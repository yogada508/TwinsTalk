import sys
sys.path.append("../..")

from twinstalk_api.twinstalk_server import TwinsTalk_Server
from config import CONTROLLER_IP, CONTROLLER_PORT
import json
from example.updrs.grasp_cal import find_peak, render_video
import time

# =========== configure this section ===========
SERVER_IP = "140.113.28.159"
PUB_PORT = 54322
SUB_PORT = 12346
PUB_SERVER_NAME = "pub/server/render"
SUB_SERVER_NAME = "sub/server/render"
PUB_TOPIC_INFO = {
    "renderedVideo": "bytes",
    "graspResult": "str"
}
SUB_TOPIC_INFO = {
    "videoName": "str",
    "videoData": "bytes",
    "annotation": "bytes"
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

    annotation = json.loads(client_data["annotation"].decode("utf-8"))
    record_right = annotation["right_hand"]
    record_left = annotation["left_hand"]
    right_lost = annotation["right_lost"]
    left_lost = annotation["left_lost"]

    fist_closing_frame, action_time_list = find_peak(record_right,record_left)
    rendered_video, grasp_result = render_video(video_name, fist_closing_frame, action_time_list, right_lost, left_lost)

    result_data = {
        "renderedVideo": rendered_video,
        "graspResult": grasp_result
    }

    print(f"calculation time: {time.time()-start_time:.4f}")

    return result_data

if __name__ == '__main__':
    tt_server = TwinsTalk_Server(config, myfunc)
    tt_server.run()