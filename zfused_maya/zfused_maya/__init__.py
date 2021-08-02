# coding:utf-8
# --author-- lanhua.zhou

import os
import sys

__version__ = "0.0.1"

_resource = None

PATH = os.path.abspath(__file__)
DIRNAME = os.path.dirname(os.path.dirname(PATH))

sys.path.insert(0,os.path.dirname(PATH))
sys.path.insert(0,os.path.dirname(DIRNAME))
sys.path.insert(0,"{}/packages".format(DIRNAME))


def _get_maya_version():
    import maya.cmds as cmds
    version = cmds.about(q=True, version=True)
    os = cmds.about(q=True, os=True)
    return "maya-%s-%s" % (version, os)

# plugins path
PLUGIN_PATH = "{}/plug-ins/{}".format(os.path.dirname(DIRNAME), _get_maya_version())

#RESOURCE_PATH = os.path.join(DIRNAME, "resources")
RESOURCE_PATH = DIRNAME
#RESOURCE_PATH = os.path.join(DIRNAME, "resources")
SETUP_PATH = os.path.join(DIRNAME, "setup")


def version():
    """
    return the current version of the zfused client

    :rtype: sts
    """
    return __version__

def software_id():
    """
    return zfused software id

    """
    import zfused_api
    import maya.cmds as cmds
    _softwares = zfused_api.zFused.get("software", filter = {"Code":"maya", "Version": int(cmds.about(version = True))})
    if _softwares:
        return _softwares[0]["Id"]
    return 0