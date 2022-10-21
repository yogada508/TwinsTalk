import sys
sys.path.append("../..")

from twinstalk_api.twinstalk_server import TwinsTalk_Server
from config import CONTROLLER_IP, CONTROLLER_PORT
import json
import time

# =========== Speech to text module ============
from deepspeech import Model
import wave
import numpy as np
# ==============================================

# =========== configure this section ===========
SERVER_IP = "140.113.193.24"
PUB_PORT = 54320
SUB_PORT = 12344
PUB_SERVER_NAME = "pub/server/deepspeech"
SUB_SERVER_NAME = "sub/server/deepspeech"
PUB_TOPIC_INFO = {
    "text": "str"
}
SUB_TOPIC_INFO = {
    "audioName": "str",
    "audioData": "bytes"
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
    audio_name = client_data["audioName"]
    with open(audio_name, "wb") as f:
        f.write(client_data["audioData"])

    ds = Model("./deepspeech-0.9.3-models.pbmm")
    ds.enableExternalScorer("./deepspeech-0.9.3-models.scorer")

    fin = wave.open(audio_name, 'rb')
    audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)
    fin.close()

    result = ds.stt(audio)

    result_data = {
        "text": result
    }

    print(f"calculation time: {time.time()-start_time:.4f}")

    return result_data

if __name__ == '__main__':
    tt_server = TwinsTalk_Server(config, myfunc)
    tt_server.run()