from UPDRS.grasp_cal import render_video
from twinstalk_api.twinstalk_client import TwinsTalk_Client
import json
import time


def main():
    with open("test_config.json") as f:
        configuration = json.load(f)

    tt_client = TwinsTalk_Client(configuration, is_streaming=True, interval=40)
    tt_client.run()

    i = 0

    file = open("two-hands_edited.mp4", "rb")
    data = file.read()

    tt_client.pub.data_writer('videoName', "two-hands_edited.mp4")
    tt_client.pub.data_writer('videoData', data)
    video_data_start = time.time()
    print("end, len of file", len(data))

    while True:
        tt_client.sub.updata_data()
        grasp_result = tt_client.sub.read_topic('graspResult')
        rendered_video = tt_client.sub.read_topic('renderedVideo')

        if grasp_result is not None:
            print("video_name RTT: ", time.time()-video_data_start)
            print(grasp_result.data)
        
        if rendered_video is not None:
            print("video_data RTT", time.time()-video_data_start)
            with open("client_result.mp4", "wb") as f:
                f.write(rendered_video.data)

    tt_client.sub.terminate()
    tt_client.pub.terminate()

if __name__ == '__main__':
    main()