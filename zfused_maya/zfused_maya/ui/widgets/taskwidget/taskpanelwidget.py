# coding:utf-8
# --author-- lanhua.zhou

""" 任务面板 """
from __future__ import print_function

import maya.cmds as cmds

import zfused_api

from zwidgets.taskwidget import taskpanelwidget

import zfused_maya.node.inputattr.util as in_util
import zfused_maya.node.outputattr.util as out_util


class TaskPanelWidget(taskpanelwidget.TaskPanelWidget):
    def __init__(self, parent = None):
        super(TaskPanelWidget, self).__init__(parent)

        self.received.connect(self._receive_file)
        self.published.connect(self._publish_file)

        self.opened.connect(self._open_file)

    def _open_file(self, file_path):
        cmds.file(file_path, o = True, f = True)    

    def _receive_file(self, mode, id, input_tasks = []):
        """ load sel index file
        :rtype: None
        """
        if mode == "version":
            in_util.receive_version_file(id)
        elif mode == "task":
            in_util.assembly_file(id, input_tasks)
        elif mode == "update":
            in_util.update_file(id, input_tasks)

    def _publish_file(self, task_id, info, extend_attr = {}):
        _task = zfused_api.task.Task(task_id)
        
        # check shot frame
        _project_entity = _task.project_entity()
        if isinstance(_project_entity, zfused_api.shot.Shot):
            # get start frame and end frame
            min_frame = cmds.playbackOptions(q = True, min = True)
            max_frame = cmds.playbackOptions(q = True, max = True)
            if int(min_frame) != int(_project_entity.data().get("FrameStart")) or int(max_frame) != int(_project_entity.data().get("FrameEnd")):
                cmds.confirmDialog(message=u"帧数设置不对")
                return False

        _value = False
        attrs = extend_attr.get("attrs")
        elements = extend_attr.get("elements")
        if attrs or elements:
            _value = out_util.fix_file(task_id, info, extend_attr)
        else:
            _value = out_util.publish_file(task_id, info, extend_attr)

        # if mode == "new":
        #     _value = out_util.publish_file(task_id, info, elements)
        # elif mode == "fix":
        #     _value = out_util.fix_file(task_id, info)

        if _value:
            self.load_task_id(task_id)

    def load_task_id(self, task_id):
        super(TaskPanelWidget, self).load_task_id(task_id)
        _assets = get_assets()
        self.load_assets(_assets)


def get_assets():
    _asset = []
    # 获取reference文件
    _reference_nodes = cmds.ls(rf=True)
    for _node in _reference_nodes:
        try:
            _file_path = cmds.referenceQuery(_node, f=True, wcn=True)
        except:
            continue

        _is_load = cmds.referenceQuery(_node, il = True)
        if not _is_load:
            continue

        _namespace = cmds.referenceQuery(_node, namespace=True)
        if _namespace.startswith(":"):
            _namespace = _namespace[1::]
        _production_files = zfused_api.zFused.get("production_file_record", filter={
            "Path": _file_path})
        if _production_files:
            _production_file = _production_files[-1]
            _task_id = _production_file.get("TaskId")
            _task = zfused_api.task.Task(_task_id)
            _task_project_entity = _task.project_entity()
            _version_id = _task.versions()
            if _task_project_entity.object() == "asset":
                _asset.append({
                    "id": _task_project_entity.id(),
                    "code": _task_project_entity.code(),
                    "namespace": _namespace,
                    'rfn': _node,
                    'last_cache': "",
                    'project_step_caches': [],
                    'version': _version_id
                })
    return _asset