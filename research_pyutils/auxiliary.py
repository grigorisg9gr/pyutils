import os
import sys
import inspect
import numpy as np
import time
import socket


def whoami():
    """
    Name of a function returned as a string.
    """
    return inspect.stack()[1][3]


def whosparent():
    """
    Name of the caller of a function.
    """
    # http://stefaanlippens.net/python_inspect
    return inspect.stack()[2][3]


# temporarily suppress output: http://thesmithfam.org/blog/2012/10/25/temporarily-suppress-console-output-in-python/
from contextlib import contextmanager

@contextmanager
def suppress_stdout():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def compare_python_types(elem1, elem2, msg='', per_elem_numpy=False):
    """
    Compares two python objects (of fundamental types) and returns if they are equal.
    If they are not, it returns a message of how 'deep' it went till they were not equal.
    The way that it works is that it checks if elem1 and elem2 have the same type(). If yes,
    then it iteratively/recursively checks their sub-elements.
    :param elem1:       First element/object.
    :param elem2:       Second element/object.
    :param msg:         (optional) String to be passed in the recursive loop
    :param per_elem_numpy: (optional) (bool) If the numpy values (if included in the elements)
    are small floats (e.g. < 0.001) there might be a case that the numpy equality array might
    return False for some values with difference < 10**(-15). In such a case, if this bool is
    True, there will be a search if they are close enough.
    :return:
    """

    t1 = type(elem1)
    t2 = type(elem2)
    if t1 != t2:
        s = 'Different data types ({} vs {}). \'Path\': {}'.format(t1, t2, msg)
        return False, s
    if t1 == int or t1 == float or t1 == str or t1 == bool:
        return elem1 == elem2, msg
    elif t1 == list:
        if len(elem1) != len(elem2):
            s = 'Different number of elements in the list. \'Path\': {}'.format(msg)
            return False, s
        for cnt, el in enumerate(elem1):
            res, s = compare_python_types(el, elem2[cnt], msg=msg + 'list -> ' + str(cnt) + ' ')
            if not res:
                s = 'Different values in element {}.\'Path\': {}'.format(cnt, s)
                return False, s
        return True, msg
    elif t1 == dict:
        if len(elem1.keys()) != len(elem2.keys()):
            s = 'Different number of keys. \'Path\': {}'.format(msg)
            return False, s
        for k, v in elem1.iteritems():
            try:
                v2 = elem2[k]
            except KeyError:
                s = 'The key {} does not exist in the second item.\'Path\': {}'.format(k, msg)
                return False, s
            res, s = compare_python_types(v, v2, msg=msg + 'dict -> (key): ' + str(k) + ' ')
            if not res:
                s = 'Different values in element {}.\'Path\': {}'.format(k, s)
                return False, s
        return True, msg
    elif isinstance(elem1, np.ndarray):
        ret = np.array_equal(elem1, elem2)
        if not ret:
            if per_elem_numpy:
                ret2 = np.allclose(elem1, elem2, atol=10**(-15))
                if ret2:
                    return True, msg
            return False, msg + 'Not equal in the numpy arrays.'
        return True, msg
    elif 'numpy' in str(type(elem1)):  # e.g. numpy.float64
        return elem1 == elem2, msg
    else:  # other types of data not supported
        raise RuntimeError(t1)


def execution_stats(return_vars=True, verbose=True):
    """
    Prints some statistics, e.g. name of the machine, time of execution.
    :param return_vars: (bool, optional) If True, return the time and machine
           name to the calling function/script.
    :param verbose:  (bool, optional) If True, print time, machine name.
    :return:
    """
    pc = socket.gethostname()
    time1 = time.strftime("%d/%m/%Y, %H:%M:%S")
    if verbose:
        print(pc)
        print(time1)
    if return_vars:
        return time1, pc


def populate_visual_options(l1, new_len=40):
    """
    Auxiliary function for populating the list elements. This is 
    particularly used along with the matplotlib visualisation 
    options to define the colours of the curves.
    Specifically, given a list l1, it repeats the elements of 
    the list to create a new list with new_len elements.
    :param l1: (list) Original list, it will be appended in the 
                beginning of the final list.
    :param new_len: (int, optional) Length of the new list.
    :return: (list) the extended list.
    """
    # accepts a list with elements and populates by choosing some of those and repeating them.
    ll = len(l1)
    assert(ll > 0)
    if ll > new_len: 
        return l1
    import random
    random.seed(0)
    l2 = list(l1)
    for i in range(ll, new_len + 1):
        np = random.randint(0, ll - 1)  # position to sample from
        l2.append(l1[np])
    return l2

