pyutils
=======

A collection of useful Python tools for my research.
[travis]: https://travis-ci.org/grigorisg9gr/pyutils
[license]: https://github.com/grigorisg9gr/pyutils/blob/master/LICENSE

#### **Files**
Specifically, the files are classified as following:
* auxiliary: General purpose tools not fitting into any of the other categories.
* filenames_changes: Functions related to specific file-names in a path. For the time being these modify the content of those folders.
* menpo_related: Convenience functions related to [menpo](http://menpo.org/).
* path_related: Convenience functions related to path modifications, e.g. creating/deleting a path.

#### **Installation**
To install those tools, you can:
* clone this repository with ``` git clone https://github.com/grigorisg9gr/pyutils.git```.
* Pip install it with ```pip install --no-deps -e [path_you_cloned_it]```. This editable mode means that every time you modify the source files the content of the actual functions will be modified accordingly. Also, the no-deps arg means that the packages required should exist to run the functions, e.g. numpy or os for most files.

#### **Feedback**
If you do have any questions or improvements, feel free to open issues here or contribute right away. Feedback is always appreciated.

