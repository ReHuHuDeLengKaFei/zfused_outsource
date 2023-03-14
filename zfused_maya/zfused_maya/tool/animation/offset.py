# coding:utf-8
# --author-- lanhua.zhou

import maya.cmds as cmds

from Qt import QtWidgets

from zwidgets.widgets import lineedit

from zfused_maya.ui.widgets import window


class offset(window._Window):
    def __init__(self, parent = None):
        super(offset, self).__init__(parent)
        self._build()

        self.get_obj_button.clicked.connect(self._get_obj)
        self.new_sel_objs_button.clicked.connect(self._sel_to_objs)
        self.ani_ctl_button.clicked.connect(self._get_ani_ctls)
        self.remove_button.clicked.connect(self._remove)
        
        self.to_obj_listwidget.itemClicked.connect(self._sel_items)

        self.do_button.clicked.connect(self._do)

    def _do(self):
        # get offset object
        _obj = self.obj_lineedit.text()
        _offset_trans = cmds.xform(_obj, q = True, ws = True, rp = True)

        _count = self.to_obj_listwidget.count()
        # _items = self.to_obj_listwidget.items()
        _remove_items = []
        for _row in range(_count):
            print(_row)
        # for _item in _items:
            _item = self.to_obj_listwidget.item(_row)
            # _row = self.to_obj_listwidget.row(_item)
            _to_obj = _item.text()
            _to_obj_trans = cmds.getAttr("{}.translate".format(_to_obj))[0]
            print(_to_obj_trans)
            try:
                #print("{}.translateX".format(_to_obj), _to_obj_trans[0] - _offset_trans[0])
                cmds.setAttr("{}.translateX".format(_to_obj), _to_obj_trans[0] - _offset_trans[0] )
                cmds.setAttr("{}.translateY".format(_to_obj), _to_obj_trans[1] - _offset_trans[1] )
                cmds.setAttr("{}.translateZ".format(_to_obj), _to_obj_trans[2] - _offset_trans[2] )
                # self.to_obj_listwidget.takeItem(_row)
                _remove_items.append(_item)

                try:
                    # add attr
                    cmds.addAttr(_to_obj, ln = "is_offset", at = "double3")
                    cmds.addAttr(_to_obj, ln = "is_offsetX", at = "double", p = "is_offset")
                    cmds.addAttr(_to_obj, ln = "is_offsetY", at = "double", p = "is_offset")
                    cmds.addAttr(_to_obj, ln = "is_offsetZ", at = "double", p = "is_offset")
                except:
                    pass
                
                cmds.setAttr("{}.is_offset".format(_to_obj), _offset_trans[0],_offset_trans[1],_offset_trans[2], type = "double3")

                # setAttr -e-keyable true |char|boy08:Group|boy08:rig|boy08:master.is_offset;
                cmds.setAttr("{}.is_offset".format(_to_obj), e = True, k = True)
                cmds.setAttr("{}.is_offsetX".format(_to_obj), e = True, k = True)
                cmds.setAttr("{}.is_offsetY".format(_to_obj), e = True, k = True)
                cmds.setAttr("{}.is_offsetZ".format(_to_obj), e = True, k = True)

            except Exception as e:
                print(e)
                cmds.setAttr("{}.translateX".format(_to_obj), _to_obj_trans[0] )
                cmds.setAttr("{}.translateY".format(_to_obj), _to_obj_trans[1] )
                cmds.setAttr("{}.translateZ".format(_to_obj), _to_obj_trans[2] )
        if _remove_items:
            for _item in _remove_items:
                _row = self.to_obj_listwidget.row(_item)
                self.to_obj_listwidget.takeItem(_row)

    def _get_obj(self):
        #
        ls = cmds.ls(sl = True)
        if ls:
            self.obj_lineedit.setText(ls[0])

    def _sel_to_objs(self):
        ls = cmds.ls(sl = True)
        if ls:
            for i in ls:
                self.to_obj_listwidget.addItem(i)

    def _get_ani_ctls(self):
        _reference_ctls = []
        _references = cmds.ls(rf = True)
        if _references:
            for _reference in _references:
                print(_reference)
                try:
                    _namespace = cmds.referenceQuery(_reference, ns = True)
                except:
                    continue
                _main_ctl = "{}:main".format(_namespace)
                if cmds.objExists(_main_ctl):
                    _parent = cmds.listRelatives(_main_ctl, parent = True)[0]
                    self.to_obj_listwidget.addItem(_parent)
                _main_ctl = "{}:Main".format(_namespace)
                if cmds.objExists(_main_ctl):
                    _parent = cmds.listRelatives(_main_ctl, parent = True)[0]
                    self.to_obj_listwidget.addItem(_parent)

    def _remove(self):
        items = self.to_obj_listwidget.selectedItems()
        for _item in items:
            col = self.to_obj_listwidget.row(_item)
            self.to_obj_listwidget.takeItem(col)

    def _sel_items(self):
        _objs = []
        items = self.to_obj_listwidget.selectedItems()
        for _item in items:
            _text = _item.text()
            _objs.append(_text)
        cmds.select(_objs, r = True)

    def _build(self):
        self.resize(600,400)
        self.set_title_name(u"偏移数据")
        
        # build offset object
        self.obj_frame = QtWidgets.QFrame()
        self.set_central_widget(self.obj_frame)
        self.obj_layout = QtWidgets.QHBoxLayout(self.obj_frame)
        self.obj_layout.setSpacing(2)
        self.obj_layout.setContentsMargins(2,2,2,2)
        self.obj_name_button = QtWidgets.QPushButton()
        self.obj_name_button.setFixedSize(100,30)
        self.obj_layout.addWidget(self.obj_name_button)
        self.obj_name_button.setText(u"偏移参考:")
        self.obj_name_button.setObjectName("title_button")
        self.obj_lineedit = lineedit.LineEdit()
        self.obj_layout.addWidget(self.obj_lineedit)
        self.obj_lineedit.setFixedHeight(30)
        self.get_obj_button = QtWidgets.QPushButton()
        self.get_obj_button.setFixedSize(100,25)
        self.obj_layout.addWidget(self.get_obj_button)
        self.get_obj_button.setText(u"提取偏移参考")
        self.get_obj_button.setFixedHeight(30)

        # to offset objects
        self.to_obj_frame = QtWidgets.QFrame()
        self.set_central_widget(self.to_obj_frame)
        self.to_obj_layout = QtWidgets.QHBoxLayout(self.to_obj_frame)
        self.to_obj_layout.setSpacing(2)
        self.to_obj_layout.setContentsMargins(2,2,2,2)
        self.to_obj_listwidget = QtWidgets.QListWidget()
        self.to_obj_layout.addWidget(self.to_obj_listwidget)
        self.to_obj_listwidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # operation
        self.to_operation_widget = QtWidgets.QFrame()
        self.to_obj_layout.addWidget(self.to_operation_widget)
        self.to_operation_layout = QtWidgets.QVBoxLayout(self.to_operation_widget)
        self.to_operation_layout.setSpacing(2)
        self.to_operation_layout.setContentsMargins(0,2,0,2)
        self.new_sel_objs_button = QtWidgets.QPushButton()
        self.new_sel_objs_button.setFixedSize(100,25)
        self.to_operation_layout.addWidget(self.new_sel_objs_button)
        self.new_sel_objs_button.setText(u"选择物体")
        self.ani_ctl_button = QtWidgets.QPushButton()
        self.ani_ctl_button.setFixedSize(100,25)
        self.to_operation_layout.addWidget(self.ani_ctl_button)
        self.ani_ctl_button.setText(u"提取绑定")
        self.to_operation_layout.addStretch(True)
        self.remove_button = QtWidgets.QPushButton()
        self.remove_button.setFixedSize(100,25)
        self.remove_button.setText(u"移除")
        self.to_operation_layout.addWidget(self.remove_button)

        # offset frame
        self.operation_widget = QtWidgets.QFrame()
        self.set_tail_widget(self.operation_widget)
        self.operation_layout = QtWidgets.QHBoxLayout(self.operation_widget)
        self.operation_layout.setSpacing(2)
        self.operation_layout.setContentsMargins(2,2,2,2)
        self.error_label = QtWidgets.QLabel()
        self.error_label.setStyleSheet("QLabel{background-color:transparent;color:#FF0000}")
        self.operation_layout.addWidget(self.error_label)
        self.operation_layout.addStretch(True)
        self.do_button = QtWidgets.QPushButton()
        self.do_button.setFixedSize(200,40)
        self.do_button.setText(u"处理偏移")
        self.operation_layout.addWidget(self.do_button)




if __name__ == "__main__":
    offset()