# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import partial

from Qt import QtWidgets,QtGui,QtCore

import zfused_api

from zwidgets.widgets import dialog

from zfused_maya.core import record

from zfused_maya.ui.widgets import window


def set_company():
    """设置对应的公司
    """
    # get all company
    _company_dict = {}
    _companys = zfused_api.zFused.get("company")
    _company_names = []
    for _company in _companys:
        _company_dict[_company.get("Name")] = _company.get("Id")
        _company_names.append(_company.get("Name"))
    
class SetCompanyWidget(dialog.Dialog):
    def __init__(self, parent = None):
        super(SetCompanyWidget, self).__init__()
        self._build()

        self._company_dict = {}
        # self._company_name = []
        self._company_completer = None

    @staticmethod
    def set_company(parent):
        """ get user 
        rtype: zfused_api.user.User
        """
        dialog = SetCompanyWidget(parent)
        # dialog.user_list_widget.load(group_type, group_id)
        result = dialog.exec_()
        print(result)
        return (dialog.company(), result)

    def accept(self):
        # get company
        _company_text = self.company_lineedit.text()
        if _company_text not in self._company_dict.keys():
            self.set_tip(u"此公司名称不存在，请联系制片", -1)
            return False
        _company_id = self._company_dict[_company_text]
        record.write_company_id(_company_id)
        super(SetCompanyWidget, self).accept()

    def company(self):
        return record.current_company_id()

    def showEvent(self, event):
        # get all company
        self._company_dict = {}
        _companys = zfused_api.zFused.get("company")
        _company_names = []
        for _company in _companys:
            self._company_dict[_company.get("Name")] = _company.get("Id")
            _company_names.append(_company.get("Name"))
        self._company_completer = QtWidgets.QCompleter(_company_names)
        print(self._company_completer)
        # self._company_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._company_completer.setFilterMode(QtCore.Qt.MatchContains)
        self._company_completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.company_lineedit.setCompleter(self._company_completer)

    def _build(self):
        self.set_title(u"设置公司")
        self.resize(600, 300)

        self.company_widget = QtWidgets.QFrame()
        self.add_content_widget(self.company_widget)
        self.company_layout = QtWidgets.QVBoxLayout(self.company_widget)
        self.company_layout.setSpacing(14)

        self.description_label = QtWidgets.QLabel()
        self.description_label.setText(u"设置制作公司\n可输入公司简称,系统自动匹配\n例如:苏州优尼提传媒有限公司,可输入优尼提\n")
        self.description_label.setStyleSheet("QLabel{background-color:#EDEDED;color:#DD0000;text-align:center;font-size:14px;}")
        self.description_label.setAlignment(QtCore.Qt.AlignCenter)
        self.company_layout.addWidget(self.description_label)

        self.company_lineedit = QtWidgets.QLineEdit()
        self.company_layout.addWidget(self.company_lineedit)
        self.company_lineedit.setPlaceholderText(u"设置公司名称{例如:苏州优尼提传媒有限公司,可输入优尼提}")
        self.company_lineedit.setFixedHeight(40)

        self.company_layout.addStretch(True)
    

if __name__ == '__main__':
    ui = SetCompanyWidget.set_company(window._Window())
