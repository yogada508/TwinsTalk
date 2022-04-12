from twinstalk_client import TwinsTalk_Client
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
    tt_client.pub.data_writer('video_name', "two-hands_edited.mp4")
    tt_client.pub.data_writer('video_data', data)
    print("end, len of file", len(data))

    while True:
        tt_client.sub.updata_data()
        skeleton = tt_client.sub.read_topic('annotation')
        if skeleton is not None:
            print(skeleton)
            print("receive time: ", time.time())
            break

    # while True:
    #     print(f'(str)data:{str(i)}, send time: {time.time()}')
    #     tt_client.pub.data_writer("video_name", str(i))

    #     i += 1
    #     time.sleep(2)


if __name__ == '__main__':
    main()
