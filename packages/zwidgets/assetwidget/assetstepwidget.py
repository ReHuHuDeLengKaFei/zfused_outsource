# coding:utf-8
# --author-- lanhua.zhou

from __future__ import print_function

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from . import versionlistwidget


class AssetStepWidget(QtWidgets.QFrame):
    reference_version = QtCore.Signal(int)
    def __init__(self, parent=None):
        super(AssetStepWidget, self).__init__(parent)
        self._build()

        self._asset_id = 0
        self._asset_handle = None
        self._project_step_id = 0

        self._index_version = {}

        self.version_listwidget.list_view.clicked.connect(self._load_version)
        self.reference_button.clicked.connect(self._reference_file)

    def _reference_file(self):
        """ reference version file
        """
        _index = self.version_listwidget.list_view.currentIndex()
        if not _index:
            return
        _data = _index.data()
        self.reference_version.emit(_data.get("Id"))

    def load_project_step_id(self, project_step_id):
        """ load project step id
        """
        self.version_combobox.clear()
        self._index_version = {}
        self.description_textedit.clear()
        self.file_name_label.clear()

        if not project_step_id or not self._asset_id:
            return 

        self._project_step_id = project_step_id
        # 
        _project_step_handle = zfused_api.step.ProjectStep(project_step_id)
        _project_step_name_code = _project_step_handle.name_code()
        self.step_button.setText(_project_step_name_code)

        # project version
        _versions = self._asset_handle.project_step_versions(project_step_id)
        _versions.reverse()
        for _index, _version in enumerate(_versions) :
            self.version_combobox.addItem(str(len(_versions) - _index))
            self._index_version[str(len(_versions) - _index)] = _version

        # get files
        self.version_listwidget.load_versions(_versions)

    def load_asset_id(self, asset_id):
        self._asset_id = asset_id
        if not asset_id:
            self.close()
            return 
        else:
            self.show()
        self._asset_handle = zfused_api.asset.Asset(asset_id)

    def _load_version(self, version_index):
        """ load version index
        """
        self.description_textedit.clear()
        _data = version_index.data()
        self.description_textedit.setText(_data["Description"])
        self.file_name_label.setText(_data["FilePath"])

    def _build(self):
        self.resize(160, 200)
        #self.setMaximumWidth(300) 
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(0,0,0,0)

        # project step widget
        self.step_widget = QtWidgets.QFrame()
        self.step_widget.setMinimumHeight(25)
        self.step_layout = QtWidgets.QVBoxLayout(self.step_widget)
        self.step_layout.setSpacing(0)
        self.step_layout.setContentsMargins(0,0,0,0)
        # name button
        self.step_button = QtWidgets.QPushButton()
        self.step_button.setText(u"项目步骤")
        self.step_button.setIcon(QtGui.QIcon(resource.get("icons", "step.png")))
        self.step_button.setObjectName("title_button")
        self.step_layout.addWidget(self.step_button)

        # version widget
        self.version_widget = QtWidgets.QFrame()
        self.version_widget.setMinimumHeight(25)
        self.version_layout = QtWidgets.QHBoxLayout(self.version_widget)
        self.version_layout.setSpacing(20)
        self.version_layout.setContentsMargins(20,0,20,0)
        #  version name button
        self.version_name_button = QtWidgets.QPushButton()
        self.version_name_button.setText(u"版本")
        #  version combobox
        self.version_combobox = QtWidgets.QComboBox()
        self.version_layout.addWidget(self.version_combobox)
        self.version_layout.addStretch(True)

        # listwidget
        self.version_listwidget = versionlistwidget.listwidget.ListWidget()

        # description widget
        self.description_textedit = QtWidgets.QTextEdit()
        self.description_textedit.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.description_textedit.setEnabled(False)
        self.description_textedit.setMaximumHeight(40)
        self.description_textedit.setPlaceholderText("version description")

        # operation widget
        # 
        self.operation_widget = QtWidgets.QFrame()
        self.operation_widget.setObjectName("operation_widget")
        self.operation_widget.setMinimumHeight(30)
        self.operation_layout = QtWidgets.QHBoxLayout(self.operation_widget)
        self.operation_layout.setContentsMargins(0,0,0,0)
        # file name
        self.file_name_label = QtWidgets.QLabel()
        self.operation_layout.addWidget(self.file_name_label)
        self.operation_layout.addStretch(True)
        # reference file
        self.reference_button = QtWidgets.QPushButton()
        self.reference_button.setObjectName("reference_button")
        self.reference_button.setFixedSize(100,30)
        self.reference_button.setText(u"参考文件")
        self.operation_layout.addWidget(self.reference_button)
        # import gpu
    
        # _layout.addWidget(self.thumbnail_widget)
        _layout.addWidget(self.step_widget)
        # _layout.addWidget(self.version_widget)
        # _layout.addStretch(True)
        _layout.addWidget(self.version_listwidget )
        _layout.addWidget(self.description_textedit)
        _layout.addWidget(self.operation_widget)