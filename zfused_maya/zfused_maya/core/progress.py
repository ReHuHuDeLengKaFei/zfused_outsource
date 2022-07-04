 # coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import wraps

import os
import traceback
import logging
# from multiprocessing import Process

from Qt import QtWidgets, QtGui, QtCore

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


def progress(title):
    def _progress( func ):
        __progress = progress_bar.ProgressBar(title, tomaya.GetMayaMainWindowPoint())
        @wraps(func)
        def wrap( *args, **kwargs ):
            QtWidgets.QApplication.processEvents()
            __progress.start()
            QtWidgets.QApplication.processEvents()
            try:
                func( *args, **kwargs )
            except Exception as e:
                logger.warning(e)
                traceback.print_exc()
            finally:
                __progress.stop()
        return wrap
    
    return _progress