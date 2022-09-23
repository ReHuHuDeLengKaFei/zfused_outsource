# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import time
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

# from . import basewidget



class FixPublishWidget(QtWidgets.QFrame):

    published = QtCore.Signal(int, dict, dict)
    
    selected_from_scene = QtCore.Signal()

    def __init__(self, parent = None):
        super(FixPublishWidget, self).__init__(parent)
        self._build()

        self._task_id = 0
        self._task_handle = None

        self.publish_button.clicked.connect(self._publish)
    
        self.asset_widget.selected_from_scene.connect(self.selected_from_scene.emit)

    def load_assets(self, assets):
        self.asset_widget.load_assets(assets)

    def get_assets(self):
        return self.asset_widget.get_assets()
    
    def get_attrs(self):
        return self.attr_widget.get_attrs()

    def _publish(self):
        """ publish file
        :rtype: bool
        """

        self.info_widget.setHidden(True)
        # check info
        _check_value = self._check()
        if not _check_value:
            self.info_widget.setHidden(False)
            return 

        _kwargs = {}
        _assets = self.get_assets()
        if _assets:
            _kwargs["assets"] = _assets
        
        _sample = self.sample_widget.sample()
        _kwargs["sample"] = _sample

        _fixs = {}
        # _fixs[]

        _attrs = self.get_attrs()
        if _attrs:
            _kwargs["attrs"] = _attrs

        _information = {}
        _information["description"] = u"单独发布 - {}".format( " | ".join([ _asset.get("rfn") for _asset in _assets ]) )
        self.published.emit(self._task_id, _information, _kwargs)

    def _check(self):
        """ check base infomation
        :rtype: bool
        """
        self.info_widget.setHidden(True)

        # _assets = self.get_assets()
        # if not _assets:
        #     self._set_error_text(u"未选择单独发布资产")
        #     return False

        _index = self._task_handle.last_version_index()
        if not _index:
            self._set_error_text(u"当前任务或父任务没有版本，不可单独发布")
            return False

        return True

    def _set_error_text(self, text):
        """ 显示错误信息
        :rtype: None
        """
        self.info_label.setText(text)
        self.info_widget.setHidden(False)

    def _restore(self):
        """ restore the widget
        :rtype: None
        """
        # clear attr checkbox
        for i in reversed(range(self.attr_layout.count())): 
            _widget = self.attr_layout.itemAt(i).widget()
            _widget.setParent(None)
            _widget.deleteLater()

    # def single_publish(self, attr):
    #     # publish file
    #     util.single_publish_file(self._task_id, attr)

    def load_task_id(self, task_id):
        """ load task id 
        :rtype: None
        """
        self._task_id = task_id
        self._task_handle = zfused_api.task.Task(task_id)
        # self._restore()

        # self.base_widget.load_task_id(task_id)

        # load attrs
        _project_step_handle =  zfused_api.step.ProjectStep(self._task_handle.data()["ProjectStepId"])
        _attrs = _project_step_handle.output_attrs()
        self.attr_widget.load_attrs(_attrs)

        # if not _attrs:
        #     return
        # for _attr in _attrs:
        #     _attr_frame = QtWidgets.QFrame()
        #     _attr_layout = QtWidgets.QHBoxLayout(_attr_frame)
        #     _attr_layout.setSpacing(0)
        #     _attr_layout.setContentsMargins(2,2,2,2)
        #     _name_checkbox = QtWidgets.QCheckBox()
        #     _attr_layout.addWidget(_name_checkbox)
        #     _name_checkbox.setText(_attr["Name"])
        #     _name_checkbox.setChecked(True)
        #     _attr_layout.addStretch(True)
        #     self.attr_layout.addWidget(_attr_frame)

    def _load_attr(self, attr = {}):
        """
        """
        _widget = QtWidgets.QFrame()
        self.attr_tabwidget.addTab(_widget, attr["Name"])

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(5)
        _layout.setContentsMargins(0,0,0,0)

        _info_label = QtWidgets.QLabel()
        _info_label.setText(u"更新替换当前版本文件数据，不会产生新版本")
        _info_label.setMaximumHeight(40)
        _info_label.setStyleSheet("QLabel{background-color:#FF0000}")
        _layout.addWidget(_info_label)

        # asset widget
        self.asset_widget = AssetWidget()
        _layout.addWidget(self.asset_widget)

        # _layout.addStretch(True)

        # attr selected
        self.attr_widget = AttrWidget()
        _layout.addWidget(self.attr_widget)
        # _layout.addWidget(self.attr_widget)
        # self.attr_layout = QtWidgets.QVBoxLayout(self.attr_widget)
        # self.attr_layout.setSpacing(2)
        # self.attr_layout.setContentsMargins(2,2,2,2)

        # self.base_widget = basewidget.BaseWidget()
        # _layout.addWidget(self.base_widget)
        
        # upload widget
        self.upload_widget = QtWidgets.QFrame()
        _layout.addWidget(self.upload_widget)
        self.upload_widget.setObjectName("publish_widget")
        self.upload_layout = QtWidgets.QVBoxLayout(self.upload_widget)
        self.upload_layout.setSpacing(0)
        self.upload_layout.setContentsMargins(2,2,2,2)

        #  information widget
        self.info_widget = QtWidgets.QFrame()
        self.info_widget.setHidden(True)
        self.info_widget.setMaximumHeight(30)
        self.info_layout = QtWidgets.QHBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(0,0,0,0)
        self.info_layout.setSpacing(0)
        self.info_label = QtWidgets.QLabel()
        self.info_label.setMinimumHeight(30)
        self.info_label.setStyleSheet("QLabel{background-color:#220000}")
        self.info_label.setText(u"无缩略图")
        self.info_layout.addWidget(self.info_label)
        self.upload_layout.addWidget(self.info_widget)

        # #  push widget
        # self.publish_widget = QtWidgets.QFrame()
        # self.publish_layout = QtWidgets.QHBoxLayout(self.publish_widget)
        # self.publish_layout.setSpacing(0)
        # self.publish_layout.setContentsMargins(0,0,0,0)
        # self.publish_button = QtWidgets.QPushButton()
        # self.publish_button.setObjectName("publish_button")
        # self.publish_button.setMinimumSize(100,40)
        # self.publish_button.setIcon(QtGui.QIcon(resource.get("icons","publish.png")))
        # self.publish_button.setText(u"上传文件")
        # self.publish_layout.addStretch(True)
        # self.publish_layout.addWidget(self.publish_button)
        # self.upload_layout.addWidget(self.publish_widget)

        #  push widget
        self.publish_widget = QtWidgets.QFrame()
        self.upload_layout.addWidget(self.publish_widget)
        self.publish_layout = QtWidgets.QHBoxLayout(self.publish_widget)
        self.publish_layout.setSpacing(0)
        self.publish_layout.setContentsMargins(0,0,0,0)

        # sample widget
        self.sample_widget = SampleWidget()
        self.publish_layout.addWidget(self.sample_widget)

        self.publish_layout.addStretch(True)

        # upload button
        self.publish_button = QtWidgets.QPushButton()
        self.publish_button.setMinimumSize(100,40)
        self.publish_button.setObjectName("publish_button")
        self.publish_button.setIcon(QtGui.QIcon(resource.get("icons","publish.png")))
        self.publish_button.setText(u"上传文件")
        self.publish_layout.addWidget(self.publish_button)


class AssetWidget(QtWidgets.QFrame):
    selected_from_scene = QtCore.Signal()
    def __init__( self, parent = None ):
        super(AssetWidget, self).__init__(parent)

        self._build()

        self._asset_widgets = {}

        self.scene_selected_button.clicked.connect(self.selected_from_scene.emit)

    def get_assets(self):
        _assets = []
        for _widget, _asset in self._asset_widgets.items():
            if _widget.isChecked():
                _assets.append(_asset)
        return _assets

    def load_assets(self, assets):
        self._asset_widgets = {}
        # clear
        for i in range(self.group_layout.count()):
            self.group_layout.itemAt(i).widget().deleteLater()

        for _asset in assets:
            name = _asset.get('code')
            namesapce = _asset.get('namespace')
            rfn = _asset.get('rfn')
            _check_box = QtWidgets.QCheckBox(u'{} - {} - {}'.format(name,namesapce,rfn))
            _check_box.setObjectName(rfn)
            self._asset_widgets[_check_box] = _asset
            self.group_layout.addWidget(_check_box)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setAlignment(QtCore.Qt.AlignTop)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        #全选
        self.operation_frame = QtWidgets.QFrame()
        _layout.addWidget(self.operation_frame)
        self.operation_layout = QtWidgets.QHBoxLayout(self.operation_frame)
        self.operation_layout.setSpacing(4)
        self.operation_layout.setContentsMargins(0,0,0,0)
        self.all_title = QtWidgets.QLabel(u"资产列表")
        self.operation_layout.addWidget(self.all_title)
        self.operation_layout.addStretch(True)
        self.scene_selected_button = QtWidgets.QPushButton(u"场景选择定位")
        self.operation_layout.addWidget(self.scene_selected_button)
        self.scene_selected_button.setFixedSize(100,20)
        self.all_check_box = QtWidgets.QCheckBox(u'全选')
        self.all_check_box.stateChanged.connect(self.all_state)
        self.operation_layout.addWidget(self.all_check_box)

        self.scroll_widget = QtWidgets.QScrollArea()
        _layout.addWidget(self.scroll_widget)
        self.scroll_widget.setWidgetResizable(True)
        self.scroll_widget.setBackgroundRole(QtGui.QPalette.NoRole)
        self.scroll_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        self.contain_widget = QtWidgets.QFrame()
        self.scroll_widget.setWidget(self.contain_widget)
        self.contain_layout = QtWidgets.QVBoxLayout(self.contain_widget)
        self.contain_layout.setSpacing(0)
        self.contain_layout.setContentsMargins(0,0,0,0)
        self.group_box = QtWidgets.QGroupBox()
        self.contain_layout.addWidget(self.group_box)
        self.group_layout = QtWidgets.QVBoxLayout(self.group_box)
        self.group_layout.setSpacing(0)
        self.group_layout.setContentsMargins(0,0,0,0)
        self.group_layout.setAlignment(QtCore.Qt.AlignTop)
        self.contain_layout.addStretch(True)

    def all_state(self):
        all_boxs = self.group_box.findChildren(QtWidgets.QCheckBox)
        if self.all_check_box.isChecked() is True:
            for check in all_boxs:
                check.setChecked(True)
        else:
            for check in all_boxs:
                check.setChecked(False)



class AttrWidget(QtWidgets.QFrame):
    def __init__( self, parent = None ):
        super(AttrWidget, self).__init__(parent)

        self._build()

        self._attr_widgets = {}

    def get_attrs(self):
        _attrs = []
        for _widget, _attr in self._attr_widgets.items():
            if _widget.isChecked():
                _attrs.append(_attr)
        _attrs.sort(key = lambda _attr: _attr.get("Sort"))
        return _attrs

    def load_attrs(self, attrs):
        self._attr_widgets = {}
        # clear
        for i in range(self.contain_layout.count()):
            self.contain_layout.itemAt(i).widget().deleteLater()

        for _attr in attrs:
            name = _attr.name()
            code = _attr.code()
            _check_box = QtWidgets.QCheckBox(u'{} - {}'.format(name,code))
            _check_box.setChecked(True)
            self._attr_widgets[_check_box] = _attr
            self.contain_layout.addWidget(_check_box)

    def _all_state(self):
        _is_checked = self.all_check_box.isChecked()
        for _widget, _attr in self._attr_widgets.items():
            _widget.setChecked(_is_checked)

    def _build(self):

        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setAlignment(QtCore.Qt.AlignTop)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # 全选
        self.operation_frame = QtWidgets.QFrame()
        _layout.addWidget(self.operation_frame)
        self.operation_layout = QtWidgets.QHBoxLayout(self.operation_frame)
        self.operation_layout.setSpacing(0)
        self.operation_layout.setContentsMargins(0,0,0,0)
        self.all_title = QtWidgets.QLabel(u"输出列表")
        self.operation_layout.addWidget(self.all_title)
        self.operation_layout.addStretch(True)
        self.all_check_box = QtWidgets.QCheckBox(u'全选')
        self.all_check_box.setChecked(True)
        self.all_check_box.stateChanged.connect(self._all_state)
        self.operation_layout.addWidget(self.all_check_box)

        # self.scroll_widget = QtWidgets.QScrollArea()
        # _layout.addWidget(self.scroll_widget)
        # self.scroll_widget.setWidgetResizable(True)
        # self.scroll_widget.setBackgroundRole(QtGui.QPalette.NoRole)
        # self.scroll_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        self.contain_widget = QtWidgets.QFrame()
        _layout.addWidget(self.contain_widget)
        self.contain_layout = QtWidgets.QVBoxLayout(self.contain_widget)
        self.contain_layout.setSpacing(0)
        self.contain_layout.setContentsMargins(0,0,0,0)


class SampleWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(SampleWidget, self).__init__(parent)

        self.frame_group = QtWidgets.QButtonGroup()
        self.frame_group.setExclusive(True)

        self._build()
    
    def sample(self):
        _custom = self.custom_lineedit.text()
        if _custom:
            return float(_custom)
        return float(self.frame_group.checkedButton().text())

    def _build(self):
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(4)
        _layout.setContentsMargins(0,0,0,0)

        self.title_label = QtWidgets.QLabel(u"输出采样:")
        _layout.addWidget(self.title_label)

        self.one_checkbox = QtWidgets.QCheckBox("1.0")
        _layout.addWidget(self.one_checkbox)
        self.one_checkbox.setChecked(True)
        self.frame_group.addButton(self.one_checkbox)

        self.point_five_checkbox = QtWidgets.QCheckBox("0.5")
        _layout.addWidget(self.point_five_checkbox)
        self.frame_group.addButton(self.point_five_checkbox)

        self.point_one_checkbox = QtWidgets.QCheckBox("0.1")
        _layout.addWidget(self.point_one_checkbox)
        self.frame_group.addButton(self.point_one_checkbox)

        self.custom_lineedit = QtWidgets.QLineEdit()
        _layout.addWidget(self.custom_lineedit)
        self.custom_lineedit.setFixedWidth(50)
        self.custom_lineedit.setPlaceholderText(u"自定义")