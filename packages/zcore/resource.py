# coding:utf-8
# --author-- lanhua.zhou

import os
import sys
import glob

PATH = os.path.dirname(__file__)
RESOURCE_DIRNAME = os.path.dirname(PATH)


from . import resources


def get(*args):
    """This is a convenience function for returning the resource path.
    :rtype: str 
    """
    return os.path.join("{}/resources".format(RESOURCE_DIRNAME), *args).replace(os.sep, "/")
    # return os.path.join(":/resources", *args).replace(os.sep, "/")