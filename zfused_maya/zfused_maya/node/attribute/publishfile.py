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

from zcore import filefunc

from zfused_maya.core import record

from zfused_maya.node.core import check,texture,xgen,alembiccache,referencefile,yeti

from zfused_maya.ui.widgets import checkwidget

logger = logging.getLogger(__file__)



def publish_file(*args, **kwargs):
    """ publish file
        base publish file script
    :rtype: bool
    """
    _task_id = args[0]
    
    record.write_task_id(_task_id)
    
    _task = zfused_api.task.Task(_task_id)
    _project_entity = _task.project_entity()
    _project_step = _task.project_step()

    # 查看雷区
    _forbidden_script = _project_step.forbidden_script()
    if _forbidden_script:
        forbidden_value = True
        exec(_forbidden_script)
        if not forbidden_value:
            return
    
    # 检查节点
    _project_step_checks = _project_step.checks()
    if _project_step_checks:
        
        if not check.Check.value:
            _ui = checkwidget.CheckWidget(_project_step_checks)
            _ui.show()
        if check.Check.value == True:
            check.Check.value = False
        else:
            return False

    _infomation = {}
    # 提交publish文件
    _value = publish_transfer(_task_id, _infomation)
    if not _value:
        cmds.confirmDialog(message=u"上传交接文件失败")
        return False  
    
    cmds.confirmDialog(message=u"交接文件上传成功\n")


def publish_transfer(task_id, infomation={}, fix_version=False):
    """ 上传任务备份文件
    """

    try:
        _format_type = cmds.file(q=True, typ=True)[0]
        cmds.file(save=True, type=_format_type, f=True, options="v=0;")
    except:
        pass

    _infomation = infomation
    _current_file = cmds.file(q=True, sn=True)
    _task_id = task_id

    # get backup file path
    _task_handle = zfused_api.task.Task(_task_id)
    _project_entity = _task_handle.project_entity()
    _transfer_path = _task_handle.transfer_path()
    _file_code = _project_entity.file_code()
    # if fix_version:
    #     _file_index = _task_handle.last_version_index(0)
    # else:
    #     _file_index = _task_handle.last_version_index() + 1
    if _task_handle.data()["Object"] == "asset":
        _file_suffix = "mb"
        _file_type = "mayaBinary"
    else:
        _file_suffix = "ma"
        _file_type = "mayaAscii"
    _transfer_file = "%s/%s.%s" % (_transfer_path, _file_code, _file_suffix)

    # # get publish file path
    # _temp_path = _task_handle.temp_path()
    # _publish_file = "%s/%s.%04d.%s" % (_temp_path, _file_code, _file_suffix)
    # _publish_file_dir = os.path.dirname(_publish_file)
    # if not os.path.isdir(_publish_file_dir):
    #     os.makedirs(_publish_file_dir)

    # 移出transfer之前文件
    try:
        shutil.rmtree(_transfer_path)
    except:
        pass
    
    try:
        # save publish file
        # cmds.file(rename=_publish_file)
        cmds.file(save=True, type=_file_type, f=True, options="v=0;")

        # publish texture
        _texture_files = texture.files()
        if _texture_files:
            _path_set = texture.paths(_texture_files)[0]
            _intersection_path = max(_path_set)
            texture.publish_file(_texture_files, _intersection_path, _transfer_path + "/texture")
            # change maya texture node path
            _file_nodes = texture.nodes()
            if _file_nodes:
                texture.change_node_path(_file_nodes, _intersection_path, _transfer_path + "/texture")

        # publish xgen file
        if xgen.xgenfile():
            xgen.publishxgen()

        # publish alembic cache
        _alembic_files = alembiccache.files()
        if _alembic_files:
            _path_set = alembiccache.paths(_alembic_files)[0]
            _intersection_path = max(_path_set)
            alembiccache.publish_file(_alembic_files, _intersection_path, _transfer_path + "/cache/alembic")
            _file_nodes = alembiccache.nodes()
            if _file_nodes:
                alembiccache.change_node_path(_file_nodes, _intersection_path, _transfer_path + "/cache/alembic")

        # publish reference file
        _reference_files = referencefile.files()
        if _reference_files:
            _path_set = referencefile.paths(_reference_files)[0]
            _intersection_path = max(_path_set)
            referencefile.publish_file(_reference_files, _intersection_path, _transfer_path + "/reference")
            _file_nodes = referencefile.nodes()
            if _file_nodes:
                referencefile.change_node_path(_file_nodes, _intersection_path, _transfer_path + "/reference")

        # publish yetinode texture
        _yeti_texture_file = yeti.tex_files()
        if _yeti_texture_file:
            _path_set = yeti.paths(_yeti_texture_file)[0]
            _intersection_path = max(_path_set)
            yeti.publish_file(_yeti_texture_file, _intersection_path, _transfer_path + "/texture/yeti")
            _yeti_texture_dict = yeti._get_yeti_attr("texture", "file_name")
            yeti.change_node_path(_yeti_texture_dict, _intersection_path, _transfer_path + "/texture/yeti")
        #print("publish yeti texture over")

        # save publish file
        cmds.file(save=True, type=_file_type, f=True, options="v=0;")

        # publish file
        _result = filefunc.publish_file(_current_file, _transfer_file)

    except Exception as e:
        logger.error(e)
        return False
    cmds.file(new=True, f=True)
    cmds.file(_current_file, o=True, f=True, pmt=False)
    return True