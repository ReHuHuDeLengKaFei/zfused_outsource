# coding:utf-8
# --author-- lanhua.zhou

""" 视频文件操作函数集合 """

from __future__ import print_function

import os
import glob
import subprocess

PATH = os.path.abspath("./plugins")
if not os.path.isdir(PATH):
    # get max app number
    _all_exe_path = glob.glob("{}/app-*".format(os.getcwd()))
    if _all_exe_path:
        _new_exe_path = max(_all_exe_path)
        PATH = "{}/plugins".format(_new_exe_path)
# DIRNAME = os.path.dirname(os.path.dirname(os.path.dirname(PATH)))
PLUGIN_DIRNAME = PATH

PLUGIN_DIRNAME = os.path.join( os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "plugins")

def cut_image(video, image):
    """ cut video to image
    :rtype: nool
    """
    _ffmpeg_exe = os.path.join(PLUGIN_DIRNAME,"ffmpeg/ffmpeg.exe")
    print(_ffmpeg_exe)
    _pic_command = '"{}" -i "{}" -vframes 1 "{}"'.format(_ffmpeg_exe, video, image)
    _pic_process = subprocess.Popen(_pic_command, shell = True)
    _pic_process.communicate()
    if not os.path.isfile(image):
        return False
    return True