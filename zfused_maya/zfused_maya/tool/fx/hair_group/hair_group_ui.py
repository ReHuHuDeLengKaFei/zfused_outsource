# coding:utf-8
# --author-- lanhua.zhou

from Qt import QtWidgets

from zfused_maya.ui.widgets import window

from . import create_group


class Window(window._Window):
    def __init__(self, parent = None):
        super(Window, self).__init__(parent)

        self._build()   

        self.group_button.clicked.connect(self._create_group)

    def _create_group(self):
        create_group.create_group()
    
    def _build(self):
        self.resize(300,300)
        self.set_title(u"毛发打组")

        self.content_widget = QtWidgets.QFrame()
        self.set_central_widget(self.content_widget)
        self.content_layout = QtWidgets.QHBoxLayout(self.content_widget)
        
        self.group_button = QtWidgets.QPushButton(u"创建毛发组")
        self.content_layout.addWidget(self.group_button)
        self.group_button.setFixedHeight(40)
