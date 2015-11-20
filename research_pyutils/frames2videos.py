# Copyright (C) 2014 Grigorios G. Chrysos
# available under the terms of the Apache License, Version 2.0

from path_related_functions import (is_path, rename_files, sep, mkdir_p)
import glob
import warnings
import sys
import os
import imgtovid
from auxiliary import suppress_stdout


def call_imgtovid(path_clip, path_videos):
    # Calls the imgtovid function to convert one clip's frames to video.
    try:
        imgtovid.imgtovid(path_clip, path_videos)
    except IOError:
        print('Ignoring exception in {}.'.format(path_clip))


def process_clip(clip, path_of_clips, path_videos, suppress_print=True, min_images=2):
    print('Preparing video for {} clip.'.format(clip))
    # check_and_rename_frames(clip, path_of_clips)
    path_clip = path_of_clips + clip
    if not is_path(path_clip):
        return
    files = sorted(os.listdir(path_clip))
    if len(files) == 0:
        warnings.warn('There are no files in the {} dir.\n'.format(path_clip))
        return
    image_type = imgtovid.find_image_type(path_clip + sep, files[0])
    images = glob.glob(path_clip + sep + '*.' + image_type)
    if len(images) < min_images:
        print('The folder {} has too few files({}), skipped.'.format(path_clip, str(len(images))))
        return
    rename_files(path_clip, image_type)
    if suppress_print:
        with suppress_stdout():
            call_imgtovid(path_clip, path_videos)
    else:
        call_imgtovid(path_clip, path_videos)


def main(clip_parent_path, vid_fold='1_videos', suppress_print=True):
    """
    Convert all frames in the respective sub-folders into videos.
    For each sub-folder:
        a) it renames the frames into sequential order inplace.
        b) it calls imgtovid.py.

    ASSUMPTION: In the original folder, the first object (in alphabetical order) should be an image.
    :param clip_parent_path: The folder with the sub-folders. Each sub-folder should contains frames of a clip.
    :param vid_fold:        (optional) The final folder, where all the videos will be saved.
    :param suppress_print:  (optional) Suppress the output to the terminal from imgtovid.
    :return:
    """
    if not is_path(clip_parent_path):
        return
    list_clips_0 = sorted(os.listdir(clip_parent_path))
    list_clips = [x for x in list_clips_0 if x not in [vid_fold]]
    p_vid = mkdir_p(clip_parent_path + vid_fold + sep)
    try:									# try to call the imgtovid for every clip in parallel
        from joblib import Parallel, delayed
        Parallel(n_jobs=-1, verbose=4)(delayed(process_clip)(clip, clip_parent_path, p_vid, suppress_print)
                                       for clip in list_clips if not(clip == vid_fold))
    except ImportError:
        print('Joblib library probably does not exist, proceeding with sequential execution.')
        t = [process_clip(clip, clip_parent_path, p_vid, suppress_print)
             for clip in list_clips if not(clip == vid_fold)]


# call from terminal with full argument list:
if __name__ == '__main__':
    args = len(sys.argv)
    if args < 2:
        print('You should provide the directory of the clips')
        raise Exception()
    elif args < 3:
        vid_fold1 = '1_videos'
    elif args < 4:
        vid_fold1 = '1_videos'
    else:
        vid_fold1 = str(sys.argv[3])
    main(str(sys.argv[1]), vid_fold1)



