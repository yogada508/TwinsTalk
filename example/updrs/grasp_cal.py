from scipy.signal import savgol_filter
from scipy import signal
import numpy as np
import cv2

def find_peak(record_right, record_left):
    #multiple hand, 0 for right hand and 1 for left hand
    fist_closing_frame = []
    action_time_list = []

    for hand in range(2):
        smooth = []
        label = ""
        if hand == 0:
            smooth = savgol_filter(record_right,9,3)
            label = "right hand"
        else:
            smooth = savgol_filter(record_left,9,3)
            label = "left hand"

        middle = (max(smooth)+min(smooth))/2
        pro = (max(smooth) - middle) * 0.8

        peaks, _ = signal.find_peaks(smooth,height=middle,prominence=pro)

        fist_closing_frame.append(peaks)

        #calculcate fist closing action time
        temp = []
        temp.append(peaks[0])
        for time in np.diff(peaks):
            temp.append(time)
        action_time_list.append(temp)

    return fist_closing_frame, action_time_list

def render_video(video_name, fist_closing_frame, action_time_list, right_lost, left_lost):
    action_count = [0,0]
    action_time = [0,0]
    right_count = -1
    left_count = -1
    temp_count = 0
    img_list = []

    # read video frame
    cap=cv2.VideoCapture(video_name)
    RES = (round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = round(cap.get(cv2.CAP_PROP_FPS))

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            img_list.append(frame)
        else:
            break

    # output video format
    output_video = "./result.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, RES)
    
    # write action count to video
    for i in range(len(img_list)):
        label = ""
        text_loc_x = 0
        if i not in right_lost:
            right_count +=1
        if i not in left_lost:
            left_count += 1
        for hand in range(2):
            if hand == 0:
                label = "right"
                text_loc_x = 100
                temp_count = right_count
            else:
                label = "left"
                text_loc_x = 1250
                temp_count = left_count

            if( (len(fist_closing_frame[hand]) > action_count[hand]) and temp_count == fist_closing_frame[hand][action_count[hand]]):
                action_time[hand] = action_time_list[hand][action_count[hand]]
                action_count[hand] += 1
            cv2.putText(img_list[i],f'action_count({label}):{action_count[hand]}',(text_loc_x, 70), cv2.FONT_HERSHEY_SIMPLEX,1.5, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(img_list[i],f'action_time({label}):{action_time[hand]/fps:.2f}s',(text_loc_x, 120), cv2.FONT_HERSHEY_SIMPLEX,1.5, (0, 0, 0), 3, cv2.LINE_AA)
        out.write(img_list[i])
    out.release()

    right_hand_result = f"right hand action count:{len(fist_closing_frame[0])}, " \
        f"frequency: {len(fist_closing_frame[0])/(len(img_list)/fps):.4f}, "\
        f"regularity: {np.std(np.array(action_time_list[0]))/fps:.4f}\n"
    
    left_hand_result = f"left hand action count:{len(fist_closing_frame[1])}, " \
        f"frequency: {len(fist_closing_frame[1])/(len(img_list)/fps):.4f}, "\
        f"regularity: {np.std(np.array(action_time_list[1]))/fps:.4f}\n"

    # return output video
    video_file = open("./result.mp4", "rb")
    data = video_file.read()

    return data, right_hand_result+left_hand_result