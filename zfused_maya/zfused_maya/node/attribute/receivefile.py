 # coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import shutil
import logging
import datetime
import time

import maya.cmds as cmds

import zfused_api
import zfused_maya.node.core.attr as attr


logger = logging.getLogger(__file__)



def receive_file(*args, **kwargs):
    """ receive file
        base receive file script
    :rtype: bool
    """
    print("receive")
    return