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

from zfused_maya.node.core import check

from zfused_maya.ui.widgets import checkwidget

logger = logging.getLogger(__file__)



def publish_file(*args, **kwargs):
    """ publish file
        base publish file script
    :rtype: bool
    """
    _task_id = args[0]
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

    # 提交publish文件
    _value = publish_backup(task_id, infomation)
    if not _value:
        cmds.confirmDialog(message=u"上传备份文件失败")
        return False  
    
    cmds.confirmDialog(message=u"提取成功\n{}".format("ds"))



def publish_backup(task_id, infomation={}, fix_version=False):
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
    _backup_path = _task_handle.backup_path()
    _file_code = _project_entity.file_code()
    if fix_version:
        _file_index = _task_handle.last_version_index(0)
    else:
        _file_index = _task_handle.last_version_index() + 1
    if _task_handle.data()["Object"] == "asset":
        _file_suffix = "mb"
        _file_type = "mayaBinary"
    else:
        _file_suffix = "ma"
        _file_type = "mayaAscii"
    _backup_file = "%s/%s.%04d.%s" % (_backup_path, _file_code, _file_index, _file_suffix)

    # get publish file path
    _temp_path = _task_handle.temp_path()
    _publish_file = "%s/%s.%04d.%s" % (_temp_path, _file_code, _file_index, _file_suffix)
    _publish_file_dir = os.path.dirname(_publish_file)
    #print("publish_path:{}".format(_production_path))

    if not os.path.isdir(_publish_file_dir):
        os.makedirs(_publish_file_dir)
    try:
        # save publish file
        cmds.file(rename=_publish_file)
        cmds.file(save=True, type=_file_type, f=True, options="v=0;")
        # publish texture
        _texture_files = texture.files()
        if _texture_files:
            _path_set = texture.paths(_texture_files)[0]
            _intersection_path = max(_path_set)
            texture.publish_file(_texture_files, _intersection_path, _backup_path + "/texture")
            # change maya texture node path
            _file_nodes = texture.nodes()
            if _file_nodes:
                texture.change_node_path(_file_nodes, _intersection_path, _backup_path + "/texture")
        #print("publish texture over")

        # publish xgen file
        if xgen.xgenfile():
            xgen.publishxgen()

        # publish alembic cache
        _alembic_files = alembiccache.files()
        if _alembic_files:
            _path_set = alembiccache.paths(_alembic_files)[0]
            _intersection_path = max(_path_set)
            alembiccache.publish_file(_alembic_files, _intersection_path, _backup_path + "/cache/alembic")
            _file_nodes = alembiccache.nodes()
            if _file_nodes:
                alembiccache.change_node_path(_file_nodes, _intersection_path, _backup_path + "/cache/alembic")
        #print("publish alembic cache over")
        # publish reference file
        _reference_files = referencefile.files()
        if _reference_files:
            _path_set = referencefile.paths(_reference_files)[0]
            _intersection_path = max(_path_set)
            referencefile.publish_file(_reference_files, _intersection_path, _backup_path + "/reference")
            _file_nodes = referencefile.nodes()
            if _file_nodes:
                referencefile.change_node_path(_file_nodes, _intersection_path, _backup_path + "/reference")
        #print("publish reference over")
        # publish yetinode texture
        _yeti_texture_file = yeti.tex_files()
        if _yeti_texture_file:
            _path_set = yeti.paths(_yeti_texture_file)[0]
            _intersection_path = max(_path_set)
            yeti.publish_file(_yeti_texture_file, _intersection_path, _backup_path + "/texture/yeti")
            _yeti_texture_dict = yeti._get_yeti_attr("texture", "file_name")
            yeti.change_node_path(_yeti_texture_dict, _intersection_path, _backup_path + "/texture/yeti")
        #print("publish yeti texture over")

        # save publish file
        cmds.file(save=True, type=_file_type, f=True, options="v=0;")

        # publish file
        _result = filefunc.publish_file(_publish_file, _backup_file)

        # if _infomation:
        #     _project_handle = zfused_api.project.Project(_task_handle.data()["ProjectId"])
        #     _project_step = zfused_api.step.ProjectStep(_task_handle.data()["ProjectStepId"])
        #     _approval_ftp = "/storage/approval/{}/{}/{}/{}".format(_project_handle.code(),
        #                                                            _task_handle.data()["ProjectEntityType"],
        #                                                            _project_step.code(),
        #                                                            _project_entity.code())
        #     # publish thumbnail and video
        #     if "video" in _infomation:
        #         _video_file = _infomation["video"]
        #         if _video_file:
        #             _video_suffix = os.path.splitext(_video_file)[-1]
        #             _video_backup_file = "%s/%s.%04d%s" % (_backup_path, _file_code, _file_index, _video_suffix)
        #             _video_production_file = "%s/thumbnail/%s.%04d%s" % (_production_path, _file_code, _file_index, _video_suffix)
        #             _result = filefunc.publish_file(_video_file, _video_backup_file)
        #             _result = filefunc.publish_file(_video_file, _video_production_file)

        #     _thumbnail_file = _infomation["thumbnail"]
        #     _thumbnail_suffix = os.path.splitext(_thumbnail_file)[-1]
        #     _thumbnail_backup_file = "%s/%s.%04d%s" % (_backup_path, _file_code, _file_index, _thumbnail_suffix)
        #     _thumbnail_production_file = "%s/thumbnail/%s.%04d%s" % (
        #     _production_path, _file_code, _file_index, _thumbnail_suffix)
        #     _result = filefunc.publish_file(_thumbnail_file, _thumbnail_backup_file)
        #     _result = filefunc.publish_file(_thumbnail_file, _thumbnail_production_file)

    except Exception as e:
        logger.error(e)
        return False
    cmds.file(new=True, f=True)
    cmds.file(_current_file, o=True, f=True, pmt=False)
    return True