import sys
sys.path.append("../..")

from example.updrs.grasp_cal import render_video
from twinstalk_api.twinstalk_client import TwinsTalk_Client
import json
import time


def main():
    with open("deepspeech.json") as f:
        configuration = json.load(f)

    tt_client = TwinsTalk_Client(configuration, is_streaming=True, interval=40)
    tt_client.run()

    i = 0

    file = open("2830-3980-0043.wav", "rb")
    data = file.read()

    tt_client.pub.data_writer('audioName', "test_audio.wav")
    tt_client.pub.data_writer('audioData', data)
    audio_data_start = time.time()
    print("end, len of file", len(data))

    while True:
        tt_client.sub.updata_data()
        text_result = tt_client.sub.read_topic('text')

        if text_result is not None:
            print("text_result RTT: ", time.time()-audio_data_start)
            print(text_result.data)
            break

    tt_client.sub.terminate()
    tt_client.pub.terminate()

if __name__ == '__main__':
    main()