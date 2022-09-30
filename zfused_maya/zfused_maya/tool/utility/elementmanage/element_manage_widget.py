# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

import zfused_maya.core.record as record

from zfused_maya.node.core import element

from zwidgets.element_widget import element_manage_widget

from zfused_maya.ui.widgets import window

import maya.cmds as cmds

__all__ = ["ElementManageWidget"]

logger = logging.getLogger(__name__)


class ElementManageWidget(window._Window):
    def __init__(self, parent = None):
        super(ElementManageWidget, self).__init__()
        self._build()

    def showEvent(self, event):

        super(ElementManageWidget, self).showEvent(event)

    def refresh_scene(self):
        # get scene elements
        _scene_elements = element.reference_elements()
        self.element_widget.load_elements(_scene_elements)

    def showEvent(self, event):
        self.refresh_scene()
        super(ElementManageWidget, self).showEvent(event)
        # self._script_job()

    def _script_job(self):
        import maya.cmds as cmds
        allJobs = cmds.scriptJob(lj = True)
        for job in allJobs:
            if "zfused_maya.tool.utility.elementmanage.element_manage_widget" in job:
                id = int(job.split(":")[0])
                cmds.scriptJob(kill= id, force=True)
        # if not is_exist:
        cmds.scriptJob(e = ("PostSceneRead", self.refresh_scene), protected = True)

    def _build(self):
        self.resize(1600, 900)
        self.set_title_name(u"场景元素管理")

        self.element_widget = element_manage_widget.ElementManageWidget()
        self.set_central_widget(self.element_widget)