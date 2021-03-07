import requests
import pandas as pd
import os
import sys
from os.path import expanduser
home = expanduser("~")

project_dir = os.path.join(home, 'testFolder')
output_dir = os.path.join(project_dir, 'raw_videos')

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)


# total arguments
n = len(sys.argv)
print("Total arguments passed:", n)
 
# Arguments passed
print("\nName of  script:", sys.argv[0])
 
print("\nArguments passed:", end = " ")
for i in range(1, n):
    print(sys.argv[i], end = " ")
     
# Addition of numbers
rows_toskip = int(sys.argv[1])

 
#metadf=pd.read_csv(os.path.join(project_dir, 'download_links_for_intel.csv'), encoding = "ISO-8859-1")
fields = ['entryid','name','parentDownloadUrl','childDownloadUrl']
#metadf=pd.read_csv(os.path.join(project_dir, 'download_links_for_intel.csv'))

metadf=pd.read_csv(os.path.join(project_dir, 'download_links_for_intel.csv'),header=0, usecols=fields, skiprows=range(1, rows_toskip), nrows=5)
print(metadf)

metadf = metadf[metadf['name'].notnull()]
metadf = metadf[metadf['childDownloadUrl'].notnull()]
print("keys are ")
print(metadf.keys())
print(metadf)
url_list= metadf['childDownloadUrl']#metadf.childDownloadUrl#['childDownloadUrl']
print(url_list)
#.to_list()


error_log=''

for i,url in enumerate(url_list):
    try:
        r = requests.get(url, allow_redirects=True)
        nameInfo = metadf['name'].iloc[i]
        nameInfoFiltered = nameInfo.replace("/", "")
        fpath = os.path.join(output_dir, nameInfoFiltered+str(metadf['entryid'].iloc[i])+'.mp4')
        #print(i, url)
        print(fpath)
        fpathNoSpace = fpath.replace(" ", "")
        open(fpathNoSpace, 'wb').write(r.content)
        
    except Exception as e:
        error_log+=metadf['entryid'].iloc[i]+":"+e+"\n"

with open(os.path.join(output_dir,'error_log'),'w') as f:
    f.write(error_log)


