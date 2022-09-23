# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import sys
import maya.utils



def clear():
    # remove class
    for k in sorted(k for k, m in sys.modules.items() if m and k.startswith('zfused_maya')):
        del sys.modules[k]
    for k in sorted(k for k, m in sys.modules.items() if m and k.startswith('zfused_api')):
        del sys.modules[k]
    for k in sorted(k for k, m in sys.modules.items() if m and k.startswith('zcore')):
        del sys.modules[k]
    for k in sorted(k for k, m in sys.modules.items() if m and k.startswith('zwidgets')):
        del sys.modules[k]


def login():
    _pipeline_path = r"P:\zfused\pipeline\zfused_outsource"

    def _python_version():
        _ver = sys.version_info
        _major = _ver.major
        _minor = _ver.minor
        return "_python%s.%s" % (_major, _minor)

    sys.path.append(r"{}\libs\{}".format(_pipeline_path, _python_version()))
    sys.path.append(r"{}\packages".format(_pipeline_path))
    sys.path.append(r"{}\zfused_maya".format(_pipeline_path))

    import zfused_maya

    maya.utils.executeDeferred(zfused_maya.login)