# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


class ProjectStepLayer(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(ProjectStepLayer, self).__init__("project_step_layer", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("project_step_layer", self._id)
                if not _data:
                    logger.error("project step layer id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def is_decisive(self):
        return self._data.get("Decisive")


class ProjectStepCheck(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(ProjectStepCheck, self).__init__("project_step_check", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("project_step_check", self._id)
                if not _data:
                    logger.error("project step layer id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def check_id(self):
        return self._data.get("CheckId")

    def check(self):
        return zfused_api.check.Check(self._data.get("CheckId"))

    def is_ignore(self):
        return self._data.get("IsIgnore")
    
    def update_is_ignore(self, is_ignore):
        self.global_dict[self._id]["IsIgnore"] = is_ignore
        self._data["IsIgnore"] = is_ignore
        v = self.put("project_step_check", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False


class ProjectStep(_Entity):

    @classmethod
    def new(cls, name, code, project_id, project_entity_type, software_id, color):
        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _created_by = zfused_api.zFused.USER_ID
        _project_step, _status = zfused_api.zFused.post( key = "project_step", data = { "Name": name,
                                                                                           "Code": code,
                                                                                           "ProjectId": project_id,
                                                                                           "Object": project_entity_type,
                                                                                           "SoftwareId": software_id,
                                                                                           "Color": color,
                                                                                           "InitScript": "print('init script')",
                                                                                           "CombineScript": "print('combine script')",
                                                                                           "PropertyScript": "print('property script')",
                                                                                           "ComputeScript": "print('compute script')",
                                                                                           "RefreshRelative": 1,
                                                                                           "Active": "true",
                                                                                           "CreatedBy":_created_by,
                                                                                           "CreatedTime":_created_time } )
        if _status:
            return _project_step["Id"], True
        return "{} create error".format(name), False

    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(ProjectStep, self).__init__("project_step", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("project_step", self._id)
                if not _data:
                    logger.error("project step id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def file_code(self):
        """ project step file code

        :rtype: str
        """
        return self.code().replace("/", "_")

    def full_name_code(self):
        return self.name_code()

    def file_path(self):
        return self.code()

    @_Entity._recheck
    def color(self):
        """ return step color
            step数据库需要增加color属性,调用project step color效率低
        """
        _color = self._data.get("Color")
        if _color:
            return _color
        else:
            # get project step color
            _step_handle = Step(self._data["StepId"])
            return _step_handle.color()
    
    @_Entity._recheck
    def sort(self):
        return self._data["Sort"]

    @_Entity._recheck
    def software(self):
        return zfused_api.software.Software(self._data.get("SoftwareId"))

    @_Entity._recheck
    def project_id(self):
        return self._data.get("ProjectId")

    @_Entity._recheck
    def project(self):
        return zfused_api.project.Project(self._data.get("ProjectId"))

    @_Entity._recheck
    def project_step_type(self):
        return self._data.get("Object")

    @_Entity._recheck
    def step_id(self):
        return self._data.get("StepId")

    @_Entity._recheck
    def step(self):
        return Step(self._data.get("StepId"))

    def default_path(self):
        _path = "{}/{}".format(self.code(), self.software().code())
        return _path
    
    @_Entity._recheck
    def path(self):
        # default path
        _path = self.default_path()
        _custom_path = self._data.get("CustomPath")
        if _custom_path:
            _path = self.get_custom_path(_custom_path)
        return _path

    def review_process(self):
        _rp = self.get("review_process", filter = {"EntityType":"project_step", "EntityId":self._id},
                                         sortby = ["Sort"], order = ["asc"] )
        if not _rp:
            return []
        return _rp

    def user_ids(self):
        return list(set(self.review_user_ids() + self.approvalto_user_ids() + self.cc_user_ids()))

    def review_user_ids(self, review_process_id = None):
        if review_process_id:
            _rs = self.get("review_user", filter = {"EntityType":"project_step", "EntityId":self._id, "ReviewProcessId": review_process_id})
        else:
            _rs = self.get("review_user", filter = {"EntityType":"project_step", "EntityId":self._id})
        if not _rs:
            return []
        return [_r["UserId"] for _r in _rs]

    def approvalto_user_ids(self):
        _apps = self.get("approval_user", filter = {"Object":"project_step", "LinkId":self._id})
        if not _apps:
            return []
        return [_app["UserId"] for _app in _apps]

    def cc_user_ids(self):
        _ccs = self.get("cc_user", filter = {"Object":"project_step", "LinkId":self._id})
        if not _ccs:
            return []
        return [_cc["UserId"] for _cc in _ccs]

    def add_approvalto_user(self, user_id):
        """添加审查人员

        :rtype: str
        """
        _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        logger.info("add approval user {} to project step {}".format(user_id, self._id))
        _apps = self.get("approval_user", filter = {"Object":"project_step", "LinkId":self._id, "UserId": user_id})
        if _apps:
            logger.warning("user {} in project step {} approval user".format(user_id, self._id))
            return 
        else:
            self.post( key = "approval_user", data = { "Object": "project_step", 
                                                       "LinkId": self._id, 
                                                       "UserId": user_id, 
                                                       "Sort": 0,
                                                       "CreatedBy": zfused_api.zFused.USER_ID,
                                                       "CreatedTime": _current_time  })

    def remove_approvalto_user(self, user_id):
        """ 移除审查人员
        """
        logger.info("remove approval user {} from project step {}".format(user_id, self._id))
        _datas = self.get("approval_user", filter = {"Object":"project_step", "LinkId":self._id, "UserId": user_id})
        if _datas:
            self.delete("approval_user", _datas[0]["Id"])

    def add_cc_user(self, user_id):
        """添加抄送人员

        :rtype: str
        """
        _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        logger.info("add cc user {} to project step {}".format(user_id, self._id))
        _ccs = self.get("cc_user", filter = {"Object":"project_step", "LinkId":self._id, "UserId": user_id})
        if _ccs:
            logger.warning("user {} in project step {} cc user".format(user_id, self._id))
            return
        else:
            self.post( key = "cc_user", data = { "Object": "project_step", 
                                                 "LinkId": self._id, 
                                                 "UserId": user_id, 
                                                 "Sort": 0,
                                                 "CreatedBy": zfused_api.zFused.USER_ID,
                                                 "CreatedTime": _current_time  })

    def remove_cc_user(self, user_id):
        """ 移除抄送人员
        """
        logger.info("remove cc user {} from project step {}".format(user_id, self._id))
        _datas = self.get("cc_user", filter = {"Object":"project_step", "LinkId":self._id, "UserId": user_id})
        if _datas:
            self.delete("cc_user", _datas[0]["Id"])

    def is_new_attribute_solution(self):
        """新的属性输入输出解决方案
        """
        _attrs = self.get("attr_output", filter = {"ProjectStepId":self._id})
        if not _attrs:
            _attrs = self.get("step_attr_output", filter = {"ProjectStepId":self._id})
            if _attrs:
                return False
            _attrs = self.get("step_attr_input", filter = {"ProjectStepId":self._id})
            if _attrs:
                return False
        return True

    def output_attrs(self):
        """获取输出属性
        :rtype: str
        """
        _attrs = self.get("attr_output", filter = {"ProjectStepId":self._id}, sortby = ["Sort"], order = ["asc"])
        if _attrs:
            return [zfused_api.attr.Output(_attr.get("Id")) for _attr in _attrs]
        if not _attrs:
            _attrs = self.get("step_attr_output", filter = {"ProjectStepId":self._id})
        return _attrs if _attrs else []

    def key_output_attr(self):
        """获取 主文件 输出属性 
        :rtype: str
        """
        _attrs = self.get("attr_output", filter = {"ProjectStepId":self._id, "Code": "file"}, sortby = ["Sort"], order = ["asc"])
        if _attrs:
            return zfused_api.attr.Output(_attrs[0].get("Id"))
        if not _attrs:
            _attrs = self.get("step_attr_output", filter = {"ProjectStepId":self._id, "Code": "file"})
        return _attrs[0] if _attrs else None

    def input_attrs(self):
        """获取输出属性
        :rtype: str
        """
        _attrs = self.get("attr_input", filter = {"ProjectStepId":self._id}, sortby = ["Sort"], order = ["asc"])
        if _attrs:
            return [zfused_api.attr.Input(_attr.get("Id")) for _attr in _attrs]
        if not _attrs:
            _attrs = self.get("step_attr_input", filter = {"ProjectStepId":self._id})
        return _attrs if _attrs else []

    @_Entity._recheck
    def init_script(self):
        return self._data.get("InitScript")

    @_Entity._recheck
    def update_init_script(self, script):
        self.global_dict[self._id]["InitScript"] = script
        self._data["InitScript"] = script
        v = self.put("project_step", self._id, self._data)
        if v:
            return True
        else:
            return False

    @_Entity._recheck
    def combine_script(self):
        return self._data.get("CombineScript")

    @_Entity._recheck
    def update_combine_script(self, script):
        self.global_dict[self._id]["CombineScript"] = script
        self._data["CombineScript"] = script
        v = self.put("project_step", self._id, self._data)
        if v:
            return True
        else:
            return False

    @_Entity._recheck
    def compute_script(self):
        return self._data.get("ComputeScript")

    @_Entity._recheck
    def update_compute_script(self, script):
        self.global_dict[self._id]["ComputeScript"] = script
        self._data["ComputeScript"] = script
        v = self.put("project_step", self.id, self._data)
        if v:
            return True
        else:
            return False

    @_Entity._recheck
    def forbidden_script(self):
        return self._data.get("ForbiddenScript")

    @_Entity._recheck
    def update_forbidden_script(self, script):
        self.global_dict[self._id]["ForbiddenScript"] = script
        self._data["ForbiddenScript"] = script
        v = self.put("project_step", self._id, self._data)
        if v:
            return True
        else:
            return False

    @_Entity._recheck
    def property_script(self):
        return self._data.get("PropertyScript")

    @_Entity._recheck
    def update_property_script(self, script):
        self.global_dict[self._id]["PropertyScript"] = script
        self._data["PropertyScript"] = script
        v = self.put("project_step", self._id, self._data)
        if v:
            return True
        else:
            return False

    @_Entity._recheck
    def refresh_relative(self):
        return self._data.get("RefreshRelative")

    @_Entity._recheck
    def update_refresh_relative(self, is_refresh):
        self.global_dict[self._id]["RefreshRelative"] = is_refresh
        self._data["RefreshRelative"] = is_refresh
        v = self.put("project_step", self._id, self._data)
        if v:
            return True
        else:
            return False

    def add_check(self, check_id):
        _is_exists = zfused_api.zFused.get("project_step_check", filter = {"ProjectStepId":self._id, "CheckId": check_id})
        if not _is_exists:
            _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            _create_by = zfused_api.zFused.USER_ID
            _value, _status = zfused_api.zFused.post(key = "project_step_check", data = { "ProjectStepId": self._id,
                                                                                          "CheckId": check_id,
                                                                                          "IsIgnore": 0,
                                                                                          "CreatedBy": _create_by,
                                                                                          "CreatedTime": _current_time })
            if _status:
                return ProjectStepCheck(_value["Id"], _value), True
        return None, False


    def remove_check(self, check_id):
        _is_exists = zfused_api.zFused.get("project_step_check", filter = {"ProjectStepId":self._id, "CheckId": check_id})
        if _is_exists:
            for _is_exist in _is_exists:
                zfused_api.zFused.delete("project_step_check", _is_exist.get("Id"))

    def checks(self):
        _nodes = zfused_api.zFused.get("project_step_check", filter = {"ProjectStepId":self._id})
        if _nodes:
            return [ProjectStepCheck(_node.get("Id")) for _node in _nodes]
        return []

    @_Entity._recheck
    def check_script(self):
        return self._data.get("CheckScript")

    @_Entity._recheck
    def update_check_script(self, script):
        self.global_dict[self._id]["CheckScript"] = script
        self._data["CheckScript"] = script
        v = self.put("project_step", self._id, self._data)
        if v:
            return True
        else:
            return False

    @_Entity._recheck
    def update_color(self, color):
        self.global_dict[self._id]["Color"] = color
        self._data["Color"] = color
        v = self.put("project_step", self._id, self._data)
        if v:
            return True
        else:
            return False

    def assembly_attributes(self):
        ''' get is assembly attrs
        :rtype: list
        '''
        _attrs = self.get('step_attr_output', filter = {'ProjectStepId': self._id, 'IsSubassembly__gte': 1 }, 
                                              sortby = ['IsSubassembly'], 
                                              order =  ['desc'])
        if not _attrs:
            return []
        return _attrs









class Step(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Step, self).__init__("step", entity_id, entity_data)
        
        if not self.global_dict.__contains__(self._id):
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("step", self._id)
                if not _data:
                    logger.error("step id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    @_Entity._recheck
    def color(self):
        return self._data["Color"]