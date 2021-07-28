# coding:utf-8
# --author-- lanhua.zhou

""" 用户widget """

from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import button

logger = logging.getLogger(__name__)


class UserButton(QtWidgets.QPushButton):
    def __init__(self, user_id = 0, parent=None):
        super(UserButton, self).__init__(parent)
        
        self._user_id = user_id

        if not self._user_id:
            self.setText(u"无配备人员")

    def load_user_id(self, user_id):
        self.setText("")
        self._user_id = user_id
        self.repaint()

    def paintEvent(self, event):
        super(UserButton, self).paintEvent(event)
        if not self._user_id:
            return
        _user_handle = zfused_api.user.User(self._user_id)
        _rect = self.rect()
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        
        _font = QtGui.QFont("Microsoft YaHei UI")
        _font.setPixelSize(14)
        _font.setBold(True)
        painter.setFont(_font)
        _pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 1)
        painter.setPen(_pen)

        fm = QtGui.QFontMetrics(_font)
        _text_width = fm.width( _user_handle.name() ) + 10
        # self.setMinimumWidth(_text_width)
        # self.setMaximumWidth(_text_width)

        # 绘制名称
        painter.drawText(_rect, QtCore.Qt.AlignCenter, _user_handle.name())
            
        painter.end()


class UserWidget(QtWidgets.QFrame):
    REMOVE_USER = QtCore.Signal(int)
    def __init__(self, parent = None):
        super(UserWidget, self).__init__(parent)
        self.__build()

        self.__user_id = 0

    #     self.__close_button.clicked.connect(self._remove_user)

    # def _remove_user(self):
    #     self.REMOVE_USER.emit(self.__user_id)

    def user_id(self):
        """ return user id
        """
        return self.__user_id

    def load_user_id(self, user_id):
        """ load user
        """
        self.__user_id = user_id
        self.__user_button.load_user_id(user_id)

    def __build(self):
        """ build user widget
        """
        self.setMinimumSize(100, 25)
        self.setMaximumSize(100, 25)

        __layout = QtWidgets.QHBoxLayout(self)
        __layout.setSpacing(2)
        __layout.setContentsMargins(0,0,0,0)

        # user button
        self.__user_button = UserButton()
        __layout.addWidget(self.__user_button) 

        # # close button
        # self.__close_button = button.IconButton( self, 
        #                                          resource.get("icons", "close.png"),
        #                                          resource.get("icons", "close_hover.png"),
        #                                          resource.get("icons", "close_pressed.png") )
        # self.__close_button.setMaximumSize(25, 25)
        # __layout.addWidget(self.__close_button)