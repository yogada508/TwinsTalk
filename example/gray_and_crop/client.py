import sys
sys.path.append("../..")

from twinstalk_api.twinstalk_client import TwinsTalk_Client
import json
import time


def main():
    with open("gray_and_crop.json") as f:
        configuration = json.load(f)

    tt_client = TwinsTalk_Client(configuration)
    tt_client.run()

    i = 0

    file = open("input_video.mp4", "rb")
    data = file.read()

    print("send time: ", time.time())
    tt_client.pub.data_writer('videoName', "input_video.mp4")
    tt_client.pub.data_writer('videoData', data)
    print("end, len of file", len(data))

    output_file = "cropped_video.mp4"

    while True:
        tt_client.sub.updata_data()
        proto = tt_client.sub.read_topic('croppedVideo')
        if proto is not None:
            with open(output_file, "wb") as f:
                f.write(proto.data)
            print("receive time: ", time.time())
            break

    # tt_client.sub.terminate()
    # tt_client.pub.terminate()
    tt_client.terminate()


if __name__ == '__main__':
    main()
