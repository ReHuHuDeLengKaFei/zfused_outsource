# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import time
import logging

import maya.cmds as cmds

import zfused_api

from zcore import zfile,transfer,filefunc

logger = logging.getLogger(__name__)


def publish_media(*args, **kwargs):
    """ 上传任务模型文件
    """
    
    _task_id, _output_attr_id = args

    _output_attr_handle = zfused_api.attr.Output(_output_attr_id)
    _file_format = _output_attr_handle.format()
    _suffix = _output_attr_handle.suffix()
    _attr_code = _output_attr_handle.code()

    _task = zfused_api.task.Task(_task_id)    
    _production_path = _task.production_path()
    _project_entity_production_path = _task.project_entity().production_path()
    _temp_path = _task.temp_path()
    _file_code = _task.file_code()
    if kwargs.get("fix_version"):
        _file_index = "{:0>4d}".format(_task.last_version_index( 0 ))
    else:
        _file_index = "{:0>4d}".format(_task.last_version_index() + 1)

    _production_file = "{}/{}/{}.{}{}".format( _production_path, _attr_code, _file_code, _file_index, _suffix )
    _production_file_dir = os.path.dirname(_production_file)
    _cover_file = "{}/{}/{}{}".format(_production_path, _attr_code, _file_code, _suffix)
    _publish_cover_file = "{}/{}/{}{}".format( _temp_path, _attr_code, _file_code, _suffix )
    _publish_file = "{}/{}/{}.{}{}".format( _temp_path, _attr_code, _file_code, _file_index, _suffix )
    _publish_file_dir = os.path.dirname(_publish_file)
    if not os.path.isdir(_publish_file_dir):
        os.makedirs(_publish_file_dir)

    _video_file = kwargs.get("video")
        
    try:


        if os.path.isfile(_video_file):

            # publish file
            _publish_file = _video_file

            filefunc.publish_file(_publish_file, _production_file)
            filefunc.publish_file(_publish_file, _cover_file)
            
            # production file
            _file_info = zfile.get_file_info(_publish_file, _production_file)
            _cover_file_info = zfile.get_file_info(_publish_file, _cover_file)
            zfused_api.task.new_production_file([_file_info, _cover_file_info], _task_id, _output_attr_id, int(_file_index) )

    except Exception as e:
        logger.error(e)
        return False

    return True