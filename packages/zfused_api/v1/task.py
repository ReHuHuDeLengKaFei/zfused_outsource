# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict
from collections import OrderedDict

import os
import time
import shutil
import datetime
import logging
import copy

from . import _Entity
import zfused_api

from . import worktime

logger = logging.getLogger(__name__)

def new_production_file(files, task_id, attr_output_id, index = 0, relative_entity_type = "", relative_entity_id = 0, relative_name_sapce = "", fix_version = False): 
    if not files:
        return
    
    _file_path_list = [_file.get("path") for _file in files]

    _task_handle = Task(task_id)
    _project_id = _task_handle.data().get("ProjectId")
    _project_step_id = _task_handle.data().get("ProjectStepId")
    _project_step_attr_id = attr_output_id

    _project_entity_type = _task_handle.data().get("ProjectEntityType")
    _project_entity_id = _task_handle.data().get("ProjectEntityId")
    _project_step_handle = zfused_api.step.ProjectStep(_project_step_id)
    _software_id = _project_step_handle.data().get("SoftwareId")

    _index = index

    # relative
    _relative_entity_type = relative_entity_type
    _relative_entity_id = relative_entity_id
    _relative_name_space = relative_name_sapce

    # remove production file if exists
    _production_files = zfused_api.zFused.get( "production_file", 
                                               filter = { "TaskId": task_id,
                                                          "ProjectStepAttrId": _project_step_attr_id } )
    if _production_files:
        for _file in _production_files:
            if fix_version:
                if _file.get("Path") in _file_path_list:
                    zfused_api.zFused.delete("production_file", _file["Id"])
            else:
                zfused_api.zFused.delete("production_file", _file["Id"])

    # remove record files
    _production_files = zfused_api.zFused.get( "production_file_record", 
                                               filter = { "TaskId": task_id,
                                                          "Index": _index,
                                                          "ProjectStepAttrId": _project_step_attr_id } )
    if _production_files:
        for _file in _production_files:
            if fix_version:
                if _file.get("Path") in _file_path_list:
                    zfused_api.zFused.delete("production_file_record", _file["Id"])
            else:
                zfused_api.zFused.delete("production_file_record", _file["Id"])

    # new file
    _created_id = zfused_api.zFused.USER_ID
    _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    for _file in files:
        _file_md5 = _file.get("md5")
        _file_path = _file.get("path")
        _file_name = _file.get("name")
        _file_format = _file.get("format")
        _file_suffix = _file.get("suffix")
        _file_size = _file.get("size")
        _file_thumbnail_path = _file.get("thumbnail_path")
        _file_width = _file.get("width")
        _file_height = _file.get("height")

        # relative
        if _file.get("relative_entity_type"):
            _relative_entity_type = _file.get("relative_entity_type")
        if _file.get("relative_entity_id"):
            _relative_entity_id = _file.get("relative_entity_id")
        if _file.get("relative_name_space"):
            _relative_name_space = _file.get("relative_name_space")

        zfused_api.zFused.post( key = "production_file",
                                data = { "ProjectId": _project_id,
                                         "ProjectStepId": _project_step_id,
                                         "ProjectStepAttrId": _project_step_attr_id,
                                         "ProjectEntityType": _project_entity_type,
                                         "ProjectEntityId": _project_entity_id,
                                         "TaskId": task_id,
                                         "Index": _index,
                                         "RelativeEntityType": _relative_entity_type,
                                         "RelativeEntityId": _relative_entity_id,
                                         "RelativeNameSpace": _relative_name_space,
                                         "SoftwareId": _software_id,
                                         "MD5": _file_md5,
                                         "Path": _file_path,
                                         "Name": _file_name,
                                         "Format": _file_format,
                                         "Suffix": _file_suffix,
                                         "Size": _file_size,
                                         "ThumbnailPath": _file_thumbnail_path,
                                         "Width": _file_width,
                                         "Height": _file_height,
                                         "CreatedBy": _created_id,
                                         "CreatedTime": _created_time } )

        zfused_api.zFused.post( key = "production_file_record",
                                data = { "ProjectId": _project_id,
                                         "ProjectStepId": _project_step_id,
                                         "ProjectStepAttrId": _project_step_attr_id,
                                         "ProjectEntityType": _project_entity_type,
                                         "ProjectEntityId": _project_entity_id,
                                         "TaskId": task_id,
                                         "Index": _index,
                                         "RelativeEntityType": _relative_entity_type,
                                         "RelativeEntityId": _relative_entity_id,
                                         "RelativeNameSpace": _relative_name_space,
                                         "SoftwareId": _software_id,
                                         "MD5": _file_md5,
                                         "Path": _file_path,
                                         "Name": _file_name,
                                         "Format": _file_format,
                                         "Suffix": _file_suffix,
                                         "Size": _file_size,
                                         "ThumbnailPath": _file_thumbnail_path,
                                         "Width": _file_width,
                                         "Height": _file_height,
                                         "CreatedBy": _created_id,
                                         "CreatedTime": _created_time } )

def new_task(name, link_obj, link_id, project_step_id, status_id, assigned_id, start_time, due_time, description = None, outsource = None, estimated_time = 0):

    _task = zfused_api.zFused.get("task", filter = {"ProjectStepId": project_step_id, "ProjectEntityType":link_obj, "ProjectEntityId":link_id})
    if _task:
        return False, "%s is exists"%name
    _project_step_handle = zfused_api.step.ProjectStep(project_step_id)
    project_id = _project_step_handle.data()["ProjectId"]
    step_id = _project_step_handle.data()["StepId"]
    software_id = _project_step_handle.data()["SoftwareId"]
    create_id = zfused_api.zFused.USER_ID
    currentTime = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    _task, _status = zfused_api.zFused.post( key = "task", data = { "SelfObject":"task",
                                                                     "Name": name,
                                                                     "ProjectId":project_id,
                                                                     "ProjectStepId": project_step_id,
                                                                     "ProjectEntityType": link_obj,
                                                                     "ProjectEntityId": link_id,
                                                                     "StepId":step_id,
                                                                     "StatusId":status_id,
                                                                     "AssignedTo":assigned_id,
                                                                     "SoftwareId":software_id,
                                                                     "Description":description,
                                                                     "EstimatedTime":estimated_time,
                                                                     "StartTime":start_time,
                                                                     "DueTime":due_time, 
                                                                     "IsOutsource":outsource, 
                                                                     "Active":"true",
                                                                     "CreatedBy": create_id,
                                                                     "CreatedTime": currentTime })

    if _status:
        _task = Task(_task["Id"])
        _project_entity = _task.project_entity()
        zfused_api.im.submit_message( "user",
                                      zfused_api.zFused.USER_ID,
                                      _project_entity.user_ids(),
                                      { "msgtype": "new", 
                                      "new": {"object": "task", "object_id": _task.id()} }, 
                                      "new",
                                      _project_entity.object(),
                                      _project_entity.id(),
                                      _project_entity.object(),
                                      _project_entity.id() )

        return _task.id(), "%s create success"%name
    
    return False,"%s create error"%name

def delete(task_id):
    """ delete task from task id

    """
    zfused_api.zFused.delete("task", task_id)

def clear(lis):
    del lis[:]

def cache(project_ids = [], extract_freeze = True):
    """ get project tasks 
        init 
    """
    _s_t = time.clock()

    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status", fields = ["Id"])
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0}, fields = ["Id"])
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])

    if not project_ids:
        _tasks = zfused_api.zFused.get("task", filter = {"StatusId__in": _status_ids} )
        _task_versions = zfused_api.zFused.get("version")
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_ids])
        _tasks = zfused_api.zFused.get("task", filter = {"ProjectId__in": _project_ids, "StatusId__in": _status_ids})
        _task_versions = zfused_api.zFused.get("version", filter = {"ProjectId__in": _project_ids})
    if _tasks:
        list(map(lambda _task: Task.global_dict.setdefault(_task["Id"],_task), _tasks))
        list(map(lambda _task: clear(Task.global_versions[_task["Id"]]) if Task.global_versions[_task["Id"]] else False, _tasks))
    if _task_versions:
        list(map(lambda _task_version: Task.global_versions[_task_version["TaskId"]].append(_task_version), _task_versions))
    _e_t = time.clock()
    
    logger.info("task cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    
    return _tasks

def cache_from_ids(ids, extract_freeze = True):
    _s_t = time.clock()

    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status", fields = ["Id"])
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0}, fields = ["Id"])
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])

    # self.global_dict = {}
    # Task.global_historys = defaultdict(list)
    # Task.global_versions = defaultdict(list)
    ids = "|".join(map(str, ids))
    _tasks = zfused_api.zFused.get("task", filter = {"Id__in": ids, "StatusId__in": _status_ids})
    _task_versions = zfused_api.zFused.get("version", filter = {"TaskId__in": ids})

    if _tasks:
        list(map(lambda _task: Task.global_dict.setdefault(_task["Id"],_task), _tasks))
        list(map(lambda _task: clear(Task.global_versions[_task["Id"]]) if Task.global_versions[_task["Id"]] else False, _tasks))
    # if _task_historys:
    #     list(map(lambda _task: Task.global_historys[_task["TaskId"]].append, _task_historys))
    if _task_versions:
        list(map(lambda _task_version: Task.global_versions[_task_version["TaskId"]].append(_task_version), _task_versions))
    _e_t = time.clock()
    logger.info("task cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _tasks


class Task(_Entity):


    @classmethod
    def new_sub_task(cls, task_id, name, code, description = ""):
        if zfused_api.zFused.get("task", filter = {"SubTaskCode": code, "ParentTaskId": task_id}):
            return "{} is exists, create error".format(name), False

        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _created_by = zfused_api.zFused.USER_ID

        _task = Task(task_id)
        _data = _task.data()
        
        _task_data = copy.deepcopy(_data)

        _task_data.pop("Id")
        _task_data["CreatedBy"] = _created_by
        _task_data["CreatedTime"] = _created_time
        _task_data["ProductionTime"] = 0
        _task_data["Name"] = "{}_{}".format(_task_data.get("Name"), code)
        _task_data["HasSubTask"] = 0
        _task_data["SubTaskName"] = name
        _task_data["SubTaskCode"] = code
        _task_data["ParentTaskId"] = task_id
        _task_data["Description"] = description

        _sub_task, _status = zfused_api.zFused.post( key = "task", data = _task_data )
        if _status:
            _task.set_has_sub_task(1) 

            return _sub_task["Id"], True

        return "{} create error".format(name), False



    global_dict = {}
    global_historys = defaultdict(list)
    global_versions = defaultdict(list)
    global_production = defaultdict(tuple)
    HISTORYS = []
    def __init__(self, entity_id, entity_data = None):
        super(Task, self).__init__("task", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get("task", filter = {"Id":self._id})
                if not _data:
                    logger.error("task id {0} not exists".format(self._id))
                    return
                self._data = _data[0]
                self.global_dict[self._id] = _data[0]
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]
        
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data

        self._time_nodes = []
        self._time_nodes_calculate = False

    def code(self):
        return self.name()

    def name_code(self):
        return self.name()

    # def data(self):
    #     return self.global_dict[self._id]

    def time_nodes(self):
        if not self._time_nodes_calculate:
            self._time_nodes_calculate = True
            self._time_nodes = self.get("time_node", filter = {"Object":"task","ObjectId":self._id})
        return self._time_nodes

    def description(self):
        return self._data["Description"]

    def link_object(self):
        return self._data["ProjectEntityType"]

    def link_id(self):
        return self._data["ProjectEntityId"]

    def link(self):
        return zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"])

    def user(self):
        _user_id = self._data.get("AssignedTo")
        if _user_id:
            return zfused_api.user.User(_user_id)
        return None

    def user_id(self):
        return self._data["AssignedTo"]

    def full_code(self):
        """
        get full path code
        rtype: str
        """
        return self.code()

    def full_name(self):
        """
        get full path name
        rtype: str
        """
        return u"{}".format(self._data["Name"])

    def full_name_code(self):
        """
        get full path name and code
        rtype: str
        """
        return u"{}".format(self.full_name())

    def file_code(self):
        """ get file name
        :rtype: str
        """
        _code = self.project_entity().file_code()

        _project_entity = zfused_api.zFused.get("project_entity", filter = { "ProjectId": self._data.get("ProjectId"),
                                                                             "Code": self.object()} )
        if _project_entity:
            _project_entity = _project_entity[0]
            _custom_file_code = _project_entity.get("CustomFileCode")
            if _custom_file_code:
                _code = self.get_custom(_custom_file_code)
        
        return _code

    def project(self):
        _project_id = self._data.get("ProjectId")
        if _project_id:
            return zfused_api.project.Project(_project_id)
        return None

    def project_id(self):
        """ get project id
        """
        return self.global_dict[self._id]["ProjectId"]

    def project_entity_type(self):
        return self._data["ProjectEntityType"]

    def project_entity_id(self):
        return self._data["ProjectEntityId"]

    def project_entity(self):
        return zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"])

    def entity(self):
        return zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"])

    def project_step(self):
        _project_step_id = self._data.get("ProjectStepId")
        if _project_step_id:
            return zfused_api.step.ProjectStep(_project_step_id)
        return None

    def project_step_id(self):
        return self.global_dict[self._id]["ProjectStepId"]

    def status(self):
        _status_id = self._data.get("StatusId")
        if _status_id:
            return zfused_api.status.Status(_status_id)
        return None

    def status_id(self):
        """ get status id 
        """
        return self._data.get("StatusId")
        # return self.global_dict[self._id]["StatusId"]

    def software(self):
        _software_id = self._data.get("SoftwareId")
        if _software_id:
            return zfused_api.software.Software(_software_id)
        return None

    def software_id(self):
        _software_id = self._data.get("SoftwareId")
        return _software_id

    def assigned_to(self):
        """
        """
        return self.global_dict[self._id]["AssignedTo"]

    def level(self):
        """ get asset level
        """
        return self._data["Level"]

    def update_level(self, index):
        """
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["Level"] == index:
            return True

        self.global_dict[self._id]["Level"] = index
        self._data["Level"] = index
        v = self.put("task", self._data["Id"], self._data, "level")
        if v:
            return True
        else:
            return False

    def priority(self):
        return self._data["Priority"]

    def update_priority(self, priority_index):
        """
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["Priority"] == priority_index:
            return True

        self.global_dict[self._id]["Priority"] = priority_index
        self._data["Priority"] = priority_index
        v = self.put("task", self._data["Id"], self._data, "priority")
        if v:
            return True
        else:
            return False

    def start_time(self):
        """get start time
        rtype: datetime.datetime
        """
        _time_text = self._data["StartTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def end_time(self):
        """ 
        get end time
        rtype: datetime.datetime
        """
        _time_text = self._data["DueTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def create_time(self):
        """ 
        get create time
        :rtype: datetime.datetime
        """
        _time_text = self._data["CreateTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def estimated_time(self):
        """ 
        get estimated time
        :rtype: datetime.datetime
        """
        return self.global_dict[self._id]["EstimatedTime"]

    def default_path(self):
        # return r"{}/{}".format(self.project_step().code(), self.software().code())
        return self.project_step().path()

    def path(self):
        _path = self.default_path()
        # project entity
        _project_entity = zfused_api.zFused.get("project_entity", filter = { "ProjectId": self._data.get("ProjectId"),
                                                                             "Code": self.object()} )
        if _project_entity:
            _project_entity = _project_entity[0]
            _custom_path = _project_entity.get("CustomPath")
            if _custom_path:
                _path = self.get_custom_path(_custom_path)
        return _path

    def production_path(self):
        """
        get task production path
        rtype: str
        """
        _link_path = zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"]).production_path()
        _path = "{}/{}".format(_link_path, self.path())
        return _path
        
    def transfer_path(self):
        _link_path = self.project_entity().transfer_path()
        _path = "{}/{}".format(_link_path, self.path())
        return _path

    def backup_path(self):
        """get task backup path
        rtype: str
        """
        _link_path = zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"]).backup_path()
        _path = "{}/{}".format(_link_path, self.path())
        return _path

    def work_path(self, absolute = True):
        """get task work path
        rtype: str
        """
        _step_code = zfused_api.step.ProjectStep(self._data["ProjectStepId"]).code()
        _software_code = zfused_api.software.Software(self._data["SoftwareId"]).code()
        _link_path = zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"]).work_path(absolute)
        _path = "{}/{}/{}".format(_link_path, _step_code, _software_code)
        return _path

    def temp_path(self):
        """get task publish path
        rtype: str
        """
        _step_code = zfused_api.step.ProjectStep(self._data["ProjectStepId"]).code()
        _software_code = zfused_api.software.Software(self._data["SoftwareId"]).code()
        _link_path = zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"]).temp_path()
        _path = "{}/{}/{}".format(_link_path, _step_code, _software_code)
        return _path

    def image_path(self):
        _link_path = zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"]).image_path()
        _path = "{}/{}".format(_link_path, self.path())
        return _path

    def cache_path(self):
        _link_path = zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"]).cache_path()
        _path = "{}/{}".format(_link_path, self.path())
        return _path

    def review_path(self):
        """get task review path

        rtype: str
        """
        _step_code = zfused_api.step.ProjectStep(self._data["ProjectStepId"]).code()
        _software_code = zfused_api.software.Software(self._data["SoftwareId"]).code()
        _link_path = zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"]).review_path()
        _path = "{}/{}/{}".format(_link_path, _step_code, _software_code)
        return _path

    def link_entity(self):
        return(self.global_dict[self._id]["ProjectEntityType"], self.global_dict[self._id]["ProjectEntityId"])

    def versions(self, refresh = False):
        """ get all task publish veriosns

        :rtype: list 
        """
        if refresh:
            _versions = self.get("version", filter = {"TaskId": self._id})
            if not _versions:
                self.global_versions[self._id] = []
            else:
                self.global_versions[self._id] = _versions

        if self._id not in self.global_versions.keys() or zfused_api.zFused.RESET:
            _versions = self.get("version", filter = {"TaskId": self._id})
            if not _versions:
                self.global_versions[self._id] = []
            else:
                self.global_versions[self._id] = _versions

        return self.global_versions[self._id]

    def last_version_id(self, is_approval = 1):
        if self.is_sub_task():
            return zfused_api.task.Task(self.parent_task_id()).last_version_id(is_approval)

        if is_approval:
            _versions = self.get("version", filter = {"TaskId":self._id, "IsApproval": 1})
        else:
            _versions = self.get("version", filter = {"TaskId":self._id})
        if _versions:
            return _versions[-1]["Id"]
        else:
            return 0

    def last_version_index(self, is_approval = 1):
        """get last version
        :rtype: int
        """
        if self.is_sub_task():
            return zfused_api.task.Task(self.parent_task_id()).last_version_index(is_approval)
        if is_approval:
            _versions = self.get("version", filter = {"TaskId":self._id, "IsApproval": 1})
        else:
            _versions = self.get("version", filter = {"TaskId":self._id})
        if _versions:
            return len(_versions)
        else:
            return 0

    def thumbnail(self):
        """ get thumbnai name
        """
        _thumbnail = self._data["Thumbnail"]
        return _thumbnail

    def get_thumbnail(self, is_version = True):
        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None        

    def notes(self):
        """ get tasks notes
                history
                version
                message
        :rtype: list
        """
        _notes = []
        _historys = self.get("task_history", filter = {"TaskId": self._id})
        if not _historys:
            _data = self._data
            _note = {"user_id": _data["CreatedBy"],
                     "notes": _data,
                     "type": "create",
                     "time": _data["CreatedTime"]}
            _notes.append(_note)
        else:
            _data = _historys[0]
            _note = {"user_id": _data["CreatedBy"],
                     "notes": _data,
                     "type": "create",
                     "time": _data["CreatedTime"]}
            _notes.append(_note)
        if _historys:
            if len(_historys) > 1:
                for _history in _historys:
                    _his_notes = []
                    for _key, _value in _history.items():
                        if _key in ["CreatedTime", "Id", "ChangedTime", "ChangeBy"]:
                            continue
                        if _value != _data[_key]:
                            _note = { _key: _value }
                            _his_notes.append(_note)
                    if _his_notes:
                        _note = {"user_id": _history["ChangeBy"],
                                 "time": _history["ChangeTime"],
                                 "notes":_his_notes,
                                 "type": "change"}
                        _notes.append(_note)
                    _data = _history
        # get task version
        _versions = self.get("version", filter = {"TaskId": self._id})
        if _versions:
            for _version in _versions:
                _note = {"user_id": _version["CreatedBy"],
                         "time": _version["CreatedTime"],
                         "notes":_version,
                         "type": "version"}
                _notes.append(_note)

        def get_sort(elem):
            return elem["time"]
        _notes.sort(key = get_sort)

        return _notes

    def submit_external_approval( self, name, 
                                        file_path,
                                        approver_id = [],
                                        cc_id = [],
                                        description = None ):
        _approver_id = approver_id[-1]
        _create_by = zfused_api.zFused.USER_ID
        _create_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _user_id = _create_by
        _project_id = self.project_id()
        _step_id = self.project_step().step_id()
        _project_step_id = self.project_step_id()
        _project_entity_type = self.project_entity_type()
        _project_entity_id = self.project_entity_id()
        _task_id = self._id
        # index
        _all_version = self.get("version", filter = {"TaskId": self._data["Id"]})
        _index = 0
        if _all_version:
            _last_version = _all_version[-1]
            if _last_version["IsApproval"] == 1:
                _index = len(_all_version) + 1
            else:
                # _last_version["Introduction"] = introduction
                _last_version["Description"] = description
                _last_version["UserId"] = _create_by
                # _last_version["CreateTime"] = _create_time
                _last_version["IsApproval"] = 0
                _last_version["CreatedBy"] = _create_by
                _last_version["CreatedTime"] = _create_time
                # _last_version["Record"] = record
                self.put("version", _last_version["Id"], _last_version)
        else:
            _index = 1
        if _index:
            _last_version, _status = self.post(key = "version", data = { "Name": name,
                                                                         "ProjectId":_project_id,
                                                                         "StepId":_step_id,
                                                                         "ProjectStepId": _project_step_id,
                                                                         "ProjectEntityType": _project_entity_type,
                                                                         "ProjectEntityId": _project_entity_id,
                                                                         "TaskId":_task_id,
                                                                         "Index":_index,
                                                                         "Thumbnail":"",
                                                                         "ThumbnailPath":"",
                                                                         "Description":description,
                                                                         "Introduction":"",
                                                                         "Record": "",
                                                                         "CreatedBy": _create_by,
                                                                         "CreatedTime": _create_time,
                                                                         "FilePath":file_path,
                                                                         "MovePath":"",
                                                                         "IsNegligible": 0,
                                                                         "IsApproval": 0, 
                                                                         "UserId": _create_by,
                                                                         "CreateTime": _create_time,
                                                                         "IsExternal": 1 } )
            if not _status:
                return False, "{} submit error".format(name)
        _version_id = _last_version["Id"]

        # 提交最后版本id
        self.update_last_version_id(_version_id)

        # 提交审查人员
        _value, _status = self.post(key = "approval", data = { "Object": "version", 
                                                               "ObjectId": _version_id, 
                                                               "ApproverId": _approver_id,
                                                               "Status":"0",
                                                               "SubmitterId": _user_id,
                                                               "SubmitTime": _create_time,
                                                               "CreatedBy": _user_id,
                                                               "CreatedTime": _create_time,
                                                               "ThumbnailPath": "",
                                                               "Description": description,
                                                               "Introduction": "",
                                                               "Record": "" })
        if not _status:
            return False,"%s approval create error"%name
        _approver_id = _value["Id"]

        # 抄送人员
        if cc_id:
            for _cc_id in cc_id:
                self.post(key = "cc", data = { "Object": "version",
                                               "ObjectId": _version_id, 
                                               "UserId": _cc_id,
                                               "CreatedBy": _user_id,
                                               "CreatedTime": _create_time })

        # 组成员 新添加组成员
        _user_ids = list(set(approver_id + cc_id + [_user_id]))
        _group_users = self.get("group_user", filter = {"EntityType":"task", "EntityId":self._id})
        if _group_users:
            for _group_user in _group_users:
                _user_id_un = int(_group_user["UserId"])
                if _user_id_un in _user_ids:
                    _user_ids.remove(_user_id_un)
        if _user_ids:
            for _user_id_un in _user_ids:
                self.post( "group_user", { "EntityType":"task", 
                                           "EntityId":self._id, 
                                           "UserId":_user_id_un,
                                           "CreatedBy": _user_id,
                                           "CreatedTime": _create_time })
        
        _user_ids = list(set(approver_id + cc_id + [_user_id]))
        #  发送通知信息
        _user_id = zfused_api.zFused.USER_ID
        zfused_api.im.submit_message( "user",
                                      _user_id,
                                      _user_ids, #approver_id + cc_id + [_user_id],
                                      {"entity_type": "version",
                                       "entity_id": _version_id},
                                      "approval", 
                                      "approval",
                                      _approver_id,
                                      "task",
                                      self._id )
        
        # 修改为审批状态
        _approval_status_ids = zfused_api.status.approval_status_ids()
        if _approval_status_ids:
            _strs = [str(_approval_status_id) for _approval_status_id in _approval_status_ids]
            _status_list = zfused_api.zFused.get("project_status", filter = {"ProjectId": self._data["ProjectId"], "StatusId__in":"|".join(_strs)})
            if _status_list:
                self.update_status(_status_list[0]["StatusId"])        
        self.update_approval_status("0")

        return _version_id, "%s submit approval success"%name

    
    def submit_approval( self, name,
                               file_path, 
                               user_id,
                               approver_id = [], 
                               cc_id = [], 
                               move_path = None, 
                               thumbnail = None, 
                               thumbnail_path = None,
                               description = None,
                               introduction = None,
                               record = None ):
        """ submit approval
        :rtype: [int, str]
        """
        _approver_id = approver_id[-1]
        _create_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        # project infomation
        _project_id = self._data["ProjectId"]
        _project_step_id = self._data["ProjectStepId"]
        _step_id = self._data["StepId"]
        _object = self._data["ProjectEntityType"]
        _link_id = self._data["ProjectEntityId"]
        _task_id = self._data["Id"]
        _user_id = user_id
        # index
        _all_version = self.get("version", filter = {"TaskId": self._data["Id"]})
        _index = 0
        if _all_version:
            _last_version = _all_version[-1]
            if _last_version["IsApproval"] == 1:
                _index = len(_all_version) + 1
            else:
                _last_version["Introduction"] = introduction
                _last_version["Description"] = description
                _last_version["UserId"] = _user_id
                _last_version["CreateTime"] = _create_time
                _last_version["IsApproval"] = 0
                _last_version["CreatedBy"] = _user_id
                _last_version["CreatedTime"] = _create_time
                _last_version["Record"] = record
                self.put("version", _last_version["Id"], _last_version)
        else:
            _index = 1
        if _index:
            _last_version, _status = self.post(key = "version", data = { "Name": name,
                                                                         "ProjectId":_project_id,
                                                                         "StepId":_step_id,
                                                                         "ProjectStepId": _project_step_id,
                                                                         "ProjectEntityType": _object,
                                                                         "ProjectEntityId": _link_id,
                                                                         "TaskId":_task_id,
                                                                         "Index":_index,
                                                                         "Thumbnail":thumbnail,
                                                                         "ThumbnailPath": thumbnail_path,
                                                                         "Description":description,
                                                                         "Introduction":introduction,
                                                                         "Record": record,
                                                                         "CreatedBy":_user_id,
                                                                         "CreatedTime":_create_time,
                                                                         "FilePath":file_path,
                                                                         "MovePath":move_path,
                                                                         "IsNegligible": 0,
                                                                         "IsApproval": 0, 
                                                                         "UserId": _user_id,
                                                                         "CreateTime": _create_time } )
            if not _status:
                return False, "{} submit error".format(name)
        _version_id = _last_version["Id"]
        
        # 提交最后版本id
        self.update_last_version_id(_version_id)

        # 提交任务图片
        if not self._data.get("ThumbnailPath"):
            self.update_thumbnail_path(thumbnail_path)

        # 提交project_entity缩略图
        try:
            _project_entity = self.project_entity()
            _project_entity.update_thumbnail_path(thumbnail_path)
            # if not _project_entity.data().get("ThumbnailPath"):
            #     _project_entity.update_thumbnail_path(thumbnail_path)
            # if not zfused_api.objects.Objects(_object, _link_id).data().get("ThumbnailPath"):
            #     zfused_api.objects.Objects(_object, _link_id).update_thumbnail_path(thumbnail_path)
        except:
            pass

        # # 提交 file link
        # if introduction:
        #     _dicts = []
        #     _images = introduction.get("image")
        #     _documents = introduction.get("document")
        #     if _images:
        #         _dicts += _images
        #     if _documents:
        #         _dicts += _documents
        #     if _dicts:
        #         for _dict in _dicts:
        #             pass

        # 提交审查人员
        _value, _status = self.post(key = "approval", data = { "Object": "version", 
                                                               "ObjectId": _version_id, 
                                                               "ApproverId": _approver_id,
                                                               "Status":"0",
                                                               "SubmitterId": _user_id,
                                                               "SubmitTime": _create_time,
                                                               "CreatedBy": _user_id,
                                                               "CreatedTime": _create_time,
                                                               "ThumbnailPath": thumbnail_path,
                                                               "Description": description,
                                                               "Introduction": introduction,
                                                               "Record": record })
        if not _status:
            return False,"%s approval create error"%name
        _approver_id = _value["Id"]

        # 抄送人员
        if cc_id:
            for _cc_id in cc_id:
                self.post(key = "cc", data = { "Object": "version",
                                               "ObjectId": _version_id, 
                                               "UserId": _cc_id,
                                               "CreatedBy": _user_id,
                                               "CreatedTime": _create_time })

        # 组成员 新添加组成员
        _user_ids = list(set(approver_id + cc_id + [_user_id]))
        _group_users = self.get("group_user", filter = {"EntityType":"task", "EntityId":self._id})
        if _group_users:
            for _group_user in _group_users:
                _user_id_un = int(_group_user["UserId"])
                if _user_id_un in _user_ids:
                    _user_ids.remove(_user_id_un)
        if _user_ids:
            for _user_id_un in _user_ids:
                self.post( "group_user", { "EntityType":"task", 
                                           "EntityId":self._id, 
                                           "UserId":_user_id_un,
                                           "CreatedBy": _user_id,
                                           "CreatedTime": _create_time })
        
        _user_ids = list(set(approver_id + cc_id + [_user_id]))
        #  发送通知信息
        _user_id = zfused_api.zFused.USER_ID
        # 取消发送个人消息
        # zfused_api.im.submit_message( "user",
        #                               _user_id,
        #                               approver_id + cc_id + [_user_id],
        #                               {"entity_type": "version",
        #                                "entity_id": _version_id},
        #                               "approval", 
        #                               "approval",
        #                               _approver_id )

        zfused_api.im.submit_message( "user",
                                      _user_id,
                                      _user_ids, #approver_id + cc_id + [_user_id],
                                      {"entity_type": "version",
                                       "entity_id": _version_id},
                                      "approval", 
                                      "approval",
                                      _approver_id,
                                      "task",
                                      self._id )
        
        # 修改为审批状态
        _approval_status_ids = zfused_api.status.approval_status_ids()
        if _approval_status_ids:
            _strs = [str(_approval_status_id) for _approval_status_id in _approval_status_ids]
            _status_list = zfused_api.zFused.get("project_status", filter = {"ProjectId": self._data["ProjectId"], "StatusId__in":"|".join(_strs)})
            if _status_list:
                self.update_status(_status_list[0]["StatusId"])
        
        self.update_approval_status("0")
        # update approval process id

        #发送系统通知
        return _version_id, "%s submit approval success"%name


    def submit_review(self, name,
                            # user_id,
                            review_process_id = 0,
                            reviewer_ids = [], 
                            ccer_ids = [], 
                            # file_path, 
                            # move_path = None, 
                            thumbnail_path = None, 
                            description = None,
                            introduction = None,
                            layer_id = 0 ):
        """ submit approval
        :rtype: [int, str]
        """
        _reviewer_id = reviewer_ids[-1]
        _create_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        # project infomation
        _project_id = self._data["ProjectId"]
        _project_step_id = self._data["ProjectStepId"]
        _step_id = self._data["StepId"]
        _object = self._data["ProjectEntityType"]
        _link_id = self._data["ProjectEntityId"]
        _task_id = self._data["Id"]
        _user_id = zfused_api.zFused.USER_ID
        
        # index
        _all_review = self.get("report", filter = { "TaskId": _task_id })
        _index = 0
        if _all_review:
            # _last_version = _all_review[-1]
            _index = len(_all_review) + 1
        else:
            _index = 1
        
        _layer_id = layer_id
        _layer_index = 0
        if _layer_id:
            _layers = self.get("report", filter = { "TaskId": _task_id, "LayerId": _layer_id })
            if _layers:
                # _last_layer_version = _all_review[-1]
                _layer_index = len(_layers) + 1
            else:
                _layer_index = 1
        
        _report_id = 0
        if _index:
            if _layer_index:
                _layer_handle = zfused_api.step.ProjectStepLayer(_layer_id)
                _name = "{}.{}.{}".format(name, _layer_handle.code(), str(_layer_index).zfill(4))
            else:
                _name = "{}.{}".format(name, str(_index).zfill(4))
            _text,_status = self.post(key = "report", data = {
                                                               "ProjectId": _project_id,
                                                               "ProjectStepId": _project_step_id,
                                                               "ProjectEntityType": _object,
                                                               "ProjectEntityId": _link_id,
                                                               # "EntityType": "task",
                                                               # "EntityId": _task_id,
                                                               "TaskId": _task_id,
                                                               "Name": _name,
                                                               "Index":_index,
                                                               "ThumbnailPath":thumbnail_path,
                                                               "Description": description,
                                                               "Introduction": introduction,
                                                               "CreatedBy": _user_id,
                                                               "CreatedTime":_create_time,
                                                               "LayerId": _layer_id,
                                                               "LayerIndex": _layer_index,
                                                              })
            if not _status:
                return False, "{} submit error".format(name)
            _report_id = _text.get("Id")

        if not _report_id:
            return False, "{} review create error".format(name)

        # 提交最后版本id
        self.update_last_report_id(_report_id)

        # 提交任务图片
        self.update_thumbnail_path(thumbnail_path)
        # 提交project_entity缩略图
        try:
            self.project_entity().update_thumbnail_path(thumbnail_path)
        except:
            pass

        # 提交审查人员
        _text,_status = self.post(key = "review", data = { "EntityType": "report", 
                                                           "EntityId": _report_id, 
                                                           "ReviewProcessId": review_process_id,
                                                           "ReviewerId": _reviewer_id,
                                                           "Status":"0",
                                                           "SubmitterId": _user_id,
                                                           "SubmitTime": _create_time,
                                                           "ThumbnailPath": thumbnail_path,
                                                           "Description": description,
                                                           "Introduction": introduction,
                                                           "CreatedBy": _user_id,
                                                           "CreatedTime":_create_time } )
        if not _status:
            # remove report id
            self.delete("report", _report_id)
            return False,"%s review create error"%name
        _review_id = _text.get("Id")
        if not _review_id:
            # remove report id
            self.delete("report", _report_id)
            return False, "{} review create error".format(name)

        # 提交审核记录
        _,_status = self.post(key = "review_record", data = { "ReviewId": _review_id,
                                                              "ReviewProcessId": review_process_id,
                                                              "CreatedBy": _user_id,
                                                              "CreatedTime":_create_time } )
        if not _status:
            # remove report id
            self.delete("report", _report_id)
            # remove review id
            self.delete("review", _review_id)
            return False, "{} review create error".format(name)
        # # 抄送人员
        # if ccer_ids:
        #     for _ccer_id in ccer_ids:
        #         self.post(key = "cc", data = {"Object": "report",
        #                                       "ObjectId": _report_id, 
        #                                       "UserId": _ccer_id})

        #  发送通知信息
        # 组成员 新添加组成员
        _user_ids = list(set(reviewer_ids + ccer_ids + [_user_id]))
        _group_users = self.get("group_user", filter = {"EntityType":"task", "EntityId":self._id})
        if _group_users:
            for _group_user in _group_users:
                _user_id_un = int(_group_user["UserId"])
                if _user_id_un in _user_ids:
                    _user_ids.remove(_user_id_un)
        if _user_ids:
            for _user_id_un in _user_ids:
                self.post( "group_user", { "EntityType":"task", 
                                           "EntityId":self._id, 
                                           "UserId":_user_id_un,
                                           "CreatedBy": _user_id,
                                           "CreatedTime": _create_time })

        _user_ids = list(set(reviewer_ids + ccer_ids + [_user_id]))
        _user_id = zfused_api.zFused.USER_ID
        # 取消消息发送个人
        # zfused_api.im.submit_message( "user",
        #                               _user_id,
        #                               reviewer_ids + ccer_ids + [_user_id],
        #                               {"entity_type": "report",
        #                                "entity_id": _report_id},
        #                               "review", 
        #                               "review",
        #                               _review_id)
        zfused_api.im.submit_message( "user",
                                      _user_id,
                                      _user_ids, # reviewer_ids + ccer_ids + [_user_id],
                                      {"entity_type": "report",
                                       "entity_id": _report_id},
                                      "review", 
                                      "review",
                                      _review_id,
                                      "task",
                                      self._id )

        #发送系统通知
        #im.submit_message(['192.168.103.19',5672],{"msgtype":"review","review":{"review_id":id,"title":"Title"}},"user",34,[111,34])
        
        try:
            # 修改为qc审核状态
            _review_status_ids = zfused_api.status.review_status_ids()
            if _review_status_ids:
                _strs = [str(_review_status_id) for _review_status_id in _review_status_ids]
                _status_list = zfused_api.zFused.get("project_status", filter = {"ProjectId": self._data["ProjectId"], "StatusId__in":"|".join(_strs)})
                if _status_list:
                    self.update_status(_status_list[0]["StatusId"])

            self.update_review_status( "0" )
            self.update_review_process( review_process_id )
        except:
            pass

        return _report_id, "%s submit review success"%name


    def is_production(self):
        if "IsProduction" not in self.global_dict[self._id]:
            return 0
        return self.global_dict[self._id]["IsProduction"]

    def analy_is_production(self):
        """ 判定当前任务是否为产品最终任务
        """
        _message = ""
        # get version
        _index = self.last_version_index()
        if _index == 0:
            self.global_dict[self._id]["IsProduction"] = -1 #, "no versions")
            return -1, "no versions"
        # get input versions
        _versions = self.get("relative", filter = {"SourceObject": "version","TargetObject": "task", "TargetId": self._id})
        if not _versions:
            self.global_dict[self._id]["IsProduction"] = 1 #, "")
            return 1, _message

        _is_production = 1
        for _version in _versions:
            _version = self.get("version", filter = {"Id": _version["SourceId"]})[0]
            _task = self.get("task", filter = {"Id": _version["TaskId"]})[0]
            _versions = self.get("version", filter = {"TaskId":_task["Id"]})
            if _versions[-1]["Id"] != _version["Id"]:
                _is_production = -1
                _message += "version {} is not last version for task {} \n".format(_version["Id"], _task["Id"])
            else:
                _message += "version {} is last version for task {} \n".format(_version["Id"], _task["Id"])
        self.global_dict[self._id]["IsProduction"] = _is_production #, _message)
        # return _is_production, _message

    def input_tasks(self):
        """ get input tasks
        :rtype: dict
        """
        tasks = OrderedDict()

        _project_step = self.project_step()
        _input_attrs = _project_step.input_attrs()
        _is_new_attribute_solution = _project_step.is_new_attribute_solution()
        # get input project step 
        # _input_attrs = self.get("step_attr_input", filter = {"ProjectStepId":self._data["ProjectStepId"]})
        if not _input_attrs:
            return tasks
        if _is_new_attribute_solution:
            _st = time.time()
            for _input_attr in _input_attrs:
                # _rule = "single"
                _rule = _input_attr.get("Rule")
                _rely = _input_attr.get("Rely")
                _attr_conns = self.get("attr_conn", filter = {"AttrInputId": _input_attr.get("Id")})
                if not _attr_conns:
                    continue
                    
                if _rely == "self":
                    for _attr_conn in _attr_conns:
                        # 自身关联任务链接
                        _attr_output_id = _attr_conn.get("AttrOutputId")
                        _attr_output = zfused_api.attr.Output(_attr_output_id)
                        _attr_output_project_step = _attr_output.project_step()
                        _tasks = self.get("task",filter = { "ProjectStepId": _attr_output_project_step.id(), 
                                                            "ProjectEntityType": self.project_entity_type(), 
                                                            "ProjectEntityId": self.project_entity_id() })
                        if _tasks:
                            if _attr_conn["Id"] not in tasks:
                                tasks[_attr_conn["Id"]] = []
                            tasks[_attr_conn["Id"]] += _tasks
                        
                            if _rule == "single":
                                break

                elif _rely == "asset" or _rely == "assembly":
                    _relative_tasks = defaultdict(list) 

                    _relatives = self.get("relative", filter = { "SourceObject": _rely,
                                                                    "TargetObject": self.project_entity_type(), 
                                                                    "TargetId": self.project_entity_id() })
                    if not _relatives:
                        continue
                    
                    for _relative in _relatives:
                        if _rule == "latest":
                            # 获取最新的关联任务
                            _latest_time = None
                            _latest_conn_id = 0
                            _latest_task = None
                            for _attr_conn in _attr_conns:
                                _attr_output_id = _attr_conn.get("AttrOutputId")
                                _attr_output = zfused_api.attr.Output(_attr_output_id)
                                _attr_output_project_step = _attr_output.project_step()
                                _attr_output_rule = _attr_output.rule()
                                _attr_output_rely = _attr_output.rely()

                                _conn_id = _attr_conn["Id"]
                                if _attr_output_rely == _rely:
                                    _output_tasks = self.get("task", filter = { "ProjectStepId": _attr_output_project_step.id(), 
                                                                                "ProjectEntityType": self.project_entity_type(), 
                                                                                "ProjectEntityId": self.project_entity_id() })
                                    if _output_tasks:
                                        _output_task = _output_tasks[0]
                                        _output_task["NameSpace"] = _relative.get("NameSpace")
                                        _files = zfused_api.zFused.get("production_file", filter = { "ProjectStepId": _attr_output_project_step.id(), 
                                                                                                     "ProjectStepAttrId": _attr_output_id,
                                                                                                     "ProjectEntityType": self.project_entity_type(), 
                                                                                                     "ProjectEntityId": self.project_entity_id(),
                                                                                                     "TaskId": _output_task.get("Id"),
                                                                                                     "RelativeEntityType": _relative.get("SourceObject"),
                                                                                                     "RelativeEntityId": _relative.get("SourceId"),
                                                                                                     "RelativeNameSpace": _relative.get("NameSpace") },
                                                                                          fields = ["Id", "CreatedTime"] )
                                        _file_time = None
                                        if _files:
                                            _file_time = _files[-1].get("CreatedTime")
                                        else:
                                            _output_task_entity = zfused_api.task.Task(_output_task.get("Id"))
                                            _file = '{}/{}/{}{}'.format(_output_task_entity.cache_path(),_attr_output.code(),_relative.get("NameSpace"),_attr_output.suffix())
                                            if os.path.isfile(_file):
                                                _file_time = os.path.getmtime(_file)
                                                _file_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(_file_time))
                                        if _file_time:
                                            if not _latest_time or _latest_time < _file_time:
                                                _latest_time = _file_time
                                                _latest_conn_id = _conn_id
                                                _latest_task = _output_task
                                else:
                                    _output_tasks = self.get("task", filter = { "ProjectStepId": _attr_output_project_step.id(), 
                                                                                "ProjectEntityType": _relative.get("SourceObject"),
                                                                                "ProjectEntityId": _relative.get("SourceId") })
                                    if _output_tasks:
                                        _output_task = _output_tasks[0]
                                        _output_task["NameSpace"] = _relative.get("NameSpace")
                                        _files = zfused_api.zFused.get("production_file", filter = { "ProjectStepId": _attr_output_project_step.id(), 
                                                                                                     "ProjectStepAttrId": _attr_output_id,
                                                                                                     "ProjectEntityType": self.project_entity_type(), 
                                                                                                     "ProjectEntityId": self.project_entity_id(),
                                                                                                     "TaskId": _output_task.get("Id") },
                                                                                          fields = ["Id", "CreatedTime"] )
                                        if _files:
                                            _file_time = _files[-1].get("CreatedTime")
                                        else:
                                            _output_task_entity = zfused_api.task.Task(_output_task.get("Id"))
                                            _file = '{}/{}/{}{}'.format(_output_task_entity.cache_path(),_attr_output.code(),_relative.get("NameSpace"),_attr_output.suffix())
                                            if os.path.isfile(_file):
                                                _file_time = os.path.getmtime(_file)
                                                _file_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(_file_time))
                                        if _file_time:
                                            if not _latest_time or _latest_time < _file_time:
                                                _latest_time = _file_time
                                                _latest_conn_id = _conn_id
                                                _latest_task = _output_task

                            if _latest_task:
                                _relative_tasks[_latest_conn_id].append(_latest_task)                                
                        else:
                            for _attr_conn in _attr_conns:
                                _attr_output_id = _attr_conn.get("AttrOutputId")
                                _attr_output = zfused_api.attr.Output(_attr_output_id)
                                _attr_output_project_step = _attr_output.project_step()
                                _attr_output_rule = _attr_output.rule()
                                _attr_output_rely = _attr_output.rely()

                                _task = {}
                                if _attr_output_rely == _rely:
                                    _tasks = self.get("task", filter = { "ProjectStepId": _attr_output_project_step.id(), 
                                                                         "ProjectEntityType": self.project_entity_type(), 
                                                                         "ProjectEntityId": self.project_entity_id() })
                                    if _tasks:
                                        _task = _tasks[0]
                                        _task["NameSpace"] = _relative.get("NameSpace")
                                else:
                                    _tasks = self.get("task", filter = { "ProjectStepId": _attr_output_project_step.id(), 
                                                                         "ProjectEntityType": _relative.get("SourceObject"),
                                                                         "ProjectEntityId": _relative.get("SourceId") })
                                    if _tasks:
                                        _task = _tasks[0]
                                        _task["NameSpace"] = _relative.get("NameSpace")
                                if _task:
                                    _relative_tasks[_attr_conn["Id"]].append(_task)

                    if not _relative_tasks:
                        continue
                    
                    for _k, _v in _relative_tasks.items():
                        if _k not in tasks:
                            tasks[_k] = []
                        tasks[_k] += _v

                    """

                    for _attr_conn in _attr_conns:
                        _attr_output_id = _attr_conn.get("AttrOutputId")
                        _attr_output = zfused_api.attr.Output(_attr_output_id)
                        _attr_output_project_step = _attr_output.project_step()
                        _attr_output_rule = _attr_output.rule()
                        _attr_output_rely = _attr_output.rely()
                        # get relative object
                        _relatives = self.get("relative", filter = { "SourceObject": _rely,
                                                                     "TargetObject": self.project_entity_type(), 
                                                                     "TargetId": self.project_entity_id() })
                        if not _relatives:
                            continue
                        for _relative in _relatives:
                            _task = {}
                            if _attr_output_rely == _rely:
                                _tasks = self.get("task", filter = { "ProjectStepId": _attr_output_project_step.id(), 
                                                                     "ProjectEntityType": self.project_entity_type(), 
                                                                     "ProjectEntityId": self.project_entity_id() })
                                if _tasks:
                                    _task = _tasks[0]
                                    _task["NameSpace"] = _relative.get("NameSpace")
                            else:
                                _tasks = self.get("task", filter = { "ProjectStepId": _attr_output_project_step.id(), 
                                                                     "ProjectEntityType": _relative.get("SourceObject"),
                                                                     "ProjectEntityId": _relative.get("SourceId") })
                                if _tasks:
                                    _task = _tasks[0]
                                    _task["NameSpace"] = _relative.get("NameSpace")
                            if _task:

                                _relative_tasks[_attr_conn["Id"]].append(_task)
                        
                        if _rule == "single":
                            continue

                    if not _relative_tasks:
                        continue
                    
                    if _rule == "latest":
                        # 获取最新的文件
                        for _k, _v in _relative_tasks.items():
                            tasks[_k] += _v


                    
                    #
                    for _attr_conn in _attr_conns:
                        _attr_output_id = _attr_conn.get("AttrOutputId")
                        _attr_output = zfused_api.attr.Output(_attr_output_id)
                        _attr_output_project_step = _attr_output.project_step()
                        _attr_output_rule = _attr_output.rule()
                        _attr_output_rely = _attr_output.rely()
                        # get relative object
                        _relatives = self.get("relative", filter = { "SourceObject": _rely,
                                                                     "TargetObject": self.project_entity_type(), 
                                                                     "TargetId": self.project_entity_id() })
                        if not _relatives:
                            continue
                        for _relative in _relatives:
                            _task = {}
                            if _attr_output_rely == _rely:
                                _tasks = self.get("task", filter = { "ProjectStepId": _attr_output_project_step.id(), 
                                                                     "ProjectEntityType": self.project_entity_type(), 
                                                                     "ProjectEntityId": self.project_entity_id() })
                                if _tasks:
                                    _task = _tasks[0]
                                    _task["NameSpace"] = _relative.get("NameSpace")
                                    # tasks[_attr_conn["Id"]].append(_task)
                            else:
                                _tasks = self.get("task", filter = { "ProjectStepId": _attr_output_project_step.id(), 
                                                                     "ProjectEntityType": _relative.get("SourceObject"),
                                                                     "ProjectEntityId": _relative.get("SourceId") })
                                if _tasks:
                                    _task = _tasks[0]
                                    _task["NameSpace"] = _relative.get("NameSpace")
                            if _task:
                                tasks[_attr_conn["Id"]].append(_task)
                                    
                        if _rule == "single":
                            break
                    """

                # # 获取属性关联
                # _attr_conns = self.get("attr_conn", filter = {"AttrInputId": _input_attr.get("Id")})
                # if _attr_conns:
                #     # 获取链接属性的上游输出属性 get _attr_output_id
                #     _attr_conn = _attr_conns[0]
                #     _mode = _attr_conn.get("Mode")
                #     if _mode == "direct":
                #         _attr_output_id = _attr_conn.get("AttrOutputId")
                #         _attr_output = zfused_api.attr.Output(_attr_output_id)
                #         _attr_output_project_step_id = _attr_output.project_step_id()
                #         _tasks = self.get("task",filter = { "ProjectStepId":_attr_output_project_step_id, 
                #                                             "ProjectEntityType":self.project_entity_type(), 
                #                                             "ProjectEntityId": self.project_entity_id() })
                #         # 任务状态机制?
                #         if _tasks:
                #             tasks[_attr_conn["Id"]] += _tasks

        else:
            for _input_attr in _input_attrs:
                if _input_attr["Id"] not in tasks:
                    tasks[_input_attr["Id"]] = []
                if _input_attr["Mode"] == "indirect":
                    _attr = self.get("step_attr_output", filter = {"Id":_input_attr["StepAttrId"]})
                    if not _attr:
                        continue
                    _attr_project_step_id = _attr[0]["ProjectStepId"]
                    task = self.get("task",filter = {"ProjectStepId":_attr_project_step_id, "ProjectEntityId":self._data["ProjectEntityId"]})
                    # 任务状态机制?
                    _is_next = False
                    if task:
                        _task_handle = zfused_api.task.Task(task[0]["Id"])
                        if _task_handle.versions():
                            tasks[_input_attr["Id"]] += task
                        else:
                            _is_next = True
                        # tasks[_input_attr["Id"]] += task
                    else:
                        _is_next = True
                    if _is_next:
                        # 如果没有对应任务,加载次任务上级任务                        
                        logger.info(u"获取关联任务-------------------------")
                        # 获取关联任务的步骤
                        # 为了配合有的有解算有的无解算的问题？？？
                        _step_attr = self.get("step_attr_input",filter = {"ProjectStepId":_attr_project_step_id,"Mode":"direct"})
                        if _step_attr:
                            _project_step_id = self.get("step_attr_output", filter = {"Id":_step_attr[0]["StepAttrId"]})[0]["ProjectStepId"]
                            _task = self.get("task", filter = {"ProjectEntityId":self._data["ProjectEntityId"],"ProjectStepId":_project_step_id})
                            if _task:
                                # tasks[_step_attr[0]["Id"]] = _task
                                tasks[_input_attr["Id"]] = _task
                elif _input_attr["Mode"] == "direct":
                    _attr = self.get("step_attr_output", filter = {"Id":_input_attr["StepAttrId"]})
                    if not _attr:
                        continue
                    _attr_project_step_id = _attr[0]["ProjectStepId"]
                    task = self.get("task", filter = {"ProjectStepId":_attr_project_step_id, "ProjectEntityId":self._data["ProjectEntityId"]})
                    # 任务状态机制?
                    if task:
                        tasks[_input_attr["Id"]] += task
                elif _input_attr["Mode"] == "root":
                    _attr = self.get("step_attr_output", filter = {"Id":_input_attr["StepAttrId"]})
                    if not _attr:
                        continue
                    _attr_project_step_id = _attr[0]["ProjectStepId"]
                    _project_step_handle = zfused_api.step.ProjectStep(_attr_project_step_id)
                    _root_entity_type = _project_step_handle.data().get("Object")
                    
                    if _root_entity_type == "sequence":
                        _sequence_id = self.entity().data().get("SequenceId")
                        task = self.get("task",filter = { "ProjectStepId":_attr_project_step_id, "ProjectEntityId":_sequence_id })
                    # 任务状态机制?
                    if task:
                        tasks[_input_attr["Id"]] += task

                elif _input_attr["Mode"] == "relative":
                    _attr = self.get("step_attr_output", filter = {"Id":_input_attr["StepAttrId"]})
                    if not _attr:
                        continue
                    _attr_project_step_id = _attr[0]["ProjectStepId"]
                    projectStepHandle = self.get("project_step", filter = {"Id":_attr_project_step_id})[0]
                    tarStepHandle = self.get("project_step", filter = {"Id":self._data["ProjectStepId"]})[0]
                    # get relative object
                    relatives = self.get("relative", filter = { "SourceObject": projectStepHandle["Object"],
                                                                "TargetObject": tarStepHandle["Object"],
                                                                "TargetId": self._data["ProjectEntityId"]})
                    if relatives:
                        for i in relatives:
                            task = self.get("task", filter = {"ProjectStepId":_attr_project_step_id, "ProjectEntityId":i["SourceId"]})
                            if task:
                                tasks[_input_attr["Id"]].append(task[0])
                            else:
                                # 如果没有对应任务,加载次任务上级任务                        
                                logger.info(u"获取关联任务-------------------------")
                                # 获取关联任务的步骤
                                # 为了配合有的有解算有的无解算的问题？？？
                                _step_attr = self.get("step_attr_input",filter = {"ProjectStepId":_attr_project_step_id,"Mode":"direct"})
                                # if _step_attr[0]["Id"] not in tasks.keys():
                                #     tasks[_step_attr[0]["Id"]] = []
                                if _step_attr:
                                    _project_step_id = self.get("step_attr_output", filter = {"Id":_step_attr[0]["StepAttrId"]})[0]["ProjectStepId"]
                                    _task = self.get("task", filter = {"ProjectEntityId":i["SourceId"],"ProjectStepId":_project_step_id})
                                    if _task:
                                        tasks[_input_attr["Id"]] += _task
        return tasks

    def source_relatives(self):
        """ 
        """
        _relatives = zfused_api.zFused.get("relative", filter = { "TargetObject": "task", 
                                                                  "TargetId": self._id })
        return list(set([(_relative["SourceObject"], _relative["SourceId"]) for _relative in _relatives if _relative["SourceId"] != self._id] if _relatives else []))

    def target_relatives(self):
        """
        """
        _relatives = zfused_api.zFused.get("relative", filter = { "SourceObject": "task", 
                                                                  "SourceId": self._id })
        return list(set([(_relative["TargetObject"], _relative["TargetId"]) for _relative in _relatives if _relative["TargetId"] != self._id] if _relatives else []))

    def history(self):
        """ get history

        :rtype: list
        """
        _history = self.get("task_history", filter = {"TaskId":self._id}, sortby = ["ChangeTime"], order = ["asc"])
        if _history:
            return _history
        else:
            return []

    def historys(self):
        """ get task history

        """
        if self._id not in self.global_historys.keys() or self.RESET:
            _historys = self.get("task_history", filter = {"TaskId":self._id}, sortby = ["ChangeTime"], order = ["asc"])
            self.global_historys[self._id] = _historys
        return self.global_historys[self._id]

    def update_status(self, status_id):
        """ update status
        :param status_id: 状态id
        :rtype: bool
        """
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data

        if self.status_id() == status_id:
            return 
            
        _status_handle = zfused_api.status.Status(status_id)

        # 取消同时只有一个制作任务
        if _status_handle.data()["IsWorking"] == 1:
            if self._data["AssignedTo"]:
                _is_woking_status = zfused_api.zFused.get("status", filter = {"IsWorking": 1})
                _is_woking_status_ids = [str(_status["Id"]) for _status in _is_woking_status]
                _is_wating_status = zfused_api.zFused.get("status", filter = {"IsWaiting": 1})
                _tasks = zfused_api.zFused.get("task", filter = {"StatusId__in": "|".join(_is_woking_status_ids), "AssignedTo":self._data["AssignedTo"]})
                if _tasks:
                    for _task in _tasks:
                        if _task["Id"] != self._id:
                            _task["StatusId"] = _is_wating_status[0]["Id"]
                            self.put("task", _task["Id"], _task, "status_id") 
                            self.global_dict[_task["Id"]] = _task
        elif _status_handle.category() == "done":
            # 任务完成状态，修改 is_finished
            self.global_dict[self._id]["IsFinished"] = 1
            self._data["IsFinished"] = 1

        self.global_dict[self._id]["StatusId"] = status_id
        self._data["StatusId"] = status_id
        v = self.put("task", self._data["Id"], self._data, "status_id")
        # self.global_dict[self._id] = self._data

        # 更新制作百分比
        _status_handle = zfused_api.status.Status(self.status_id())
        _percent = 0
        _percent_one = 100
        if _status_handle.data().get("Category") == "done":
            _percent += _percent_one
        else:
            _review_status = self.review_status()
            _approval_status = self.approval_status()
            if _approval_status == "1":
                if _review_status == "1" or not _review_status:
                    _percent += _percent_one*0.8
                else:
                    _percent += _percent_one*0.6
            else:
                if _approval_status:
                    _percent += _percent_one*0.2
                if _review_status:
                    _percent += _percent_one*0.2
                    if _review_status == "1":
                        _percent += _percent_one*0.2
        self.update_percent(int(_percent))

        if v:
            return True
        else:
            return False

    def update_assigned(self, user_id):
        """
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["AssignedTo"] == user_id:
            return True

        self.global_dict[self._id]["AssignedTo"] = user_id
        self._data["AssignedTo"] = user_id
        v = self.put("task", self._data["Id"], self._data, "assigned_to")
        if v:
            return True
        else:
            return False

    def update_start_time(self, time_str):
        """ update start time
        """  
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self._data["StartTime"].split("+")[0] == time_str.split("+")[0]:
            return False

        self.global_dict[self._id]["StartTime"] = time_str
        self._data["StartTime"] = time_str
        v = self.put("task", self._data["Id"], self._data, "start_time")
        if v:
            return True
        else:
            return False

    def update_end_time(self, time_str):
        """ update end time
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self._data["DueTime"].split("+")[0] == time_str.split("+")[0]:
            return False

        self.global_dict[self._id]["DueTime"] = time_str
        self._data["DueTime"] = time_str
        v = self.put("task", self._data["Id"], self._data, "due_time")
        if v:
            return True
        else:
            return False

    def update_estimated_time(self, hour):
        """ update estimated time
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self._data["EstimatedTime"] == hour:
            return False
            
        self._data["EstimatedTime"] = hour
        self.global_dict[self._id]["EstimatedTime"] = hour
        v = self.put("task", self._data["Id"], self._data, "estimated_time")
        if v:
            return True
        else:
            return False

    def update_description(self, _description):
        self.global_dict[self._id]["Description"] = _description
        self._data["Description"] = _description
        v = self.put("task", self._data["Id"], self._data, "description")
        if v:
            return True
        else:
            return False

    def update_is_production(self, is_production):
        self.global_dict[self._id]["IsProduction"] = is_production
        self._data["IsProduction"] = is_production
        v = self.put("task", self._data["Id"], self._data, "is_production", False)
        if v:
            return True
        else:
            return False

    def update_is_outsource(self, outsourcer_id = 0):
        self.global_dict[self._id]["IsOutsource"] = outsourcer_id
        self._data["IsOutsource"] = outsourcer_id
        v = self.put("task", self._data["Id"], self._data, "is_outsource")
        if v:
            return True
        else:
            return False

    def update_thumbnail(self, _thumbnail):
        """
        """
        self.global_dict[self._id]["Thumbnail"] = _thumbnail
        self._data["Thumbnail"] = _thumbnail
        v = self.put("task", self._data["Id"], self._data, "thumbnail", False)
        if v:
            return True
        else:
            return False

    def update_thumbnail_path(self, thumbnail_path):
        if self.global_dict[self._id]["ThumbnailPath"] == thumbnail_path:
            return True
        self.global_dict[self._id]["ThumbnailPath"] = thumbnail_path
        self._data["ThumbnailPath"] = thumbnail_path
        v = self.put("task", self._data["Id"], self._data, "thumbnail_path", False)
        if v:
            return True
        else:
            return False

    def update_start_frame(self, start_frame):
        _entity = self.entity()
        if _entity.object() == "shot":
            return self.entity().update_start_frame(start_frame)
        return False

    def update_end_frame(self, end_frame):
        _entity = self.entity()
        if _entity.object() == "shot":
            return self.entity().update_end_frame(end_frame)
        return False

    def review_status(self):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if "ReviewStatus" not in self.global_dict[self._id]:
            return ""
        return self.global_dict[self._id]["ReviewStatus"]

    def update_review_status(self, status):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["ReviewStatus"] == status:
            return True
        self.global_dict[self._id]["ReviewStatus"] = status
        self._data["ReviewStatus"] = status
        v = self.put("task", self._data["Id"], self._data, "review_status")

        # if status != "1":
        if self.approval_status() == "1":
            self.update_approval_status("01")

        # 更新制作百分比
        _status_handle = zfused_api.status.Status(self.status_id())
        _percent = 0
        _percent_one = 100
        if _status_handle.data().get("Category") == "done":
            _percent += _percent_one
        else:
            _review_status = self.review_status()
            _approval_status = self.approval_status()
            if _approval_status == "1":
                if _review_status == "1" or not _review_status:
                    _percent += _percent_one*0.8
                else:
                    _percent += _percent_one*0.6
            else:
                if _approval_status:
                    _percent += _percent_one*0.2
                if _review_status:
                    _percent += _percent_one*0.2
                    if _review_status == "1":
                        _percent += _percent_one*0.2
        self.update_percent(int(_percent))   

        if v:
            return True
        else:
            return False

    def update_review_process(self, process_id):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["ReviewProcessId"] == process_id:
            return True
        self.global_dict[self._id]["ReviewProcessId"] = process_id
        self._data["ReviewProcessId"] = process_id
        v = self.put("task", self._data["Id"], self._data, "review_process_id")

        # 更新制作百分比
        _status_handle = zfused_api.status.Status(self.status_id())
        _percent = 0
        _percent_one = 100
        if _status_handle.data().get("Category") == "done":
            _percent += _percent_one
        else:
            _review_status = self.review_status()
            _approval_status = self.approval_status()
            if _approval_status == "1":
                if _review_status == "1" or not _review_status:
                    _percent += _percent_one*0.8
                else:
                    _percent += _percent_one*0.6
            else:
                if _approval_status:
                    _percent += _percent_one*0.2
                if _review_status:
                    _percent += _percent_one*0.2
                    if _review_status == "1":
                        _percent += _percent_one*0.2
        self.update_percent(int(_percent))        

        if v:
            return True
        else:
            return False

    def approval_status(self):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if "ApprovalStatus" not in self.global_dict[self._id]:
            return ""
        return self.global_dict[self._id].get("ApprovalStatus")

    def update_approval_status(self, status):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id].get("ApprovalStatus") == status:
            return True

        self.global_dict[self._id]["ApprovalStatus"] = status
        self._data["ApprovalStatus"] = status
        v = self.put("task", self._data["Id"], self._data, "approval_status")

        # 判定任务状态，如果审核状态已通过，审批状态也为通过，则自动判定任务状态未完成
        # 如果任务标记过is_finished,则任务也自动标记完成
        _is_finish = False
        # if self._data.get("IsFinished") == 1:
        #     _is_finish = True
        _review_status = self.review_status()
        if _review_status == "1":
            if status == "1":
                # 审定任务为完成
                _is_finish = True
        if _is_finish and self._data.get("IsFinished") == 1:
            # get done status
            _done_status = zfused_api.status.done_status_ids()
            self.update_status(_done_status[0])

        # 更新制作百分比
        _status_handle = zfused_api.status.Status(self.status_id())
        _percent = 0
        _percent_one = 100
        if _status_handle.data().get("Category") == "done":
            _percent += _percent_one
        else:
            _review_status = self.review_status()
            _approval_status = self.approval_status()
            if _approval_status == "1":
                if _review_status == "1" or not _review_status:
                    _percent += _percent_one*0.8
                else:
                    _percent += _percent_one*0.6
            else:
                if _approval_status:
                    _percent += _percent_one*0.2
                if _review_status:
                    _percent += _percent_one*0.2
                    if _review_status == "1":
                        _percent += _percent_one*0.2
        self.update_percent(int(_percent))

        if v:
            return True
        else:
            return False

    def update_approval_process(self, process_id):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["ApprovalProcessId"] == process_id:
            return True
        self.global_dict[self._id]["ApprovalProcessId"] = process_id
        self._data["ApprovalProcessId"] = process_id
        v = self.put("task", self._data["Id"], self._data, "approval_process_id")
        if v:
            return True
        else:
            return False

    def update_performance_salary(self, salary):
        """ 更新绩效薪资
        """
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["PerformanceSalary"] == salary:
            return True
        self.global_dict[self._id]["PerformanceSalary"] = salary
        self._data["PerformanceSalary"] = salary
        v = self.put("task", self._data["Id"], self._data, "performance_salary", False)
        if v:
            return True
        else:
            return False

    def working_time(self):
        """ 计算任务制作总时间
        """
        return self.global_dict[self._id].get("ProductionTime")

    def analy_working_time(self):
        """ get work time
        """
        _history_list = self.historys()
        if not _history_list:
            _history_list = []
        _time_key = []
        for _history in _history_list:
            _status_id = _history["StatusId"]
            _status_handle = zfused_api.status.Status(_status_id)
            if len(_time_key) % 2 == 0:
                # if _history["StatusId"] in _working_status:
                if _status_handle.data()["IsWorking"] == 1:
                    _time_key.append(_history["ChangeTime"].split("+")[0].replace("T"," "))
            # 获取开始时间
            if len(_time_key) % 2 == 1:
                # if _history["StatusId"] not in _working_status:
                if _status_handle.data()["IsWorking"] != 1:
                    _time_key.append(_history["ChangeTime"].split("+")[0].replace("T"," "))
        if len(_time_key) % 2 == 1:
            _time_key.append(time.strftime('%Y-%m-%d %H:%M:%S'))
        _hours = 0.0
        if _time_key:
            for i in range(int(len(_time_key)/2)):
                _k = i*2
                _t_s = _time_key[_k].split(" ")[0].split("-")
                _h_s = _time_key[_k].split(" ")[1].split(":")
                _t_e = _time_key[_k+1].split(" ")[0].split("-")
                _h_e = _time_key[_k+1].split(" ")[1].split(":")
                _hours_handle_1 = worktime.WorkHours( datetime.datetime(int(_t_s[0]),int(_t_s[1]),int(_t_s[2]),int(_h_s[0]),int(_h_s[1])),
                                                      datetime.datetime(int(_t_e[0]),int(_t_e[1]), int(_t_e[2]),int(_h_e[0]),int(_h_e[1])), 
                                                      worktiming = ["09:30", "12:00"])
                _hours_handle_2 = worktime.WorkHours( datetime.datetime(int(_t_s[0]),int(_t_s[1]), int(_t_s[2]),int(_h_s[0]),int(_h_s[1])),
                                                      datetime.datetime(int(_t_e[0]),int(_t_e[1]), int(_t_e[2]),int(_h_e[0]),int(_h_e[1])), 
                                                      worktiming=["13:30", "18:00"])
                _hours += float(_hours_handle_1.gethours()) 
                _hours += float(_hours_handle_2.gethours())
        _hours = "%.1f"%_hours
        self.global_dict[self._id]["WorkingTime"] = _hours
        return _hours
    
    def production_time(self):
        return self.global_dict[self._id].get("ProductionTime")

    def update_production_time(self, hours):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["ProductionTime"] == hours:
            return True
        self.global_dict[self._id]["ProductionTime"] = hours
        self._data["ProductionTime"] = hours
        v = self.put("task", self._data["Id"], self._data, "production_time")
        if v:
            return True
        else:
            return False

    def submit_task_time(self, date, hours, description = ""):
        _date = date
        _user_id = zfused_api.zFused.USER_ID
        _hours = hours

        _times = zfused_api.zFused.get( "task_time", filter = {"UserId":_user_id, "ProductionDate": _date, "TaskId": self._id} )
        if _times:
            # return 
            _data = _times[0]
            _data["ProductionTime"] = _hours
            _data["Description"] = description
            zfused_api.zFused.put("task_time", _data["Id"], _data)
        else:
            _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            # _task_handle = zfused_api.task.Task(_task_id)
            _value, _status = zfused_api.zFused.post("task_time", data = { "UserId": _user_id, 
                                                                            "ProductionDate": "{}T00:00:00+00:00".format(_date),
                                                                            "ProjectId": self.data().get("ProjectId"),
                                                                            "ProjectStepId": self.data().get("ProjectStepId"),
                                                                            "ProjectEntityType": self.data().get("ProjectEntityType"),
                                                                            "ProjectEntityId": self.data().get("ProjectEntityId"),
                                                                            "TaskId": self._id,
                                                                            "ProductionTime": _hours,
                                                                            "Description": description,
                                                                            "CreatedBy": _user_id,
                                                                            "CreatedTime": _current_time })

        _times = zfused_api.zFused.get( "task_time", filter = {"TaskId": self._id} )
        if _times:
            _hours_all = 0
            for _time in _times:
                _hours_all += _time.get("ProductionTime")
            self.update_production_time(_hours_all)

        # if self.is_sub_task():
        #     _parent_task = Task(self._data.get("ParentTaskId"))
        #     _parent_task.submit_task_time(date, hours, description)

    def prophet(self, proposed_entity_type, proposed_entity_id, proposed_description):
        _value = self._data.get("ProphetValue")
        if _value == -1:
            return False
        _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _user_id = zfused_api.zFused.USER_ID
        # new prophet
        _value, _status = zfused_api.zFused.post("prophet", data = { "EntityType": "task", 
                                                                     "EntityId": self._id,
                                                                     "Value": -1,
                                                                     "ProposedEntityType": proposed_entity_type,
                                                                     "ProposedEntityId": proposed_entity_id,
                                                                     "ProposerId": _user_id,
                                                                     "ProposedTime": _current_time,
                                                                     "ProposedDescription": proposed_description,
                                                                     "CreatedBy": _user_id,
                                                                     "CreatedTime": _current_time })
        if _status:
            _prophet_id = _value["Id"]
            self.global_dict[self._id]["ProphetId"] = _prophet_id
            self._data["ProphetId"] = _prophet_id
            self.global_dict[self._id]["ProphetValue"] = -1
            self._data["ProphetValue"] = -1
            v = self.put("task", self._data["Id"], self._data, "prophet_id")
            if v:
                return True
            else:
                return False
        return False

    def unprophet(self):
        _prophet_id = self._data.get("ProphetId")
        _value = self._data.get("ProphetValue")
        if _value != -1:
            return False
        _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _user_id = zfused_api.zFused.USER_ID
        # un prophet
        _prophet_handle = zfused_api.prophet.Prophet(_prophet_id)
        _prophet_handle.unprophet()
        _status = self.update_prophet_value(1)
        return _status

    def update_prophet_value(self, value):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["ProphetValue"] == value:
            return True
        self.global_dict[self._id]["ProphetValue"] = value
        self._data["ProphetValue"] = value
        v = self.put("task", self._data["Id"], self._data, "prophet_value")
        if v:
            return True
        else:
            return False

    def percent(self):
        _percent =  self.global_dict[self._id].get("Percent")
        return _percent if _percent else - 100

    def update_percent(self, value):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["Percent"] == value:
            return True
        self.global_dict[self._id]["Percent"] = value
        self._data["Percent"] = value
        v = self.put("task", self._data["Id"], self._data, "percent")
        if v:
            return True
        else:
            return False

    def update_last_version_id(self, version_id):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["LastVersionId"] == version_id:
            return True
        self.global_dict[self._id]["LastVersionId"] = version_id
        self._data["LastVersionId"] = version_id
        v = self.put("task", self._data["Id"], self._data, "", False)
        if v:
            return True
        else:
            return False

    def update_last_report_id(self, report_id):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["LastReportId"] == report_id:
            return True
        self.global_dict[self._id]["LastReportId"] = report_id
        self._data["LastReportId"] = report_id
        v = self.put("task", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False

    def is_locked(self):
        return self._data.get("IsLocked")
    
    def set_locked(self, is_locked):
        if self.global_dict[self._id]["IsLocked"] == is_locked:
            return True
        _created_by = zfused_api.zFused.USER_ID
        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        if is_locked:
            self.global_dict[self._id]["LockedTime"] = _created_time
            self._data["LockedTime"] = _created_time
        self.global_dict[self._id]["LockedBy"] = _created_by
        self._data["LockedBy"] = _created_by
        self.global_dict[self._id]["IsLocked"] = is_locked
        self._data["IsLocked"] = is_locked
        v = self.put("task", self._data["Id"], self._data, "is_locked")
        if v:
            return True
        else:
            return False



    def is_sub_task(self):
        return self._data.get("ParentTaskId")

    def has_sub_task(self):
        return self._data.get("HasSubTask")

    def set_has_sub_task(self, has_sub_task):
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["HasSubTask"] == has_sub_task:
            return True
        self.global_dict[self._id]["HasSubTask"] = has_sub_task
        self._data["HasSubTask"] = has_sub_task
        v = self.put("task", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False

    def parent_task_id(self):
        return self._data.get("ParentTaskId")

    def sub_task_name(self):
        return self._data.get("SubTaskName")

    def sub_task_code(self):
        return self._data.get("SubTaskCode")