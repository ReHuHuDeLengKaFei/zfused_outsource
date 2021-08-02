# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

import zfused_maya.core.record as record

from zwidgets.assetwidget import assetmanagewidget

from zfused_maya.ui.widgets import window

import maya.cmds as cmds
import zfused_maya.node.core.attr as attr

__all__ = ["AssetManageWidget"]

logger = logging.getLogger(__name__)


class AssetManageWidget(window._Window):
    def __init__(self, parent = None):
        super(AssetManageWidget, self).__init__()
        self._build()

        self.asset_widget.reference_by_attr.connect(self._reference)

    def _reference(self, version_id, output_attr_id):
        _version = zfused_api.version.Version(version_id)

        # asset type
        _type = _version.project_entity().type()
        _type_code = _type.code()
        if not cmds.objExists(_type_code):
            cmds.createNode("transform", name = _type_code)

        _task = _version.task()
        _project_step = _task.project_step()
        # _key_output_attr = _project_step.key_output_attr()
        # print(output_attr_id)
        _output_attr = zfused_api.attr.Output(output_attr_id)

        _production_file = _version.production_file()

        _ori_assemblies = cmds.ls(assemblies=True)
        rf = cmds.file(_production_file, r = True, ns = _task.file_code())
        rfn = cmds.referenceQuery(rf, rfn = True)
        attr.set_node_attr(rfn, _output_attr.id(), _version.id(), "false")
        _new_assemblies = cmds.ls(assemblies=True)
        _asset_tops = list(set(_new_assemblies) - set(_ori_assemblies))
        if _asset_tops:
            for _asset_top in _asset_tops:
                try:
                    cmds.parent(_asset_top, _type_code)
                except:
                    pass

    def _build(self):
        self.resize(1600, 900)
        self.set_title_name(u"资产管理(asset management)")

        self.asset_widget = assetmanagewidget.AssetManageWidget()
        self.set_central_widget(self.asset_widget)

    def showEvent(self, event):
        _project_id = record.current_project_id()
        self.asset_widget.load_project_id(_project_id)
        super(AssetManageWidget, self).showEvent(event)