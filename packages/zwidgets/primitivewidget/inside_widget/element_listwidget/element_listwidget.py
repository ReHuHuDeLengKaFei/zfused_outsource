# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import lineedit

from . import iconitemdelegate,listview,listmodel,listitemdelegate



class ElementListWidget(QtWidgets.QFrame):
    task_selected = QtCore.Signal(int)
    gpu_import = QtCore.Signal(str)
    replace_by_project_step_id = QtCore.Signal(int)
    def __init__(self, parent = None):
        super(ElementListWidget, self).__init__(parent)
        self._build()
        self.search_lineedit.search_clicked.connect(self._search)

        self.listwidget.clicked.connect(self._selected_task)

        self.listwidget.doubleClicked.connect(self._selected_task)

        self.listwidget.download.connect(self._selected_task)

        self.listwidget.download.connect(self._import_gpu)

    def _selected_task(self, index):
        _data = index.data()
        self.task_selected.emit(_data.get("Id"))

    def _import_gpu(self, index):
        _data = index.data()
        _task_id = _data.get("task_id")
        _task = zfused_api.task.Task(_task_id)
        _production_path = _task.production_path()
        _gpu_path = "{}/gpu/{}.abc".format(_production_path, _task.file_code())
        if os.path.isfile(_gpu_path):
            self.gpu_import.emit(_gpu_path)

    def _search(self, text):
        """ search task
        """
        self.task_proxy_model.search(text)

    # @zfused_api.reset
    # def load_project_id(self, project_id, has_version):
    #     # get alembic cache
    #     _gpu_project_step_ids = []
    #     _asset_steps = zfused_api.zFused.get("project_step", filter = {"ProjectId": project_id,"Object":"asset"})
    #     if _asset_steps:
    #         _asset_step_ids = [_asset_step.get("Id") for _asset_step in _asset_steps]
    #     if _asset_step_ids:
    #         # 获取 混合两种输出方案
    #         _attr_outputs = zfused_api.zFused.get("attr_output", filter = {"ProjectStepId__in":"|".join([str(_id) for _id in _asset_step_ids]), "Code":"gpu"})
    #         if not _attr_outputs:
    #             _attr_outputs = zfused_api.zFused.get("step_attr_output", filter = {"ProjectStepId__in":"|".join([str(_id) for _id in _asset_step_ids]), "Code":"gpu"})
    #         if _attr_outputs:
    #             _gpu_project_step_ids = [_attr_output.get("ProjectStepId") for _attr_output in _attr_outputs ]
        
    #     if _gpu_project_step_ids:
    #         _tasks = zfused_api.zFused.get("task", filter = {"ProjectStepId__in": "|".join(str(_id) for _id in _gpu_project_step_ids)})
    #         if has_version:
    #             _task_ids = [_task.get("Id") for _task in _tasks if _task.get("LastVersionId")]
    #         else:
    #             _task_ids = [_task.get("Id") for _task in _tasks]
    #         _tasks = zfused_api.task.cache_from_ids(_task_ids)
    #         model = listmodel.ListModel(_tasks, self.listwidget)
    #         self.task_proxy_model.setSourceModel(model)

    def load_elements(self, datas):
        model = listmodel.ListModel(datas, self.listwidget)
        self.task_proxy_model.setSourceModel(model)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)

        self.contant_widget = QtWidgets.QFrame()
        _layout.addWidget(self.contant_widget)
        self.contant_layout = QtWidgets.QVBoxLayout(self.contant_widget)
        self.contant_layout.setContentsMargins(0,0,0,0)
        self.contant_layout.setSpacing(0)
        self.setObjectName("widget")

        # search name
        self.search_lineedit = lineedit.SearchLineEdit()
        self.contant_layout.addWidget(self.search_lineedit)
        self.search_lineedit.setMinimumHeight(24)

        # task list widget
        self.listwidget = listview.ListView()
        # self.listwidget.setViewMode(QtWidgets.QListView.IconMode)
        # self.listwidget.setViewMode(QtWidgets.QListView.ListMode)
        self.contant_layout.addWidget(self.listwidget)
        self.listwidget.setObjectName("listwidget")
        self.task_proxy_model = listmodel.ListFilterProxyModel()
        self.listwidget.setModel(self.task_proxy_model)
        self.listwidget.setItemDelegate(iconitemdelegate.IconItemDelegate(self.listwidget))
        # self.listwidget.setItemDelegate(listitemdelegate.ListItemDelegate(self.listwidget))