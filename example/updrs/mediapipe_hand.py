import numpy as np
import cv2
import os
import mediapipe as mp

def hand_detection(video_name):
    if(not os.path.isfile(video_name)):
        print("The input video doesn't exist!")
        return

    # Read video with OpenCV.
    cap=cv2.VideoCapture(video_name)

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    #movement of two hands
    hands = mp_hands.Hands(static_image_mode=True,max_num_hands=2,min_detection_confidence=0.5)

    record_left = []
    record_right =[]
    img_lost = []
    right_lost=[]
    left_lost = []
    frame_count = 0
    img_list = []
    results = 0
    while(cap.isOpened()):
        ret, frame = cap.read()

        if ret == True:
            # Convert the BGR image to RGB, flip the image around y-axis for correct 
            # handedness output and process it with MediaPipe Hands.
            results = hands.process(cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 1))

            annotated_image = frame.copy()

            if results.multi_hand_landmarks != None:
                annotated_image = cv2.flip(frame.copy(), 1)
                right_hand = None
                left_hand = None

                if (len(results.multi_hand_landmarks) == 1 and results.multi_handedness[0].classification[0].label == "Left"):
                    right_hand = results.multi_hand_landmarks[0]
                    left_lost.append(frame_count)
                elif (len(results.multi_hand_landmarks) == 1 and results.multi_handedness[0].classification[0].label == "Right"):
                    left_hand = results.multi_hand_landmarks[0]
                    right_lost.append(frame_count)
                
                elif (len(results.multi_hand_landmarks) == 2):
                    hand0 = results.multi_hand_landmarks[0]
                    hand1 = results.multi_hand_landmarks[1]
                    #two same hands
                    if(results.multi_handedness[0].classification[0].label == results.multi_handedness[1].classification[0].label):
                        hand0_x = hand0.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x
                        hand1_x = hand1.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x

                        left_hand = hand0 if hand0_x > hand1_x else hand1
                        right_hand = hand1 if hand0_x > hand1_x else hand0

                    else:
                        right_hand = hand0 if results.multi_handedness[0].classification[0].label == "Left" else hand1
                        left_hand = hand0 if results.multi_handedness[0].classification[0].label == "Right" else hand1
                
                if(right_hand != None):
                    mp_drawing.draw_landmarks(annotated_image, right_hand, mp_hands.HAND_CONNECTIONS)
                    record_right.append(right_hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y)
                    #print(frame_count,"right", right_hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x)
                if(left_hand != None):
                    mp_drawing.draw_landmarks(annotated_image, left_hand, mp_hands.HAND_CONNECTIONS)
                    record_left.append(left_hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y)
                    #print(frame_count,"left", left_hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x)

                #after processing the hand, flip back the image  
                annotated_image = cv2.flip(annotated_image, 1)
            else:
                img_lost.append(frame_count)

            img_list.append(annotated_image)
            frame_count += 1
            print(frame_count)

        else:
            break

    cap.release()
    return img_list,record_right,record_left,right_lost,left_lost,img_lost