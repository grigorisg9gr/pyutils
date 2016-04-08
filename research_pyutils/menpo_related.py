from os.path import join, isdir, isfile
import menpo.io as mio



def from_ln_to_bb_path(shapes=None, p_in=None, p_out=None, overwrite=None):
    """
    Converts the list of landmarks to the respective tightest bounding boxes.
    Calls the menpo convenience method of bounding_box() for the landmarks.
    
    Can be provided either the shapes directly or an import path.
    If an exporting path is provided, the bounding boxes will be 
    exported there.
        
    """
    if p_out is not None:
        assert(isdir(p_out))

    if shapes is None:
        # import the shapes
        assert(isdir(p_in))
        shapes = list(mio.import_landmark_files(p_in))

    bbs = []
    # dummy image
    im = mio.import_builtin_asset.lenna_png()
    # loop over the shapes to convert to bounding boxes.
    for ln in shapes:
        # get the bounding box
        im.landmarks['g'] = ln.lms.bounding_box()
        if p_out is not None:
            # if path is provided, export it.
            mio.export_landmark_file(im.landmarks['g'], p_out + ln.path.name, 
                                     overwrite=overwrite)
        bbs.append(im.landmarks['g'])
        
    return bbs


