# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from collections import defaultdict

import time
import threading
import requests

from Qt import QtGui, QtCore

httpsession = requests.session()


class ThumbnailPixmapThread(QtCore.QObject):
    cached = QtCore.Signal(str)
    stop_signal = QtCore.Signal()
    def __init__(self):
        super(ThumbnailPixmapThread, self).__init__()
        self._count = 0
        
        self._sleep_time = 0

        self._handle_pool = []

        self._cmd_pool = []

    def get(self, handle, cmd = None):
        self._handle_pool.append( handle )
        self._cmd_pool.append( cmd )

    def analyze(self):
        self._count += 1
        while True:
            if self._handle_pool:
                for _index, _handle in enumerate(self._handle_pool):
                    _object = _handle.object()
                    _id = _handle.id()
                    _object_id = "{}:{}".format(_object, _id)
                    _thumbnail = _handle.get_thumbnail()
                    try:
                        if _thumbnail:
                            if _thumbnail.startswith("http:"):
                                req = httpsession.get(_thumbnail)
                                _pixmap = QtGui.QPixmap()
                                _pixmap.loadFromData(req.content)
                            else:
                                _pixmap = QtGui.QPixmap(_thumbnail)
                        else:
                            _pixmap = None
                    except:
                        _pixmap = None
                    _ThumbnailCache.THUMBNAIL_PATH_CACHE[_object_id] = _thumbnail
                    _ThumbnailCache.PIXMAP_CACHE[_object_id] = _pixmap
                    self.cached.emit(_object_id)
                    self._handle_pool.pop(_index)
                    if self._cmd_pool[_index]:
                        try:
                            self._cmd_pool[_index]()
                        except Exception as e:
                            print(e)
                    self._cmd_pool.pop(_index)
                self._sleep_time = 0
            else:
                self._sleep_time = 0.1
            self.stop_signal.emit()
            time.sleep(self._sleep_time)


class _ThumbnailCache(QtCore.QObject):
    cached = QtCore.Signal(str)
    PIXMAP_CACHE = defaultdict(QtGui.QPixmap)
    THUMBNAIL_PATH_CACHE = defaultdict(str)
    # PIXMAP_CACHE = {}
    # THUMBNAIL_PATH_CACHE = {}

    @classmethod
    def clear(cls):
        _ThumbnailCache.PIXMAP_CACHE = defaultdict(QtGui.QPixmap)
        _ThumbnailCache.THUMBNAIL_PATH_CACHE = defaultdict(str)

    def __init__(self):
        super(_ThumbnailCache, self).__init__()
        
        self._thread_start = False

        self._thread = QtCore.QThread()
        self._pixmap_thread = ThumbnailPixmapThread()
        self._pixmap_thread.moveToThread(self._thread)
        self._pixmap_thread.stop_signal.connect(self.finish_analyze)
        self._thread.started.connect(self._pixmap_thread.analyze)
        # self._thread.finished.connect(self.finish_analyze)

        self._pixmap_thread.cached.connect(self.cached.emit)

    def _cached_emit(self, object_id):
        self.cached.emit(object_id)

    def finish_analyze(self):
        self._thread_start = False
        # print("thumbnail cache thread finish")
        self._thread.quit()
        # self._thread.wait()

    # @classmethod
    def get_pixmap(self, handle, cmd = None):
        # self._pixmap_thread.get(handle)
        _object = handle.object()
        _id = handle.id()
        _thumbnail = handle.get_thumbnail()
        _object_id = "{}:{}".format(_object, _id)
        # if not self.PIXMAP_CACHE.get(_object_id) or self.THUMBNAIL_PATH_CACHE.get(_object_id) != _thumbnail:
        if _object_id not in self.PIXMAP_CACHE or self.THUMBNAIL_PATH_CACHE.get(_object_id) != _thumbnail:
            self.PIXMAP_CACHE[_object_id] = None
            self.THUMBNAIL_PATH_CACHE[_object_id] = _thumbnail
            self._pixmap_thread.get(handle, cmd)
            if not self._thread_start:
                self._thread.start()
                self._thread_start = True
        return self.PIXMAP_CACHE[_object_id]


class CloudImagePixmapThread(QtCore.QObject):
    cached = QtCore.Signal(str)
    stop_signal = QtCore.Signal()
    def __init__(self):
        super(CloudImagePixmapThread, self).__init__()
        self._count = 0

        self._sleep_time = 0

        self._url_pool = []

        self._cmd_pool = []

    def get(self, url, cmd):
        self._url_pool.append( url )
        self._cmd_pool.append( cmd )

    def analyze(self):
        self._count += 1
        while True:
            if self._url_pool:
                for _index, _url in enumerate(self._url_pool):
                    _thumbnail = _url
                    try:
                        if _thumbnail:
                            if _thumbnail.startswith("http:"):
                                req = httpsession.get(_thumbnail)
                                _pixmap = QtGui.QPixmap()
                                _pixmap.loadFromData(req.content)
                            else:
                                _pixmap = QtGui.QPixmap(_thumbnail)
                        else:
                            _pixmap = None
                    except:
                        _pixmap = None
                    _CloudImageCache.PIXMAP_CACHE[_url] = _pixmap
                    # self.cached.emit(_object_id)
                    self._url_pool.pop(_index)
                    if self._cmd_pool[_index]:
                        try:
                            self._cmd_pool[_index]()
                        except Exception as e:
                            print(e)
                    self._cmd_pool.pop(_index)
                self._sleep_time = 0
            else:
                self._sleep_time = 0.1
            # return
            self.stop_signal.emit()
            time.sleep(self._sleep_time)


class _CloudImageCache(QtCore.QObject):
    cached = QtCore.Signal(str)
    PIXMAP_CACHE = {}

    @classmethod
    def clear(cls):
        _CloudImageCache.PIXMAP_CACHE = defaultdict(QtGui.QPixmap)
        # cls.THUMBNAIL_PATH_CACHE = defaultdict(str)

    def __init__(self):
        super(_CloudImageCache, self).__init__()
        
        self._thread_start = False

        self._thread = QtCore.QThread()
        self._pixmap_thread = CloudImagePixmapThread()
        self._pixmap_thread.moveToThread(self._thread)

        self._pixmap_thread.stop_signal.connect(self.finish_analyze)
        self._thread.started.connect(self._pixmap_thread.analyze)
        # self._thread.finished.connect(self.finish_analyze)

        self._pixmap_thread.cached.connect(self.cached.emit)

    def _cached_emit(self, object_id):
        self.cached.emit(object_id)

    def finish_analyze(self):
        self._thread_start = False
        # print("cloud image thread finish")
        self._thread.quit()
        # self._thread.wait()

    # @classmethod
    def get_pixmap(self, url, cmd = None):
        if url not in self.PIXMAP_CACHE:
            self.PIXMAP_CACHE[url] = None
            self._pixmap_thread.get(url, cmd)
            if not self._thread_start:
                self._thread.start()
                self._thread_start = True
        return self.PIXMAP_CACHE[url]


# 全局
ThumbnailCache = _ThumbnailCache()

CloudImageCache = _CloudImageCache()

# class _ThumbnailPixmapThread(threading.Thread):
#     exec_ = False
#     def __init__(self, handle):
#         super(_ThumbnailPixmapThread, self).__init__()

#         self._handle = handle

#     def run(self):
#         _object = self._handle.object()
#         _id = self._handle.id()
#         _object_id = "{}:{}".format(_object, _id)
#         _thumbnail = self._handle.get_thumbnail()
#         if _thumbnail:
#             if _thumbnail.startswith("http:"):
#                 req = httpsession.get(_thumbnail)
#                 _pixmap = QtGui.QPixmap()
#                 _pixmap.loadFromData(req.content)
#             else:
#                 _pixmap = QtGui.QPixmap(_thumbnail)
#         else:
#             _pixmap = None
#         # self.PIXMAP[self._user_id] = _pixmap        
#         ThumbnailCache.PIXMAP_CACHE[_object_id] = _pixmap