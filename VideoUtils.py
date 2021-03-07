import cv2
import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def processVideo( input_fpath, output_fpath, label):

    # input_video
    input_video = cv2.VideoCapture(input_fpath)
    frames_per_second = int(input_video.get(cv2.CAP_PROP_FPS))
    frame_width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # output_video
    codec = cv2.VideoWriter.fourcc(*'mp4v')
    output_video = cv2.VideoWriter(output_fpath,
                                   codec,
                                   frames_per_second,
                                   (frame_width, frame_height))
    no_of_frames = 10000
    count = 1
    while count <= no_of_frames:
        # Read the video to retrieve individual frames. 'frame' will reference individual frames read from the video.
        ret, frame = input_video.read()
        # Check the 'ret' (return value) to see if we have read all the frames in the video to exit the loop
        if not ret:
            print('Processed all frames')
            break

        # Convert the image (frame) to RGB format as by default Open CV uses BGR format.
        # This conversion is done as face_recognition and other libraries usually use RGB format.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # describe the type of font 
        # to be used. 
        font = cv2.FONT_HERSHEY_SIMPLEX 
    
        # Use putText() method for 
        # inserting text on video 
        cv2.putText(frame,  
                    label,  
                    (50, 50),  
                    font, 1,  
                    (0, 255, 255),  
                    2,  
                    cv2.LINE_4) 

        # draw rectangle, draw face landmarks , write text, ...
        # cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Write the frame to the output video
        output_video.write(frame)

        # Print for every second of video processed
        if (count - 1) % frames_per_second == 0:
            print('Processed', (count - 1) // frames_per_second, 'seconds of video')

        # update counter for number of frames processed
        count += 1
        if count>600: break

    # Release to close all the resources that we have opened for reading and writing video
    input_video.release()
    output_video.release()
    cv2.destroyAllWindows()


    # Some useful functions for plotting in OpenCV
    import random

    # plot object detection box
    def plot_one_box(x, img, color=None, label=None, line_thickness=None):
        # x - object detection box: left, top, right, bottom
        # Plots one bounding box on image img
        tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
        color = color or [random.randint(0, 255) for _ in range(3)]
        c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3])) #(left, top), (right, bottom)
        cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        if label:
            tf = max(tl - 1, 1)  # font thickness
            t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

    # put text bellow the object detection box
    def put_text_bellow_rectangle(frame, text, left, right, bottom, color):
        font = cv2.FONT_HERSHEY_DUPLEX  # font
        cv2.rectangle(frame, (left, bottom + 25), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, text, (left + 5, bottom + 15), font, 0.5, (255, 255, 255), 1)

    # Draw lines for e.g. face landmarks
    # cv2.polylines(frame, [points], True, (255, 0, 0))

#processVideo( input_fpath, output_fpath)