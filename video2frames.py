#
# Copyright (C) 2014 Grigorios G. Chrysos
# available under the terms of the Apache License, Version 2.0


type_v = 'mp4'


# mkdir -p in python from http://stackoverflow.com/a/11860637/1716869
import os, sys
import errno

def mkdir_p(path):
    """ 'mkdir -p' in Python """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


import subprocess
import shutil
import re,string
def clip_to_frames(clip_name, path_video, path_fr_0):
    """
    Accepts a clip file and converts it into individual frames by calling avconv. 
    It might rename the original file if it contains whitespaces (just removes thems).
    """
    print clip_name
    if clip_name[-3:]!= type_v:
        print('Ignoring file ' + clip_name); return  
    #_name = clip_name; name = _name.replace(' ','')           # replace all empty spaces in the original file
    pattern = re.compile('[^a-zA-Z0-9.]+')
    name = pattern.sub('', clip_name) # strip all white spaces, quatation points, etc.
    shutil.move(path_video + clip_name, path_video + name)
    path_frames = path_fr_0 + name[:-4] + '/'; mkdir_p(path_frames)
    p = subprocess.check_output(['avconv -i ' +  path_video + name + ' -f image2 ' + 
                             path_frames + '%06d.png'], shell=True)  


def main(path_base, video_f='mp4/', frames='frames/'):
    """
    Convert different clips (videos) to frames. This function calls the clip_to frames for each clip it finds.
    :param path_base:       The base directory where both the video files should be and the frames that will be written.
    :param video_f:         (optional) Folder with relative address to the path_base, where the videos are.
    :param frames:          (optional) Folder that will be created and will contain the created frames.
    :return:
    """
    path_video = path_base + video_f + '/'
    path_v_fr = path_base + frames + '/'; mkdir_p(path_v_fr)
    list_clips = sorted(os.listdir(path_video)); print list_clips
    try: 
        from joblib import Parallel, delayed
        Parallel(n_jobs=-1, verbose=4)(delayed(clip_to_frames)(clip_name, path_video, path_v_fr) for clip_name in list_clips);
    except: 
        print('Sequential execution')
        [clip_to_frames(clip_name, path_video, path_v_fr) for clip_name in list_clips] 


# call from terminal with full argument list:
if __name__ == '__main__':
    args = len(sys.argv)
    if args < 4:
        raise Exception('You should provide the base directory, the folder of'
                        'the clips and the folder that you wish the frames to be saved ')
    main(str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3]))


