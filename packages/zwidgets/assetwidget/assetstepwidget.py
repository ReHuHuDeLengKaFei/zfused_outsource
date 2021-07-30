# coding:utf-8
# --author-- lanhua.zhou

from __future__ import print_function
from functools import partial

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from . import versionlistwidget


class AssetStepWidget(QtWidgets.QFrame):
    reference_by_attr = QtCore.Signal(int, int)
    def __init__(self, parent=None):
        super(AssetStepWidget, self).__init__(parent)
        self._build()

        self._asset_id = 0
        self._asset_handle = None
        self._project_step_id = 0

        self._index_version = {}

        self.version_listwidget.list_view.clicked.connect(self._load_version)

    def _reference_file(self, output_attr_id):
        """ reference version file
        """
        _index = self.version_listwidget.list_view.currentIndex()
        if not _index:
            return
        _data = _index.data()
        self.reference_by_attr.emit(_data.get("Id"), output_attr_id)

    def _clear(self):
        self.version_combobox.clear()
        self._index_version = {}
        self.description_textedit.clear()
        # remove operation
        for i in range(self.operation_layout.count()):
            self.operation_layout.itemAt(i).widget().deleteLater()

    def load_project_step_id(self, project_step_id):
        """ load project step id
        """
        self._clear()

        if not project_step_id or not self._asset_id:
            return 

        self._project_step_id = project_step_id
        
        # project step
        _project_step = zfused_api.step.ProjectStep(project_step_id)
        _project_step_name_code = _project_step.name_code()
        self.step_button.setText(_project_step_name_code)

        # project version
        _versions = self._asset_handle.project_step_versions(project_step_id)
        _versions.reverse()
        for _index, _version in enumerate(_versions) :
            self.version_combobox.addItem(str(len(_versions) - _index))
            self._index_version[str(len(_versions) - _index)] = _version

        # get files
        self.version_listwidget.load_versions(_versions)

        # output attrs
        _output_attrs = _project_step.output_attrs()
        if _output_attrs:
            for _output_attr in _output_attrs:
                if _project_step.is_new_attribute_solution():
                    _output_attr = zfused_api.attr.Output(_output_attr.get("Id"))
                else:
                    _output_attr = zfused_api.outputattr.OutputAttr(_output_attr.get("Id"))
                _operation_widget = OperationWidget()
                _operation_widget.load_output_attr(_output_attr)
                _operation_widget.referenced.connect(self._reference_file)
                self.operation_layout.addWidget(_operation_widget)

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
        # self.file_name_label.setText(_data["FilePath"])

    def _build(self):
        self.resize(160, 200)
        #self.setMaximumWidth(300) 
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(0,0,0,0)

        # ==================================================================================
        # project step widget
        self.step_widget = QtWidgets.QFrame()
        _layout.addWidget(self.step_widget)
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

        # ==================================================================================
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
        _layout.addWidget(self.version_listwidget )

        # ==================================================================================
        # description widget
        self.description_textedit = QtWidgets.QTextEdit()
        _layout.addWidget(self.description_textedit)
        self.description_textedit.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.description_textedit.setEnabled(False)
        self.description_textedit.setMaximumHeight(40)
        self.description_textedit.setPlaceholderText("version description")

        # ==================================================================================
        # operation widget
        self.operation_widget = QtWidgets.QFrame()
        _layout.addWidget(self.operation_widget)
        self.operation_widget.setObjectName("operation_widget")
        self.operation_widget.setMinimumHeight(30)
        self.operation_layout = QtWidgets.QVBoxLayout(self.operation_widget)
        self.operation_layout.setContentsMargins(0,0,0,0)
        # # file name
        # self.file_name_label = QtWidgets.QLabel()
        # self.operation_layout.addWidget(self.file_name_label)
        # self.operation_layout.addStretch(True)
        # # reference file
        # self.reference_button = QtWidgets.QPushButton()
        # self.reference_button.setObjectName("reference_button")
        # self.reference_button.setFixedSize(100,30)
        # self.reference_button.setText(u"参考文件")
        # self.operation_layout.addWidget(self.reference_button)
        
        

class OperationWidget(QtWidgets.QFrame):
    referenced = QtCore.Signal(int)
    def __init__(self, parent = None):
        super(OperationWidget, self).__init__(parent)
        self._build()

        self._output_attr_id = 0

        self.reference_button.clicked.connect(self._reference)

    def _reference(self):
        self.referenced.emit(self._output_attr_id)

    def load_output_attr(self, output_attr):
        self._output_attr_id = output_attr.id()
        self.title_label.setText(output_attr.name())
        self.format_label.setText(output_attr.data().get("Format"))
        self.suffix_label.setText(output_attr.data().get("Suffix"))

    def _build(self):
        self.setObjectName("operation_widget")
        self.setMinimumHeight(40)

        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setContentsMargins(4,4,4,4)
        
        self.title_label = QtWidgets.QLabel()
        _layout.addWidget(self.title_label)

        _layout.addStretch(True)

        self.format_label = QtWidgets.QLabel()
        _layout.addWidget(self.format_label)

        _layout.addStretch(True)

        self.suffix_label = QtWidgets.QLabel()
        _layout.addWidget(self.suffix_label)

        _layout.addStretch(True)

        # self.import_button = QtWidgets.QPushButton()
        # _layout.addWidget(self.import_button)
        # self.import_button.setText(u"Import导入")
        # self.import_button.setFixedSize(120, 30)

        self.reference_button = QtWidgets.QPushButton()
        _layout.addWidget(self.reference_button)
        self.reference_button.setText(u"Reference参考")
        self.reference_button.setFixedSize(120, 30)


