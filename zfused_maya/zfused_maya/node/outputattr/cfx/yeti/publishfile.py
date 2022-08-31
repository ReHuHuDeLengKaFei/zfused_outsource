# coding:utf-8
# --author-- binglu.wang
from __future__ import print_function

import os
import logging

import maya.cmds as cmds

import zfused_api
from zcore import filefunc

import zfused_maya.core.record as record

import zfused_maya.node.core.alembiccache as alembiccache
import zfused_maya.node.core.texture as texture
import zfused_maya.node.core.yeti as yeti
import zfused_maya.node.core.material as material
import zfused_maya.node.core.fixmeshname as fixmeshname
import zfused_maya.node.core.renderinggroup as renderinggroup
import zfused_maya.node.core.referencefile as referencefile

__all__ = ["publish_file"]

logger = logging.getLogger(__name__)

# test
def publish_file(*args, **kwargs):
    """ 上传yeti文件
    
    """
    
    output_entity_type, output_entity_id, output_attr_id = args

    _output_attr_handle = zfused_api.outputattr.OutputAttr(output_attr_id)
    _suffix = _output_attr_handle.suffix()
    _file_format = _output_attr_handle.format()
    _attr_code = _output_attr_handle.code()

    _project_step_id = _output_attr_handle.data()["ProjectStepId"]
    _project_step_handle = zfused_api.step.ProjectStep(_project_step_id)
    _step_code = _project_step_handle.code()
    _software_code = zfused_api.software.Software(_project_step_handle.data()["SoftwareId"]).code()
    
    _output_link_handle = zfused_api.objects.Objects(output_entity_type, output_entity_id)
    _production_path = _output_link_handle.production_path()
    _temp_path = _output_link_handle.temp_path()
    _file_code = _output_link_handle.file_code()

    _task = _output_link_handle.tasks([_project_step_id])[0]
    _task_id = _task["Id"]
    _task_handle = zfused_api.task.Task(_task_id)
    if kwargs.get("fix_version"):
        _file_index = "{:0>4d}".format(_task_handle.last_version_index( 0 ))
    else:
        _file_index = "{:0>4d}".format(_task_handle.last_version_index() + 1)

    _production_file = "{}/{}/{}/{}/{}.{}{}".format( _production_path, _step_code, _software_code, _attr_code, _file_code, _file_index, _suffix )
    _production_file_dir = os.path.dirname(_production_file)
    _cover_file = "{}/{}/{}/{}/{}{}".format(_production_path, _step_code, _software_code, _attr_code, _file_code, _suffix)
    _publish_file = "{}/{}/{}/{}/{}.{}{}".format( _temp_path, _step_code, _software_code, _attr_code, _file_code, _file_index, _suffix )
    _publish_file_dir = os.path.dirname(_publish_file)
    if not os.path.isdir(_publish_file_dir):
        os.makedirs(_publish_file_dir)

    try:
        _current_file = cmds.file(q = 1,sn = 1)
        # save publish file
        _sel = [i for i in cmds.ls("fx") if cmds.objExists("%s.name"%i) and cmds.getAttr("%s.name"%i) == "fx"]
        _yeti_all_set = cmds.ls("yeti_all_sets",type = "objectSet")
        if _yeti_all_set:
            _sel.append(_yeti_all_set[0])
        cmds.select(_sel,r = 1,ne = 1)
        cmds.file(rename = _publish_file)
        cmds.file(f = 1,options = "v=0;",typ = "mayaBinary" ,pr= 1, es=1)

        # open publish file
        cmds.file(new = 1,f= 1)
        cmds.file(_publish_file,f =1,o = 1,typ = "mayaBinary",ignoreVersion = 1,options = "v=0;")
        
        # publish texture
        # 修改文件中贴图路径
        _texture_files = texture.files()
        if _texture_files:
            # 获取路径
            _path_set = texture.paths(_texture_files)[0]
            _intersection_path = max(_path_set)
            texture.publish_file(_texture_files, _intersection_path, _production_path + "/texture/yeti/filenodes")
            # change maya texture node path
            _file_nodes = texture.nodes()
            if _file_nodes:
                texture.change_node_path(_file_nodes, _intersection_path, _production_path + "/texture/yeti/filenodes")

        # 修改文件中yeti节点里的贴图路径
        _yeti_texture_file = yeti.tex_files()
        if _yeti_texture_file:
            _path_set = yeti.paths(_yeti_texture_file)[0]
            _intersection_path = max(_path_set)
            yeti.publish_file(_yeti_texture_file, _intersection_path, _production_path + "/texture/yeti")
            _yeti_texture_dict = yeti._get_yeti_attr("texture","file_name")
            yeti.change_node_path(_yeti_texture_dict,_intersection_path, _production_path + "/texture/yeti")

        # delete unused material
        material.delete_unused()

        # recore material
        material.record()
        
        # save publish file
        cmds.file(save = True, type = _file_format, f = True)
        
        # publish file
        _result = filefunc.publish_file(_publish_file, _production_file)
        _result = filefunc.publish_file(_publish_file, _cover_file)

        # link files
        zfused_api.files.new_file("task", _task_id, _production_file, int(_file_index))
        zfused_api.files.new_file("task", _task_id, _cover_file, int(_file_index))

    except Exception as e:
        logger.error(e)
        return False

    # open orignal file
    # if _current_file:
    #     cmds.file(_current_file, o = True, f = True, pmt = True)
    return True


if __name__ == '__main__':
    publish_file()