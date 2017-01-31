# expose the most frequently used functions in the top level.
from .path_related import (mkdir_p, rm_if_exists, remove_empty_paths,
                           copy_contents_of_folder, count_files, 
                           copy_the_previous_if_missing)

try:
    from .menpo_related import (resize_all_images, from_ln_to_bb_path,
                                process_lns_path, compute_overlap,
                                rasterize_all_lns)
except ImportError:
    m1 = ('The menpo related utils are not imported. If '
          'you intended to use them please check your '
          'menpo installation.')
    print(m1)

from .filenames_changes import (rename_files, change_suffix,
                                strip_filenames)

from .auxiliary import (execution_stats, compare_python_types,
                        whoami, populate_visual_options)


