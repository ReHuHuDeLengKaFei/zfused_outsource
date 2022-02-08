 # coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os







def publish_file(task_id, infomation={}, is_auto=False):
    """ publish file
    :rtype: bool
    """
    record.write_task_id(task_id)

    cmds.file(lf = 0)
    cmds.file(save = True, f = True, options = "v=0;")
    _current_file = cmds.file(q=True, sn=True)

    _task = zfused_api.task.Task(task_id)
    _project_entity = _task.project_entity()
    _project_step = _task.project_step()
    _output_scripts = _project_step.output_attrs()
    _is_new_attribute_solution = _project_step.is_new_attribute_solution()

    if not is_auto:
        # 查看雷区
        _forbidden_script = _project_step.forbidden_script()
        if _forbidden_script:
            forbidden_value = True
            exec(_forbidden_script)
            if not forbidden_value:
                return
        # 任务检查
        _project_step_checks = _project_step.checks()
        if _project_step_checks:
            _ui = checkwidget.CheckWidget(_project_step_checks)
            if not check.Check.value:
                _ui.show()
            if check.Check.value == True:
                _ui.close()
                check.Check.value = False
            else:
                return False
        # else: # 移除，分块检查
        #     _check_script = _project_step.check_script()
        #     if _check_script and len(_check_script) != 1:
        #         if not check.Check.value:
        #             exec(_check_script)
        #         if check.Check.value == True:
        #             check.Check.value = False
        #         else:
        #             return False

    # # 获取场景信息
    # _scene_elements = element.scene_elements()

    # # 更新propertry
    # _property_script = _project_step.property_script()
    # if _property_script:
    #     global project_entity
    #     project_entity = _task.project_entity()
    #     exec(_property_script)

    # # 获取运算
    # compute_result = None
    # _compute_script = _project_step.data().get("ComputeScript")
    # exec(_compute_script)
    # _record = compute_result

    # # 提交关联信息
    # relatives.create_relatives()

    # # 提交预览信息
    # if "video" in infomation:
    #     if infomation["video"]:
    #         _approval_file = infomation["video"]
    #     else:
    #         _approval_file = infomation["thumbnail"]
    # else:
    #     _approval_file = infomation["thumbnail"]
    # _zfile = zfile.LocalFile(_approval_file, "approval")
    # _res = _zfile.upload()
    # if _res:
    #     thumbnail_path = _zfile._cloud_thumbnail_path
    #     _task.update_thumbnail_path(thumbnail_path)
    # _thumbnail_path = _zfile._cloud_thumbnail_path

    # # 上传备份文件
    # _value = publish_backup(task_id, infomation)
    # if not _value:
    #     cmds.confirmDialog(message=u"上传备份文件失败")
    #     return False

    # 运行自定义脚本
    if _output_scripts:
        for _output_script in _output_scripts:
            publish_result = False
            _output_entity_type = _task.data()["ProjectEntiyType"]
            _output_entity_id = _task.data()["ProjectEntiyId"]
            _output_attr_id = _output_script["Id"]
            # 为了兼容新旧attribute 需要设定 _is_new_attribute_solution
            kwargs = {"is_new_attribute_solution": _is_new_attribute_solution}
            if _is_new_attribute_solution:
                args = (task_id, _output_attr_id)
            else:
                args = (_output_entity_type, _output_entity_id, _output_attr_id)
            # run scrpt
            zfused_api.zFused.RESET = True
            exec(_output_script["Script"])
            zfused_api.zFused.RESET = False
            if not publish_result:
                cmds.confirmDialog(message=u"发布失败 \n{}".format(_output_script["Script"]))
                cmds.file(_current_file, o=True, f=True, pmt=False)
                return False