#coding:utf-8
CODE_TITLE      = u'相机黑边预览'
CODE_AUTHOR     = 'ning.qin'
CODE_VERSION    = '0.2'
CODE_START_DATE = 20230222
CODE_EDIT_DATE  = 20230228

import os
import json
from pymel.core import *
import maya.cmds as cmds

import zfused_api
import zfused_maya.core.record as record
# import zfused_maya.core.resource as resource

def read_json_file(file_path):
    with open(os.path.abspath(file_path), "r") as json_file:
        json_dict = json.load(json_file)
    return json_dict if json_dict else {}
def write_json_file(json_dict, file_path):
    with open(file_path,"w") as json_file:
        json_file.write(json.dumps(json_dict,indent = 4,separators=(',',':')))
        json_file.close()

def _get_project_path():
    _project_id = record.current_project_id()
    _project_handle = zfused_api.project.Project(_project_id)
    return _project_handle.production_path()
def _get_width_height():
    _project_id = record.current_project_id()
    _project_handle = zfused_api.project.Project(_project_id)
    return _project_handle.image_width(), _project_handle.image_height()
# SETUP_DIR = '{}/setup/'.format(_get_project_path())
IMAGE_NAME = 'MAYACAM__2048_1152__2048_858.png'
# IMAGE_PATH = resource.get('uis/animation/letterboxpreview', 'MAYACAM__2048_1152__2048_858.png')


def get_cam(*args):
    viewport_list = list(set(getPanel(type = 'modelPanel')).intersection(set(getPanel(visiblePanels = True))))
    cam = modelPanel(viewport_list[0], query = True, camera = True)
    return cam

def set_imageplane(cam):
    current_dir = os.path.split(__file__)[0]
    image_path = os.path.join(current_dir, IMAGE_NAME)

    stereo_imageplane = imagePlane(camera = cam, fileName = image_path)
    setAttr(stereo_imageplane[1] + '.depth', 1)

    cam_shape = str(listRelatives(cam, shapes = True)[0])
    setAttr(cam_shape + '.filmFit', True)
    setAttr(cam_shape + '.displayResolution', True)
    setAttr(cam_shape + '.displayGateMaskOpacity', 1)
    setAttr(cam_shape + '.displayGateMaskColor', (0,0,0))
    
def set_render_attr(*args):
    # playblast_setup_path = SETUP_DIR + 'MAYA_PLAYBLAST.json'
    # playblast_setup_dict = read_json_file(playblast_setup_path)
    # width = playblast_setup_dict['width']
    # height = playblast_setup_dict['height']
    width, height = _get_width_height()
    
    setAttr('defaultResolution.width', width)
    setAttr('defaultResolution.height', height)
    setAttr('defaultResolution.deviceAspectRatio', float(width)/height)


def add_imageplane_to_selection(*args):
    cam = ls(selection = True)[0]
    if len(listHistory(cam, type = 'imagePlane')) == 0:
        set_imageplane(cam)
        # set_render_attr()
    else:
        confirmDialog(title = u'一个悲伤的故事', message = cam + u'有image plane了', button = u'emmm')

def add_imageplane_to_viewport(*args):
    cam = get_cam()
    if len(listHistory(cam, type = 'imagePlane')) == 0:
        set_imageplane(cam)
        # set_render_attr()
    else:
        confirmDialog(title = u'一个悲伤的故事', message = cam + u'有image plane了', button = u'emmm')

def ui(*args):
    
    try:
        dialog_stereo_preview
    except:
        print('create window')
    else:
        if control(dialog_stereo_preview, exists = True):
            deleteUI(dialog_stereo_preview)
    if window('window_stereo_preview', exists = True):
        deleteUI('window_stereo_preview')
    
    # qt_ui_file = resource.get('uis/animation/letterboxpreview', 'letterboxpreview.ui')
    current_dir = os.path.split(__file__)[0]
    qt_ui_file = os.path.join(current_dir, 'letterboxpreview.ui')
    print(qt_ui_file)
    window_stereo_preview = window('window_stereo_preview', title = CODE_TITLE + CODE_VERSION, widthHeight = (450, 100))
    paneLayout('layout_stereo_preview', configuration = 'single')
    dialog_stereo_preview = loadUI(verbose = 1, uiFile = qt_ui_file)
    control(dialog_stereo_preview, edit = True, parent = 'layout_stereo_preview')
    showWindow('window_stereo_preview')

    button('add_imageplane_to_selection_button', edit = True, command = add_imageplane_to_selection)
    button('add_imageplane_to_viewport_button', edit = True, command = add_imageplane_to_viewport)
