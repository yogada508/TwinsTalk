import sys
sys.path.append("../..")

from twinstalk_api.twinstalk_client import TwinsTalk_Client
import json
import time

def main():
    with open("object_detection.json") as f:
        configuration = json.load(f)

    tt_client = TwinsTalk_Client(configuration, is_streaming=True, interval=60)
    tt_client.run()

    file = open("image1.jpg", "rb")
    data = file.read()

    tt_client.pub.data_writer('imageName', "image1.jpg")
    tt_client.pub.data_writer('imageData', data)
    image_data_start = time.time()
    print("end, len of file", len(data))

    while True:
        tt_client.sub.updata_data()
        result_image = tt_client.sub.read_topic('resultImage')
        
        if result_image is not None:
            print("image_data RTT", time.time()-image_data_start)
            with open("./result.jpg", "wb") as f:
                f.write(result_image.data)

    tt_client.sub.terminate()
    tt_client.pub.terminate()

if __name__ == '__main__':
    main()