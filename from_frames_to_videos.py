# coding: utf-8

# grigoris, 17/12/2014: v.1.1: Performs the copying, call to imgtovid per clip.  
# grigoris, 9/12/2014: Convert different clips in the subfolders to a video, using the imgtovid.
# Support for case of non-sequential naming of frames as well.
#
#
# Copyright (C) 2014 Grigorios G. Chrysos
# available under the terms of the Apache License, Version 2.0

# mkdir -p in python from http://stackoverflow.com/a/11860637/1716869
import os, shutil
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
            

def rm_if_exists(path):
    try: 
        shutil.rmtree(path)
    except OSError: 
        pass


# temporarily suppress output from videos # http://thesmithfam.org/blog/2012/10/25/temporarily-suppress-console-output-in-python/
from contextlib import contextmanager
import sys, os

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout


import imgtovid

def call_imgtovid(path_clip, path_videos):
# Calls the imgtovid function to convert one clip's frames to video
    try:
        imgtovid.imgtovid(path_clip, path_videos)
    except IOError:
        print('Ignoring exception in ' + path_clip)


def clip_frames_to_videos(path_of_clips, vid_fold='1_videos', nam='renamed', suppress_print='True'):
    if not(os.path.isdir(path_of_clips)): 
        print('Wrong original path provided, seems non-existent'); return
    list_clips_0 = sorted(os.listdir(path_of_clips))
    list_clips = [x for x in list_clips_0 if x not in [nam, vid_fold]]
    path_of_clips_new = path_of_clips + nam + '/'; mkdir_p(path_of_clips_new);
    path_videos = path_of_clips_new + vid_fold + '/';  mkdir_p(path_videos);
    try:									# try to do the call the imgtovid for every clip in parallel
        from joblib import Parallel, delayed
        Parallel(n_jobs=-1, verbose=4)(delayed(process_clip)(clip, path_of_clips, path_videos, nam, suppress_print) 
                                       for clip in list_clips if not(clip == vid_fold))
    except:
	print('Sequential execution')
        for clip in list_clips:
            if clip == vid_fold: continue; 
            process_clip(clip, path_of_clips, path_videos, nam, suppress_print)


def process_clip(clip, path_of_clips, path_videos, nam='renamed', suppress_print='True'):
    print('Preparing video for %s clip' % clip)
    copy_folder_and_rename_frames(clip, path_of_clips, path_of_clips + nam + '/')
    path_clip = path_of_clips + nam + '/' + clip
    if suppress_print=='True':
        with suppress_stdout():
            call_imgtovid(path_clip, path_videos)
    else:
        call_imgtovid(path_clip, path_videos)


# grigoris, 4/12/2014: Two functions that are used to write frames in a video using imgtovid. 
# They should be used in case the frames are not sequential. Then it copies the clips and 
# re-writes them in a sequential matter. 
# Assumption: In the original folder, the first object (in alphabetical order) should be an image.  

def rename_frames(d):
    # The function renames the frames in the 'd' folder and re-writes them sequentially. 
    list_d = sorted(os.listdir(d))
    image_type = imgtovid.find_image_type(d, list_d[0])           # will raise an error if it's not an image
    ext = '.' + image_type
    padd = '%.' + str(len(os.path.splitext(list_d[0])[0])) + 'd'  # checks the format and writes with the same padding
    for i, fr in enumerate(list_d):
        n = os.path.splitext(fr)[0]
        os.rename(d + fr, d + padd %i + ext)                    

import glob 
import warnings
def copy_folder_and_rename_frames(folder, dir_1, dir_2, min_images=2):
    _tmp_dir = dir_1 + folder
    if not(os.path.isdir(_tmp_dir)):
        warnings.warn('The path %s/ is empty\n'%_tmp_dir)
        return
    files = sorted(os.listdir(_tmp_dir))
    #if len(files) < 150: print('The folder has too few files(' + str(len(files)) + '), skipped');return;                              # TODO: dirty hack, should be fixed to check for images
    if len(files) == 0:
        warnings.warn('There are no files in the %s/ dir\n'%_tmp_dir)
        return
    image_type = imgtovid.find_image_type(_tmp_dir, files[0])
    images = glob.glob(_tmp_dir + '/*.' + image_type)
    if len(images) < min_images:
        print('The folder %s/ has too few files('%_tmp_dir + str(len(images)) + '), skipped');
        return
    print len(images)
    fold_2 = dir_2 + folder
    rm_if_exists(fold_2)
    shutil.copytree(_tmp_dir, fold_2)
    rename_frames(fold_2 + '/')

# def copy_and_rename_frames(dir_1, nam = 'renamed'):
#     # For each subfolder that contains frames (images), copies them in the 'nam' directory
#     # and then renames them, in order to call imgtovid to produce a video. 
#     dir_2 = dir_1 + nam + '/'
#     mkdir_p(dir_2)
#     try:                      # try to do it in parallel
#         from joblib import Parallel, delayed
#         Parallel(n_jobs=-1, verbose=4)(delayed(copy_folder_and_rename_frames)(folder, dir_1, dir_2) 
#                                        for folder  in sorted(os.listdir(dir_1)))
#     except:
#         for folder  in sorted(os.listdir(dir_1)):
#             copy_folder_and_rename_frames(folder, dir_1, dir_2)

        
def move_to_orig_folder(dir_1, vid_fold, nam):
    rm_if_exists(dir_1 + vid_fold + '/'); 
    shutil.move(dir_1 + nam + '/' + vid_fold + '/', dir_1)
    rm_if_exists(dir_1 + nam + '/'); 


def main(dir_1, nam='renamed', vid_fold = '1_videos', suppress_print='True'):
# Main function that does all the actions. 
# ARGS:
#   dir_1:            The folder with the subfolders. Each subfolder should contains frames of a clip. 
#   nam (optional):   The new temp folder for writing the frames sequentially.
#   vid_fold (opt):   The final folder, where all the videos will be.
#     copy_and_rename_frames(dir_1, nam = nam)
    clip_frames_to_videos(dir_1, vid_fold=vid_fold, nam=nam, suppress_print=suppress_print)
    move_to_orig_folder(dir_1, vid_fold, nam)


# call from terminal with full argument list:
if __name__ == '__main__':
    args = len(sys.argv)
    if args < 2:
        print('You should provide the directory of the clips')
        raise Exception()
    elif args < 3:
        nam = 'renamed'; vid_fold = '1_videos'
    elif args < 4:
        nam = str(sys.argv[2]); vid_fold = '1_videos'
    else:
        nam = str(sys.argv[2]); vid_fold = str(sys.argv[3])
    main(str(sys.argv[1]), nam, vid_fold)



