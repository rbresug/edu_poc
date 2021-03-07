"""
Created on Feb 14, 2021

@author: 
"""

import configparser
import time
#import pyaudio
import wave
import json
import logging as log
import datetime

import os
#import moviepy.video.io.ffmpeg_tools
from moviepy.editor import *
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from os.path import expanduser
home_dir = expanduser("~")

import cv2 
from VideoUtils import *

from shutil import *


def processResults( input_file, score_thresh):
    self_input_file = input_file
    self_score_thresh = score_thresh
    self_detections = []
    log.info('Loading {}'.format(input_file))
    with open(input_file) as f:
        all_detections = json.load(f)
    #print(all_detections)
    capturing = False
    output_arr = []
    snapshotStartTs = 0
    snapshotStopTs = 0
    for source_detections in all_detections:
        detections_dict = {}
        entry = (source_detections['events'])
        entry0 = entry[0]
        label_dict = entry0['detection']
        label = label_dict['label']

        tmpSnapshotStopTs = entry0['end_timestamp']
        if capturing == False and label =='Speech':
            snapshotStartTs = entry0['start_timestamp']
            capturing = True
        if capturing == True and label != 'Speech':
            snapshotStopTs = tmpSnapshotStopTs #entry0['start_timestamp']
            capturing = False
            output_arr.append([snapshotStartTs, snapshotStopTs, snapshotStopTs-snapshotStartTs])
    output_arr.sort(key = lambda x: x[2],reverse=True)
    duration_arr = []
    print("There are SPEECH detections at the following seconds timestamps")
    for output_entry in output_arr:
        simple_output_arr = [x / 1000000000 for x in output_entry]
        dur = simple_output_arr[1]- simple_output_arr[0]
        duration_arr.append(dur)
        #print (simple_output_arr)
        h_simple_output_arr = [str(datetime.timedelta(seconds=x)) for x in simple_output_arr]
        print(h_simple_output_arr)
    duration_arr.sort(reverse=True)
    print("Longest sorted timewindow")
    print(duration_arr)
    return output_arr





def videoExtract (listDetections):
    input_fpath = os.path.join( home_dir +"/testFolder/raw_videos/work", "video.mp4" )
    #"path_to_the_input_video_file"
    output_fpath =  os.path.join( home_dir + "/testFolder/raw_videos/work", "summary_video.mp4" )
    output_str_path = home_dir + "/testFolder/raw_videos/work/"
    #"path_to_the_output_video_file"
    cnt = 0
    clips = []
    for output_entry in listDetections:
        cnt = cnt + 1
        simple_output_arr = [x / 1000000000 for x in output_entry]
        dur = simple_output_arr[1]- simple_output_arr[0]
        outvid = output_str_path+str(cnt)+".mp4"
        outVidUnlabeled = output_str_path+str(cnt)+"unlabeled.mp4"
        outVidAudio = output_str_path+str(cnt)+"audio.mp4"
        print("outvid is"+ outvid)
        item = ffmpeg_extract_subclip(input_fpath, simple_output_arr[0], simple_output_arr[1], targetname=outvid)
        
        copyfile(outvid, outVidUnlabeled)
        textOverlay =str(datetime.timedelta(seconds=simple_output_arr[0]))
        processVideo(outVidUnlabeled,outvid,textOverlay)
        ##clip = mp.VideoFileClip(outVidUnlabeled) 
        clipEntry = VideoFileClip(outvid)
        clipWithAudio = VideoFileClip(outVidUnlabeled)
        audio = clipWithAudio.audio
        audio.write_audiofile('orig_background.mp3')
        audioc = AudioFileClip('orig_background.mp3')
        #audio_background = AudioFileClip('orig_background.mp3')
        #audio.write_audiofile(sys.argv[2]
        video_with_new_audio = clipEntry.set_audio(audioc)
        video_with_new_audio.write_videofile(outVidAudio)
        clipEntry = VideoFileClip(outvid)
        #move(outVidAudio, outvid)
        #insertFrame(outvid, textOverlay)
        
        print("after extraction")
        ## txt_clip = TextClip("Detection", fontsize = 70, color = 'white').set_duration(2) 
        ##clips.append(txt_clip)
        clips.append(VideoFileClip(outVidAudio))

        print(item)
        #clips.append(ffmpeg_extract_subclip(input_fpath, simple_output_arr[0], simple_output_arr[1], targetname=outvid))
        if cnt==3:
            break
    outvidTotal = output_str_path +"summary.mp4"
    print(clips)
    #slided_clips = [CompositeVideoClip([clip.fx( transfx.crossfadein, transition_seconds)]) for clip in clips]
    #slided_clips = [CompositeVideoClip([clip]) for clip in clips]
    #added 'method = compose' NEED TO TEST - supposedly removes the weird glitches.
    print("summary creation output_str_path=" +  output_str_path)
    c = concatenate_videoclips(clips, method = 'compose')
    c.write_videofile(outvidTotal,fps=23.98)
    

    ##use cv2 to insert text
    #cap = cv2.VideoCapture(outvidTotal)

def insertFrame(videoTitle, textOverlay):
    cap = cv2.VideoCapture(videoTitle)
    print("this is capturing") 
  
    while(True): 
        
        # Capture frames in the video 
        ret, frame = cap.read()
        print('Process one  frame')
        # Check the 'ret' (return value) to see if we have read all the frames in the video to exit the loop
        if not ret:
            print('Processed all frames')
            break 
    
        # describe the type of font 
        # to be used. 
        font = cv2.FONT_HERSHEY_SIMPLEX 
    
        # Use putText() method for 
        # inserting text on video 
        cv2.putText(frame,  
                    'TEXT ON VIDEO',  
                    (50, 50),  
                    font, 1,  
                    (0, 255, 255),  
                    2,  
                    cv2.LINE_4) 
        # Display the resulting frame 
        cv2.imshow('video', frame) 
    
        # creating 'q' as the quit  
        # button for the video 
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break
    
    
    # release the cap object 
    cap.release() 
    # close all windows 
    cv2.destroyAllWindows() 


def wait_and_grab(self_detections,self_last_index , self_score_thresh ):
    output = []
    for source in self_detections:
        valid_detections = []
        if self_last_index in source:
            for bbox, score in zip(source[self_last_index]['boxes'], source[self_last_index]['scores']):
                if score > self_score_thresh:
                    bbox = [int(value) for value in bbox]
                    valid_detections.append((bbox, score))
        output.append(valid_detections)
    return output

def update_detections(output, detections, frame_number):
    for i, detection in enumerate(detections):
        entry = {'frame_id': frame_number, 'scores': [], 'boxes': []}
        for det in detection:
            entry['boxes'].append(det[0])
            entry['scores'].append(float(det[1]))
        output[i].append(entry)



def get_elapsed_time(time_before):
    """
    Initializing a new Modem instance and wait for network coverage

    Args:
        time_before (float): the previous time instance for calculation

    Returns:
        float: Return the time difference between input time and the current time
    """
    time_after = time.time()
    time_difference = time_after - time_before
    return time_difference





if __name__ == '__main__':

    detections = "input.json"
    detections_list = processResults(detections, 2)
    #txt_clip = TextClip("Detection", fontsize = 70, color = 'white').set_duration(2)
    #txt_clip = TextClip("Detection", fontsize = 70, color = 'black')
    videoExtract(detections_list)


