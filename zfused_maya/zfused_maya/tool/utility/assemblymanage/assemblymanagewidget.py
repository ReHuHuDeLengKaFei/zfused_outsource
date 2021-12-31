# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import maya.cmds as cmds

import zfused_api

from zwidgets.assemblywidget import assemblymanagewidget

import zfused_maya.core.record as record
import zfused_maya.node.core.attr as attr
from zfused_maya.ui.widgets import window



__all__ = ["AssemblyManageWidget"]

logger = logging.getLogger(__name__)


class AssemblyManageWidget(window._Window):
    def __init__(self, parent = None):
        super(AssemblyManageWidget, self).__init__()
        self._build()

        self.assembly_widget.reference_version.connect(self._reference)

    def _reference(self, version_id):
        _version = zfused_api.version.Version(version_id)

        _type_code = "assembly_group"
        if not cmds.objExists(_type_code):
            cmds.createNode("transform", name = _type_code)

        _task = _version.task()
        _project_step = _task.project_step()
        _key_output_attr = _project_step.key_output_attr()

        _production_file = _version.production_file()
        _production_file = ".".join(_production_file.split(".{:0>4d}.".format(_version.index())))
        print(_production_file)

        _ori_assemblies = cmds.ls(assemblies=True)
        _ns = "{}__ns__00".format(_task.project_entity().file_code())
        rf = cmds.file(_production_file, r = True, ns = _ns)
        rfn = cmds.referenceQuery(rf, rfn = True)
        attr.set_node_attr(rfn, _key_output_attr["Id"], _version.id(), "false")
        _new_assemblies = cmds.ls(assemblies=True)
        _assembly_tops = list(set(_new_assemblies) - set(_ori_assemblies))
        if _assembly_tops:
            for _assembly_top in _assembly_tops:
                try:
                    cmds.parent(_assembly_top, _type_code)
                except:
                    pass

    def _build(self):
        self.resize(1600, 900)
        self.set_title_name(u"场景装配管理(assembly management)")

        self.assembly_widget = assemblymanagewidget.AssemblyManageWidget()
        self.set_central_widget(self.assembly_widget)

    def showEvent(self, event):
        _project_id = record.current_project_id()
        self.assembly_widget.load_project_id(_project_id)
        super(AssemblyManageWidget, self).showEvent(event)