# coding:utf-8
# --author-- lanhua.zhou
from functools import  partial

import logging

import maya.cmds as cmds
import maya.mel as mm

from Qt import QtCore

import zfused_api

import zfused_maya.node.core.clear as clear
import zfused_maya.core.record as record

import zfused_maya.core.defender as defender


logger = logging.getLogger(__name__)


class StartupSetting(QtCore.QObject):
    def __init__(self):
        super(StartupSetting, self).__init__()
    
    def run(self):
        allJobs = cmds.scriptJob(lj = True)
        for job in allJobs:
            if "zfused_maya.interface.setting.StartupSetting" in job or "kill_putian" in job or "delete_useless" in job or "execute" in job:
                id = int(job.split(":")[0])
                cmds.scriptJob(kill= id, force=True)

        cmds.scriptJob(e = ("PostSceneRead", self.clear_unknown_plugins), protected = True)
        cmds.scriptJob(e = ("PostSceneRead", self.clear_onModelChange3dc), protected = True)
        cmds.scriptJob(e = ("PostSceneRead", self.hw_instance), protected = True)
        
        # cmds.scriptJob(e = ("PostSceneRead", self.preview_scene), protected = True)
        cmds.scriptJob(e = ("SceneSaved", self.unlock_file), protected = True)
        cmds.scriptJob(e = ("SceneSaved", self.clear_nodeGraphEditorInfo), protected = True)
        
        
        _incremental_save = True
        _clear_unused = True
        _project_id = record.current_project_id()
        if _project_id:
            _project = zfused_api.project.Project(_project_id)
            _incremental_save = _project.variables("incremental_save", True)
            _clear_unused = _project.variables("clear_unused", True)

        # # 先注销
        # if _incremental_save:
        #     cmds.scriptJob(e = ("SceneSaved", partial(self.incremental_save, 1) ), protected = True)
        # else:
        #     cmds.scriptJob(e = ("SceneSaved", partial(self.incremental_save, 0) ), protected = True)
        
        # 先注销使用，会清除特效示意节点 fuild
        if _clear_unused:
            cmds.scriptJob(e = ("SceneSaved", self.clear_unused), protected = True)

        defender.run()

    
    def hw_instance(self):
        # gpu instance 显示加速
        cmds.setAttr("hardwareRenderingGlobals.hwInstancing", True)

    def clear_unused(self):
        mm.eval("MLdeleteUnused;")

    def unlock_file(self):
        cmds.optionVar(intValue = ("defaultLockFile",  0))

    def incremental_save(self, value):
        cmds.optionVar(intValue = ("isIncrementalSaveEnabled",  value))

    def preview_scene(self):
        """ 刷新显示多象限
        """
        mm.eval("optionVar -iv generateUVTilePreviewsOnSceneLoad true;")
        mm.eval("generateAllUvTilePreviews;")

    def clear_unknown_plugins(self):
        """ clear unknown plugins
        """
        logger.info("run clear unknown plugins")
        # if not is_exist:
        clear.unknown_plugins()

    def clear_onModelChange3dc(self):
        logger.info("run clear onModelChange3dc")
        clear.onModelChange3dc()

    def clear_nodeGraphEditorInfo(self):
        import maya.cmds as cmds
        _nodeGraphEditorInfo = cmds.ls(type = 'nodeGraphEditorInfo')
        finds = len(_nodeGraphEditorInfo)
        if finds > 0:
            cmds.delete(_nodeGraphEditorInfo)
            logger.info('run clear nodeGraphEditorInfo : %d'%finds)
        else:
            pass