# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import lineedit

from .tasklistwidget import listitemdelegate, listview, listmodel

from . import taskpanelwidget


class MyTaskWidget(QtWidgets.QFrame):
    received = QtCore.Signal(str, int, list)
    published = QtCore.Signal(int, dict, dict)

    opened = QtCore.Signal(str)
    task_selected = QtCore.Signal(int)
    refreshed = QtCore.Signal()
    def __init__(self):
        super(MyTaskWidget, self).__init__()
        self.tab_dict = {}

        self._build()

        self.task_list_frame.task_selected.connect(self._task_list_to_panel)
        self.task_list_frame.task_selected.connect(self.task_selected.emit)
        self.task_list_frame.refreshed.connect(self.refreshed.emit)
        self.task_panel_frame.task_list_show.connect(self._task_panel_to_list)

        self.task_panel_frame.received.connect(self.received.emit)
        self.task_panel_frame.published.connect(self.published.emit)
        self.task_panel_frame.opened.connect(self.opened.emit)

    def load_task_id(self, task_id):
        self.task_panel_frame.load_task_id(task_id)

    def load_tasks(self, tasks):
        self.task_list_frame.load_tasks(tasks)

    def _task_panel_to_list(self):
        """ task panel to task list widget
        :rtype: None
        """
        self.tab_widget.setCurrentWidget(self.task_list_frame)

    def _task_list_to_panel(self, task_id):
        """ task list to task panel widget
        :rtype: None
        """
        self.task_panel_frame.load_task_id(task_id)
        self.tab_widget.setCurrentWidget(self.task_panel_frame)

    def set_active_tab(self, tabname):
        self.tab_widget.setCurrentWidget(self.tab_dict[tabname])

    def active_tabname(self):
        _index =  self.tab_widget.currentIndex()
        return self.tab_widget.tabText(_index)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # scroll widget
        self.scroll_widget = QtWidgets.QScrollArea()
        _layout.addWidget(self.scroll_widget)

        self.scroll_widget.setWidgetResizable(True)
        self.scroll_widget.setBackgroundRole(QtGui.QPalette.NoRole)

        # tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        self.scroll_widget.setWidget(self.tab_widget)
        self.tab_widget.tabBar().hide()

        self.task_list_frame = TaskListFrame(self.tab_widget)
        self.task_panel_frame = TaskPanelFrame(self.tab_widget)
        self.tab_widget.addTab(self.task_list_frame, "task list")
        self.tab_dict["task list"] = self.task_list_frame
        self.tab_widget.addTab(self.task_panel_frame, "task panel")
        self.tab_dict["task panel"] = self.task_panel_frame

        #
        self.set_active_tab("task list")


# task list frame
class TaskListFrame(QtWidgets.QFrame):
    task_selected = QtCore.Signal(int)
    refreshed = QtCore.Signal()
    def __init__(self, parent=None):
        """初始化
        """
        super(TaskListFrame, self).__init__(parent)
        self._build()

        self._tasks = []

        self._filter_active_status(True)

        self.refresh_button.clicked.connect(self.refreshed.emit)
        self.search_line.search_clicked.connect(self._search_tasks)
        self.working_checkbox.stateChanged.connect(self._filter_active_status)
        self.task_listwidget.doubleClicked.connect(self._set_task)

    def _set_task(self, index):
        _task_id = index.data()["Id"]
        # _ui_record = record.Interface()
        # _ui_record.write("current_task_id", _task_id)
        self.task_selected.emit(_task_id)

    # def _refresh(self):
    #     self.load_tasks(self._tasks)

    def load_tasks(self, tasks):
        self._tasks = tasks
        model = listmodel.ListModel(tasks, self.task_listwidget)
        self.task_proxy_model.setSourceModel(model)

    def _filter_active_status(self, _v):
        """过滤不是激活中的任务
        """
        if _v:
            _ids = zfused_api.status.working_status_ids()
        else:
            _ids = []
        self.task_proxy_model.filter_status(_ids)

        return None

    def _search_tasks(self):
        """搜索任务
        """
        #get search text
        text = self.search_line.text()
        self.task_proxy_model.search(text)
        self.task_proxy_model.invalidateFilter()

        return None

    def _build(self):
        """构建界面
        """
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(2)
        self.setObjectName("widget")

        # search widget
        self.search_widget = QtWidgets.QFrame()
        _layout.addWidget(self.search_widget)
        self.search_widget.setObjectName("search_widget")
        self.search_layout = QtWidgets.QHBoxLayout(self.search_widget)
        self.search_layout.setSpacing(0)
        self.search_layout.setContentsMargins(2, 2, 2, 2)
        #  search line
        self.search_line = lineedit.SearchLineEdit()
        self.search_line.setMinimumWidth(200)
        self.search_line.setMinimumHeight(25)
        self.search_line.setObjectName("search_line")
        self.search_layout.addWidget(self.search_line)
        self.search_line.set_tip(u"关键字搜索,摁enter搜索") 
        #  refresh button
        self.search_layout.addStretch(True)
        self.refresh_button = QtWidgets.QPushButton()
        self.search_layout.addWidget(self.refresh_button)
        self.refresh_button.setIcon(QtGui.QIcon(resource.get("icons","refresh.png")))

        # filter widget
        self.filter_widget = QtWidgets.QFrame()
        _layout.addWidget(self.filter_widget)
        self.filter_widget.setObjectName("filter_widget")
        self.filter_layout = QtWidgets.QHBoxLayout(self.filter_widget)
        self.filter_layout.setSpacing(0)
        self.filter_layout.setContentsMargins(2, 2, 2, 2)
        #  working status
        self.working_checkbox = QtWidgets.QCheckBox()
        self.working_checkbox.setChecked(True)
        self.working_checkbox.setMinimumHeight(25)
        self.working_checkbox.setObjectName("working_checkbox")
        self.filter_layout.addWidget(self.working_checkbox)
        self.working_checkbox.setText(u"只显示制作中任务")
        self.filter_layout.addStretch(True)

        # task list widget
        self.task_listwidget = listview.ListView()
        self.task_listwidget.setViewMode(QtWidgets.QListView.ListMode)
        _layout.addWidget(self.task_listwidget)
        self.task_listwidget.setObjectName("task_listwidget")
        self.task_proxy_model = listmodel.ListFilterProxyModel()
        self.task_listwidget.setModel(self.task_proxy_model)
        self.task_listwidget.setItemDelegate(listitemdelegate.ListItemDelegate(self.task_listwidget))



# task panel frame
class TaskPanelFrame(QtWidgets.QFrame):
    task_list_show = QtCore.Signal()
    received = QtCore.Signal(str, int)
    published = QtCore.Signal(str, int, dict)
    opened = QtCore.Signal(str)
    def __init__(self, parent = None):
        super(TaskPanelFrame, self).__init__(parent)
        self._build()

        self._task_id = 0

        self.task_list_button.clicked.connect(self._task_list_show)
        self.refresh_button.clicked.connect(self._reload)
        # self.task_panel_widget.publish_over.connect(self._reload)

        self.task_panel_widget.received.connect(self.received.emit)
        self.task_panel_widget.published.connect(self.published.emit)
        self.task_panel_widget.opened.connect(self.opened.emit)


    def _reload(self):
        self.load_task_id(self._task_id)

    @zfused_api.reset
    def load_task_id(self, task_id):
        self._task_id = task_id
        self.task_panel_widget.load_task_id(task_id)

    def _task_list_show(self):
        self.task_list_show.emit()

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(0,0,0,0)

        # head widget
        self.head_widget = QtWidgets.QFrame()
        self.head_widget.setObjectName("head_widget")
        self.head_layout = QtWidgets.QHBoxLayout(self.head_widget)
        self.head_layout.setSpacing(0)
        self.head_layout.setContentsMargins(2,2,2,2)
        #  task list home
        self.task_list_button = QtWidgets.QPushButton()
        self.task_list_button.setMinimumHeight(25)
        self.task_list_button.setIcon(QtGui.QIcon(resource.get("icons","home.png")))
        self.head_layout.addWidget(self.task_list_button)
        self.head_layout.addStretch(True)
        #  task refresh button
        self.refresh_button = QtWidgets.QPushButton()
        self.refresh_button.setIcon(QtGui.QIcon(resource.get("icons","refresh.png")))
        self.head_layout.addWidget(self.refresh_button)

        # task widget
        self.task_widget = QtWidgets.QFrame()
        self.task_layout = QtWidgets.QVBoxLayout(self.task_widget)
        self.task_layout.setSpacing(0)
        self.task_layout.setContentsMargins(2,2,2,2)
        
        #  task panel widget
        self.task_panel_widget = taskpanelwidget.TaskPanelWidget()
        self.task_layout.addWidget(self.task_panel_widget)

        _layout.addWidget(self.head_widget)
        _layout.addWidget(self.task_widget)
