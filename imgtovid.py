#! /usr/bin/env python
import os
from os import path
import subprocess


# http://stackoverflow.com/a/377028/2691632
def exists(program):
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)

    if fpath:
        if is_exe(program):
            return True
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return True

    return False


def create_video(input_dir, n_zeros, output_fname,
                 output_dir=None, image_type='png', fps=30,
                 overwrite=True, verbose=False):
    file_pattern = '%0{}d.{}'.format(n_zeros, image_type)
    input_pattern = path.join(input_dir, file_pattern)
    if output_dir is None:
        output_dir = input_dir
    output = path.join(output_dir, output_fname + '.mp4')

    if not overwrite and path.isfile(output):
        # user doesn't want to overwrite and the file is already there
        print ('    {} already exists and overwrite is False - '
               'skipping').format(output)
        return

    if verbose:
        vb_cmd = 'info'
    else:
        vb_cmd = 'quiet'

    if exists('avconv'):
        cmd = ['avconv', '-y', '-v', vb_cmd, '-r', str(fps),
               '-i', input_pattern,
               '-b:v', '1000k',
               output]
    elif exists('ffmpeg'):
        cmd = ['ffmpeg', '-y', '-v', vb_cmd, '-r', str(fps),
               '-i', input_pattern,
               output]
    else:
        raise Exception("avconv or ffmpeg are required to use this utility")
    print '    {} -> {}'.format(input_dir, output)
    return subprocess.call(cmd)


extensions = {'png', 'jpg', 'gif', 'jpeg'}
from os.path import splitext
def find_image_type(dirname, fname):
    try:
        image_type = splitext(fname)[-1][1:] # Assumption that the first element is an image.
    except IOError:
        print('Probably the first element in the folder is not an image, which is required')
        raise
    if image_type in extensions:
        return image_type
    else:
        import imghdr
        try:
            type1 = imghdr.what(dirname + '/' + fname)
        except IOError:
            raise IOError('The file %s does not exist.\n' % (dirname + '/' + fname))
        if type1 in extensions:
            return type1
        else:
            raise Exception('Not supported type (extension) of image')


def search_for_images(output_dir, dirname, fnames):
    image_type = find_image_type(dirname, fnames[0])
    images = [s for s in fnames if s.endswith('.' + image_type)]
    if len(images) != 0:
        root, containing = path.split(dirname)
        image_names = [path.splitext(i)[0] for i in images]
        list_im = sorted([int(x) for x in image_names])
        image_numbers = set(list_im)
        expected = set(range(list_im[0], len(images) + list_im[0]))
        if image_numbers == expected:
            n_zeros = len(image_names[0])
            print ('{} has contiguous {} files'
                   ' in range 0-{} ({} padded)').format(
                dirname, image_type, len(images) - 1, n_zeros)
            create_video(dirname, n_zeros, containing,
                         output_dir=output_dir, image_type=image_type)
        else:
            print('Did not find the expected arithmetic sequence of images. '
			    'Potentially missing some images from the sequence')


def imgtovid(input_dir, output_dir=None):
    if output_dir is None:
        output_dir = path.join(input_dir, 'imgtovid')
    if not path.isdir(output_dir):
        os.makedirs(output_dir)
    path.walk(input_dir, search_for_images, output_dir)


def main(args):
    print args
    imgtovid(args.dir, output_dir=args.output)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description=r"""
        Recursively search for folders of sequential images and generate
        videos from them. Videos will be named after the containing directory
        structure - e.g.

            dir/foo/bar/001.jpg  -> output/foo_bar.mp4

	    Should be called like this:
		python imgtovid.py /dir/my_images -o /dir_output/ 
	    if the images are in the folder my_images.

        Note that this does lead to degenerate cases if you use underscore
        folder names. Currently only supports jpg images but trivial to add
        support for more in the future.
        """)
    parser.add_argument("dir", help="the directory that should be recursively "
                                    "searched")
    parser.add_argument("-o", "--output",
                        help="The folder which should be outputted to. If "
                             "none is provided, set to dir/imgtovid")
    main(parser.parse_args())
