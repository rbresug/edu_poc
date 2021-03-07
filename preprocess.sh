#!/bin/bash


cd ~/testFolder
echo  "script after testFolder"
#python3 downloaderLIL.py
echo  "script waiting.."
#sleep 60
echo  "script download ready.."


cat download_links_for_intel.csv  | wc -l
num_of_lines=$(wc -l download_links_for_intel.csv)
echo "lines ${num_of_lines}" 
countercvs=0
for i in {5..3600..5}; do
    cd ~/testFolder
    echo  "script after testFolder"
    python3 downloaderLIL.py "${i}" 
    echo  "script waiting.."
    #sleep 60
    echo  "script download ready.."
    cd ~/testFolder/raw_videos/
    export hostTargetFiles="$(pwd)"

    cnt=0
    #hostTargetFiles = $(pwd)
    if [ ! -z "$hostTargetFiles" ]; then
        for localFile in "$hostTargetFiles"/*.mp4; do
            if [ ! -d "$localFile" ]; then
                ##sandbox start
                echo  "sandbox start"
                echo "~/testFolder/raw_videos/${localFile##*/}" 
                #rm "${HOME}/testFolder/raw_videos/${localFile##*/}_p192.wav"
                echo  "sandbox end"
                #break
                ##sandbox end
                cd ~/testFolder/raw_videos/
                cnt=$((cnt+1))
                echo  "each file"
                echo "${localFile##*/}"
                curfile=$(basename $localFile)
                echo  "before $curfile"
                curfilefirst5=${curfile:0:5}
                echo  "after testFolder2"
                #ffmpeg -i localFile $(sound +"%cnt_").wav
                ffmpeg -i "${localFile##*/}" "${localFile%.mp3}_p192.wav"
                #prepare for later step
                cp "${localFile##*/}" work/video.mp4
                /opt/intel/openvino_2021/data_processing/dl_streamer/samples/gst_launch/audio_detect/audio_event_detection.sh\
                "${localFile%.mp3}_p192.wav" > "${localFile%.mp3}_p192.txt"
                echo  "script after inference"
                cd ~/testFolder/
                inputTxt="${localFile%.mp3}_p192.txt"
                echo $PWD
                echo scriptcheck
                cat $inputTxt | grep confidence > input.json
                echo scriptcheck
                sleep 1
                sed -e 's/$/,/' -i input.json #add one comma for each line
                sleep 1
                sed  '$ s/.$/]/' -i input.json #remove last line comma
                sed -i '1s/^/[ /' input.json
                cd ~/testFolder/
                pythonOut=$(date +"%Y_%m_%d_%I_%M_%p").log
                #mkdir "dir${localFile##*/}"
                python3 TestJsonLoad.py > $pythonOut
                #sed -i '1 i\anything' $pythonOut
                #echo "${localFile##*/}"  | cat - $pythonOut
                cd ~/testFolder/raw_videos
                echo scriptCreatedir
                mkdir -p "dir_${localFile##*/}"
                cp work/summary.mp4 "dir_${localFile##*/}/summary.mp4"
                cp "../$pythonOut" "dir_${localFile##*/}/transcript.txt"
                rm -f ../input.json
                #cleanup
                rm  "${HOME}/testFolder/raw_videos/${localFile##*/}"
                rm  "${HOME}/testFolder/raw_videos/${localFile##*/}_p192.wav"
            fi
        done
    fi
done



