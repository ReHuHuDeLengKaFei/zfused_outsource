# coding:utf-8
# --author-- lanhua.zhou

# pyside and qtpy
from Qt import QtGui,QtWidgets,QtCore


class ItemWidget(QtWidgets.QWidget):
    DEFAULT = "{background-color: rgb(239, 173, 3);}"
    RIGHT = "{background-color: rgb(0, 250, 0);}"
    ERROR = "{background-color: rgb(250, 0, 0);}"
    def __init__(self, name, check_command, clear_command = None, is_ignore = True):
        super(ItemWidget, self).__init__()
        
        self.name = name
        self.check_command = check_command
        self.clear_command = clear_command
        self.is_ignore = is_ignore

        self._build()
        
        self.info_button.clicked.connect(self._show_info)
        self.clear_button.clicked.connect(self.clear)
        self.listWidget.itemSelectionChanged.connect(self._select_item)

    def _show_info(self):
        """ 显示信息

        """
        if self.listWidget.isHidden():
            self.listWidget.setHidden(False)
        else:
            self.listWidget.setHidden(True)
    
    def clear(self):
        """ 是否需要保存？？？
        """
        if self.clear_command != None:
            exec(self.clear_command)
        # re check
        self.check()

    def check(self):
        # print(self.ignore_checkBox.isChecked())
        if self.ignore_checkBox.isChecked():
            self.infoWidget.setStyleSheet("QWidget%s"%self.RIGHT)
            self.show_button.setStyleSheet("QPushButton%s"%self.RIGHT)
            return True
        print(self.check_command)
        global _check_status,_check_info # = False,""
        exec(self.check_command, globals())
        print(_check_status,_check_info)
        if not _check_status:
            self.infoWidget.setStyleSheet("QWidget%s"%self.ERROR)
            self.show_button.setStyleSheet("QPushButton%s"%self.ERROR)
            items = _check_info.split("\n")[:]
            self.listWidget.clear()
            if len(items) == 1:
                self.listWidget.addItem(items[0])
            else:
                for item in items:
                    self.listWidget.addItem(item)
            return False
        else:
            self.infoWidget.setStyleSheet("QWidget%s"%self.RIGHT)
            self.show_button.setStyleSheet("QPushButton%s"%self.RIGHT)
            return True

    def _select_item(self):
        selName = self.listWidget.selectedItems()
        # if selName:
        try:
            import maya.cmds as cmds
            cmds.select(cl = 1)
            for name in selName:
                cmds.select(name.text(),add = 1)
        except:
            pass

    def _build(self):
        """ build itemwidget widget

        """
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(3,3,3,3)

        self.infoWidget = QtWidgets.QFrame()
        _layout.addWidget(self.infoWidget)
        self.infoWidget.setMaximumHeight(1)
        self.infoWidget.setMinimumHeight(1)
        self.infoWidget.setStyleSheet("QFrame%s"%self.DEFAULT)

        self.head_widget = QtWidgets.QWidget()
        _layout.addWidget(self.head_widget)
        self.head_widget.setMaximumHeight(25)
        self.head_widget.setMaximumHeight(25)
        self.head_layout = QtWidgets.QHBoxLayout(self.head_widget)
        self.head_layout.setContentsMargins(0,0,0,0)

        self.ignore_layout = QtWidgets.QVBoxLayout()
        self.head_layout.addLayout(self.ignore_layout)
        self.ignore_checkBox = QtWidgets.QCheckBox()
        self.ignore_checkBox.setMaximumSize(100, 25)
        self.ignore_checkBox.setMinimumSize(100, 25)
        #self.ignore_checkBox.setStyleSheet("QCheckBox{background-color: rgb(60, 60, 60, 0);}")
        self.ignore_checkBox.setText(u"忽略")
        self.ignore_layout.addWidget(self.ignore_checkBox)
        #if is_ignore
        if self.is_ignore:
            self.ignore_checkBox.setEnabled(True)
        else:
            print("is ignore %s"%self.is_ignore)
            self.ignore_checkBox.setEnabled(False)
        self.ignore_checkBox.update()

        self.title_label = QtWidgets.QLabel()
        self.head_layout.addWidget(self.title_label)
        self.title_label.setStyleSheet("QLabel{background-color: rgb(60, 60, 60, 0);}")
        self.title_label.setText(self.name)

        self.show_button = QtWidgets.QPushButton()
        self.head_layout.addWidget(self.show_button)
        self.show_button.setStyleSheet("QPushButton%s"%self.DEFAULT)
        self.show_button.setMinimumSize(10,10)
        self.show_button.setMaximumSize(10,10)

        self.info_button = QtWidgets.QPushButton()
        self.head_layout.addWidget(self.info_button)
        self.info_button.setMaximumSize(80, 25)
        self.info_button.setMinimumSize(80, 25)
        self.info_button.setText(u"显示信息")

        self.clear_button = QtWidgets.QPushButton()
        self.head_layout.addWidget(self.clear_button)
        self.clear_button.setMaximumSize(50, 25)
        self.clear_button.setMinimumSize(50, 25)
        self.clear_button.setText(u"修复")
        if not self.clear_command:
            self.clear_button.setEnabled(False)
            self.clear_button.hide()
        else:
            self.clear_button.showNormal()

        self.listWidget = QtWidgets.QListWidget()
        _layout.addWidget(self.listWidget)
        self.listWidget.setFrameShape(QtWidgets.QListWidget.NoFrame)
        self.listWidget.setStyleSheet("background:rgb(0,0,0)")
        self.listWidget.setHidden(True)

        
        
        