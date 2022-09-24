# coding:utf-8
# --author-- lanhua.zhou

from __future__ import print_function
from functools import partial

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from . import path_widget

class ProjectWidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(ProjectWidget, self).__init__(parent)

        self._build()

    def load_project_id(self, project_id):
        for i in range(self.path_layout.count()):
            self.path_layout.itemAt(i).widget().deleteLater()

        _project = zfused_api.project.Project(project_id)
        # production path
        _production_path = _project.production_path()
        print(_production_path)
        self.path_layout.addWidget( path_widget.PathWidget(_production_path) )

        # backup path
        _backup_path = _project.backup_path()
        self.path_layout.addWidget( path_widget.PathWidget(_backup_path) )

        # work_path
        _work_path = _project.work_path()
        self.path_layout.addWidget( path_widget.PathWidget(_work_path) )

        # temp_path
        _temp_path = _project.temp_path()
        self.path_layout.addWidget( path_widget.PathWidget(_temp_path) )

        # image_path
        _image_path = _project.image_path()
        self.path_layout.addWidget( path_widget.PathWidget(_image_path) )

        # cache_path
        _cache_path = _project.cache_path()
        self.path_layout.addWidget( path_widget.PathWidget(_image_path) )

    def check(self):
        for i in range(self.path_layout.count()):
            self.path_layout.itemAt(i).widget().run()

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        self.scroll_widget = QtWidgets.QScrollArea(self)
        _layout.addWidget(self.scroll_widget)
        self.scroll_widget.setWidgetResizable(True)
        self.scroll_widget.setBackgroundRole(QtGui.QPalette.NoRole)

        self.content_widget = QtWidgets.QFrame()
        self.scroll_widget.setWidget(self.content_widget)
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0,0,0,0)

        self.path_widget = QtWidgets.QFrame()
        self.content_layout.addWidget(self.path_widget)
        self.path_layout = QtWidgets.QVBoxLayout(self.path_widget)
        self.path_layout.setSpacing(0)
        self.path_layout.setContentsMargins(0,0,0,0)

        self.content_layout.addStretch(True)

