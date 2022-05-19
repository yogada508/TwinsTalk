from twinstalk_api.twinstalk_client import TwinsTalk_Client
import json
import time


def main():
    with open("test_config.json") as f:
        configuration = json.load(f)

    tt_client = TwinsTalk_Client(configuration)
    tt_client.run()

    i = 0

    file = open("two-hands_edited.mp4", "rb")
    data = file.read()

    print("send time: ", time.time())
    tt_client.pub.data_writer('videoName', "two-hands_edited.mp4")
    tt_client.pub.data_writer('videoData', data)
    print("end, len of file", len(data))

    while True:
        tt_client.sub.updata_data()
        skeleton = tt_client.sub.read_topic('annotation')
        if skeleton is not None:
            print(skeleton)
            print("receive time: ", time.time())
            break

    tt_client.sub.terminate()
    tt_client.pub.terminate()

if __name__ == '__main__':
    main()