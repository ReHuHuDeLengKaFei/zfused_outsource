#coding:utf-8
#--author-- lanhua.zhou

#pyside and pyside2
from PySide2 import QtGui,QtWidgets,QtCore

import zfused_maya.interface.tomaya as tomaya


class ItemWidget(QtWidgets.QWidget):
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
            self.clear_command()
        #保存当前文件
        #-----获取文件格式
        import maya.cmds as cmds
        _type = cmds.file(q = True, type = True)[0]
        #-----保存文件
        cmds.file(save = True, options = "v=0;", f = True, type = _type)
        self.check()

    # WBLadd
    def check(self):
        if self.ignoreCheckBox.isChecked():
            self.infoWidget.setStyleSheet("QWidget%s"%self.RIGHT)
            self.showButton.setStyleSheet("QPushButton%s"%self.RIGHT)
            return True
        value,info = self.check_command()
        if not value:
            self.infoWidget.setStyleSheet("QWidget%s"%self.ERROR)
            self.showButton.setStyleSheet("QPushButton%s"%self.ERROR)
            # self.infoLineEdit.setText(info)
            items = info.split("\n")[:]
            self.listWidget.clear()
            if len(items) == 1:
                self.listWidget.addItem(items[0])
            else:
                # for index in xrange(1,len(items)):
                #     items[index] = items[index].split(":")[-1]
                for item in items:
                    self.listWidget.addItem(item)
            return False
        else:
            self.infoWidget.setStyleSheet("QWidget%s"%self.RIGHT)
            self.showButton.setStyleSheet("QPushButton%s"%self.RIGHT)
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
        # else:
        #     self.listWidget.clearSelection()

    def _build(self):
        """ build itemwidget widget

        """
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(3,3,3,3)

        self.infoWidget = QtWidgets.QFrame()
        self.infoWidget.setMaximumHeight(1)
        self.infoWidget.setMinimumHeight(1)
        self.infoWidget.setStyleSheet("QFrame%s"%self.RIGHT)

        headWidget = QtWidgets.QWidget()
        headWidget.setMaximumHeight(25)
        headWidget.setMaximumHeight(25)
        headLayout = QtWidgets.QHBoxLayout(headWidget)
        headLayout.setContentsMargins(0,0,0,0)

        ignoreLayout = QtWidgets.QVBoxLayout()
        self.ignoreCheckBox = QtWidgets.QCheckBox()
        self.ignoreCheckBox.setMaximumSize(100, 25)
        self.ignoreCheckBox.setMinimumSize(100, 25)
        #self.ignoreCheckBox.setStyleSheet("QCheckBox{background-color: rgb(60, 60, 60, 0);}")
        self.ignoreCheckBox.setText(u"忽略")
        ignoreLayout.addWidget(self.ignoreCheckBox)
        #if is_ignore
        if self.is_ignore:
            self.ignoreCheckBox.setEnabled(True)
        else:
            print "is ignore %s"%self.is_ignore
            self.ignoreCheckBox.setEnabled(False)
        self.ignoreCheckBox.update()

        titleLabel = QtWidgets.QLabel()
        titleLabel.setStyleSheet("QLabel{background-color: rgb(60, 60, 60, 0);}")
        titleLabel.setText(self.name)

        self.showButton = QtWidgets.QPushButton()
        self.showButton.setStyleSheet("QPushButton%s"%self.RIGHT)
        self.showButton.setMinimumSize(10,10)
        self.showButton.setMaximumSize(10,10)

        self.info_button = QtWidgets.QPushButton()
        self.info_button.setMaximumSize(80, 25)
        self.info_button.setMinimumSize(80, 25)
        self.info_button.setText(u"显示信息")

        self.clear_button = QtWidgets.QPushButton()
        self.clear_button.setMaximumSize(50, 25)
        self.clear_button.setMinimumSize(50, 25)
        self.clear_button.setText(u"清除")
        if self.clear_command == None:
            self.clear_button.setEnabled(False)

        headLayout.addWidget(self.showButton)
        headLayout.addLayout(ignoreLayout)
        headLayout.addWidget(titleLabel)
        headLayout.addWidget(self.info_button)
        headLayout.addWidget(self.clear_button)

        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setFrameShape(QtWidgets.QListWidget.NoFrame)
        self.listWidget.setStyleSheet("background:rgb(0,0,0)")
        self.listWidget.setHidden(True)

        # self.infoLineEdit = QtGui.QTextEdit()
        # self.infoLineEdit.setStyleSheet("QLabel{background-color: rgb(160, 60, 60, 60);}")
        # self.infoLineEdit.setHidden(True)

        #_layout.addWidget(self.infoWidget)
        _layout.addWidget(headWidget)
        _layout.addWidget(self.listWidget)