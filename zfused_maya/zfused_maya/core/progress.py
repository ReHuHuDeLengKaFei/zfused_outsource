 # coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import wraps,partial

import sys
import os
import traceback
import logging
# from multiprocessing import Process

from Qt import QtWidgets, QtGui, QtCore

import maya.OpenMaya as om

from zwidgets.widgets import progress_bar

from . import tomaya


logger = logging.getLogger(__name__)


def set_range(mini, maxi):
    progress_bar.set_range(mini, maxi)
    QtWidgets.QApplication.processEvents()

def set_label_text(text):
    progress_bar.set_label_text(text)
    QtWidgets.QApplication.processEvents()

def set_value(value):
    progress_bar.set_value(value)
    QtWidgets.QApplication.processEvents()


def set_sub_range(mini, maxi):
    progress_bar.set_sub_range(mini, maxi)
    QtWidgets.QApplication.processEvents()

def set_sub_label_text(text):
    progress_bar.set_sub_label_text(text)
    QtWidgets.QApplication.processEvents()

def set_sub_value(value):
    progress_bar.set_sub_value(value)
    QtWidgets.QApplication.processEvents()


def catchOutput(msg, *args):
    window.set_script_text(msg)
    with open('D:/maya.log', 'a') as f:
        f.write("Caught: %s\n" % msg)


from zfused_maya.ui.widgets import window


# class OutputWrapper(QtCore.QObject):
#     outputWritten = QtCore.Signal(object, object)

#     def __init__(self, parent, stdout=True):
#         super().__init__(parent)
#         if stdout:
#             self._stream = sys.stdout
#             sys.stdout = self
#         else:
#             self._stream = sys.stderr
#             sys.stderr = self
#         self._stdout = stdout

#     def write(self, text):
#         self._stream.write(text)
#         self.outputWritten.emit(text, self._stdout)

#     def __getattr__(self, name):
#         return getattr(self._stream, name)

#     def __del__(self):
#         try:
#             if self._stdout:
#                 sys.stdout = self._stream
#             else:
#                 sys.stderr = self._stream
#         except AttributeError:
#             pass


class CatchOutput(window._Window):
    def __init__(self, title, parent = None):
        super(CatchOutput, self).__init__()
        self._title = title
        self._build()

        self._catchOutput_id = 0

    def start(self):
        self.script_textedit.clear()
        self.progress_bar.start()
        self.showNormal()
        self._catchOutput_id = om.MCommandMessage.addCommandOutputCallback(self.set_script_text)

    def stop(self):
        self.progress_bar.stop()
        try:
            om.MCommandMessage.removeCallback(self._catchOutput_id)
        except:
            pass
        
    def close(self):
        self.stop()
        super(CatchOutput, self).close()

    def set_script_text(self, text, *args):
        if not text or text == "\n":
            return
        if not text.endswith("\n"):
            text += "\n"
        cursor = self.script_textedit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText("--std out: " + text)
        self.script_textedit.setTextCursor(cursor)
        self.script_textedit.ensureCursorVisible()

    def _build(self):
        self.set_title(self._title)
        self.resize(800,600)
        self.contain_widget = QtWidgets.QFrame()
        self.contain_layout = QtWidgets.QVBoxLayout(self.contain_widget)

        self.progress_bar = progress_bar.ProgressBar(self._title)
        self.contain_layout.addWidget(self.progress_bar)

        self.script_textedit = QtWidgets.QTextEdit(self)
        self.contain_layout.addWidget(self.script_textedit)


        self.set_central_widget(self.contain_widget)


def progress(title):
    def _progress( func ):
        
        __progress = CatchOutput(title)
        # catchOutput_id = om.MCommandMessage.addCommandOutputCallback(__progress.set_script_text)
        @wraps(func)
        def wrap( *args, **kwargs ):
            QtWidgets.QApplication.processEvents()
            __progress.start()
            QtWidgets.QApplication.processEvents()
            try:
                func( *args, **kwargs )
                __progress.close()
            except Exception as e:
                _info = traceback.format_exc()
                logger.error(_info)
                traceback.print_exc()
            finally:
                __progress.stop()
                # om.MCommandMessage.removeCallback(catchOutput_id)
        return wrap
    
    return _progress


def progress_(title):
    def _progress( func ):
        
        __progress = progress_bar.ProgressBar(title, tomaya.GetMayaMainWindowPoint())
        # catchOutput_id = om.MCommandMessage.addCommandOutputCallback(__progress.set_script_text)
        @wraps(func)
        def wrap( *args, **kwargs ):
            QtWidgets.QApplication.processEvents()
            __progress.start()
            QtWidgets.QApplication.processEvents()
            try:
                func( *args, **kwargs )
            except Exception as e:
                _info = traceback.format_exc()
                logger.error(_info)
                traceback.print_exc()
            finally:
                __progress.stop()
                # om.MCommandMessage.removeCallback(catchOutput_id)
        return wrap
    
    return _progress