# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import os
import time
import datetime
import shutil
import logging
import re

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


def delete(assembly_id):
    """ delete assembly

    """
    zfused_api.zFused.delete("assembly", assembly_id)

def new(project_id, name, code, status_id, active = "true", create_by = None, description = None):
    """ create new assembly

    """
    # assembly is exists
    _assemblys = zfused_api.zFused.get( "assembly", 
                                     filter = {"ProjectId": project_id, "Code": code})
    if _assemblys:
        return "{} is exists".format(name), False

    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if create_by:
        _create_by_id = create_by
    else:
        _create_by_id = zfused_api.zFused.USER_ID
    _value, _status = zfused_api.zFused.post(key = "assembly", data = { "Name": name,
                                                                        "Code": code,
                                                                        "ProjectId": project_id,
                                                                        "Description":description,
                                                                        "StatusId":status_id,
                                                                        "StartTime":"0001-01-01T00:00:00Z", 
                                                                        "EndTime":"0001-01-01T00:00:00Z",
                                                                        "Active":active,
                                                                        "CreatedBy":_create_by_id,
                                                                        "CreatedTime":_current_time })
    if _status:
        return Assembly(_value["Id"], _value), True
    return "{} create error".format(name), False

def new_assembly(project_id, name, code, status_id, type_id = 0, active = "true", create_by = None, description = None):
    """ create new assembly

    """
    # assembly is exists
    _assemblys = zfused_api.zFused.get( "assembly", 
                                        filter = {"ProjectId": project_id, "Code": code})
    if _assemblys:
        return "{} is exists".format(name), False

    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if create_by:
        _create_by_id = create_by
    else:
        _create_by_id = zfused_api.zFused.USER_ID
    _value, _status = zfused_api.zFused.post(key = "assembly", data = { "Name": name,
                                                                        "Code": code,
                                                                        "ProjectId": project_id,
                                                                        "TypeId": type_id,
                                                                        "Description":description,
                                                                        "StatusId":status_id,
                                                                        "StartTime":"0001-01-01T00:00:00Z", 
                                                                        "EndTime":"0001-01-01T00:00:00Z",
                                                                        "Active":active,
                                                                        "CreatedBy":_create_by_id,
                                                                        "CreatedTime":_current_time })
    if _status:
        return _value["Id"], True
    return "{} create error".format(name), False

def clear(lis):
    del lis[:]

def cache(project_id_list = [], extract_freeze = True):
    """ init project assemblys
    """

    _s_t = time.clock()
    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status", fields = ["Id"])
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0}, fields = ["Id"])
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])

    if not project_id_list:
        _assemblys = zfused_api.zFused.get("assembly", filter = {"StatusId__in": _status_ids})
        _assembly_tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityType": "assembly", "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])
    else:
        _project_ids = "|".join(map(str,project_id_list))
        _assemblys = zfused_api.zFused.get("assembly", filter = {"ProjectId__in": _project_ids, "StatusId__in": _status_ids})
        _assembly_tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityType": "assembly", "ProjectId__in": _project_ids, "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])
    if _assemblys:
        list(map(lambda _assembly: Assembly.global_dict.setdefault(_assembly["Id"],_assembly), _assemblys))
        list(map(lambda _assembly: clear(Assembly.global_tasks[_assembly["Id"]]) if Assembly.global_tasks[_assembly["Id"]] else False, _assemblys))
    if _assembly_tasks:
        from . import task
        list(map(lambda _task: Assembly.global_tasks[_task["ProjectEntityId"]].append(_task), _assembly_tasks))
        list(map(lambda _task: task.Task.global_dict.setdefault(_task["Id"],_task), _assembly_tasks))
    # cache tags
    _str_assembly_ids = [str(_assembly_id) for _assembly_id in Assembly.global_dict]
    _tag_links = zfused_api.zFused.get("tag_link", filter = {"LinkObject": "assembly", "LinkId__in": "|".join(_str_assembly_ids)}, fields = ["LinkId", "TagId"] )
    if _tag_links:
        for _tag_link in  _tag_links:
            _assembly_id = _tag_link["LinkId"]
            Assembly.global_tags[_assembly_id].append(_tag_link["TagId"])
    _e_t = time.clock()
    logger.info("assembly cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _assemblys

def cache_from_ids(ids, extract_freeze = False):
    _s_t = time.clock()
    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status", fields = ["Id"])
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0}, fields = ["Id"])
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])

    ids = "|".join(map(str, ids))
    _assemblys = zfused_api.zFused.get("assembly", filter = {"Id__in": ids, "StatusId__in": _status_ids})
    _assembly_tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityType": "assembly", "ProjectEntityId__in": ids, "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])

    if _assemblys:
        list(map(lambda _assembly: Assembly.global_dict.setdefault(_assembly["Id"],_assembly), _assemblys))
        list(map(lambda _assembly: clear(Assembly.global_tasks[_assembly["Id"]]) if Assembly.global_tasks[_assembly["Id"]] else False, _assemblys))
    if _assembly_tasks:
        from . import task
        list(map(lambda _task: Assembly.global_tasks[_task["ProjectEntityId"]].append(_task), _assembly_tasks))
        list(map(lambda _task: task.Task.global_dict.setdefault(_task["Id"],_task), _assembly_tasks))
    return _assemblys



class Assembly(_Entity):
    global_dict = {}
    global_historys = defaultdict(list)
    global_tasks = defaultdict(list)
    global_tags = defaultdict(list)
    task_dict = defaultdict(list)
    def __init__(self, entity_id, entity_data = None):
        super(Assembly, self).__init__("assembly", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("assembly", self._id)
                if not isinstance(_data, dict):
                    logger.error("assembly id {0} not exists".format(self._id))
                    self._data = {}
                    return None
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]
                
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data

    def description(self):
        return self._data["Description"]

    def file_code(self):
        """ task version file name
        :rtype: str
        """
        return self.code().replace("/", "_")

    def full_code(self):
        """get full path code
        rtype: str
        """
        _code = self._data["Code"]
        if self._data["TypeId"]:
            _step_code = zfused_api.types.Types(
                self._data["TypeId"]).data()["Code"]
            return u"{}/{}".format(_step_code, _code)
        else:
            return _code

    def full_name(self):
        """get full path name
        rtype: str
        """
        _name = self._data["Name"]
        if self._data["TypeId"]:
            _step_name = zfused_api.types.Types(
                self._data["TypeId"]).data()["Name"]
            return u"{}/{}".format(_step_name, _name)
        else:
            return _name

    def full_name_code(self):
        """get full path name and code
        rtype: str
        """
        return u"{}({})".format(self.full_name(), self.full_code())

    def type(self):
        """get type handle
        rtype: str
        """
        _type_id = self._data.get("TypeId")
        if _type_id:
            return zfused_api.types.Types(_type_id)
        return None

    def project(self):
        _project_id = self._data.get("ProjectId")
        if _project_id:
            return zfused_api.project.Project(_project_id)
        return None

    def project_id(self):
        """ get project id
        rtype: str
        """
        return self._data["ProjectId"]

    def status_id(self):
        """ get status id 
        rtype: int
        """
        return self.global_dict[self._id]["StatusId"]

    def status(self):
        return zfused_api.status.Status(self._data.get("StatusId"))

    def level(self):
        """ get assembly level
        rtype: str
        """
        return self.global_dict[self._id]["Level"]

    def start_time(self):
        """ get start time
        rtype: datetime.datetime
        """
        _time_text = self._data["StartTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def end_time(self):
        """ get end time
        rtype: datetime.datetime
        """
        _time_text = self._data["EndTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def create_time(self):
        """ get create time
        rtype: datetime.datetime
        """
        _time_text = self._data["CreateTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def default_path(self):
        return r"{}/{}".format(self.object(), self.full_code())

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
        """ get assembly production path

        rtype: str
        """
        _project_production_path = self.project().production_path()
        _path = "{}/{}".format(_project_production_path, self.path())
        return _path

    def transfer_path(self):
        _project_transfer_path = self.project().transfer_path()
        _path = "{}/{}".format(_project_transfer_path, self.path())
        return _path

    def backup_path(self):
        """ get assembly backup path

        rtype: str
        """
        _backup_project_path = self.project().backup_path()
        _path = "{}/{}".format(_backup_project_path, self.path())
        return _path

    def work_path(self, absolute = True):
        """ get assembly work path
        rtype: str
        """
        if absolute:
            _work_project_path = self.project().work_path()
            _path = "{}/{}".format(_work_project_path, self.path())
        else:
            _path = self.path()
        return _path

    def temp_path(self):
        """ get assembly publish path

        rtype: str
        """
        _publish_project_path = self.project().temp_path()
        _path = "{}/{}".format(_publish_project_path, self.path())
        return _path

    def image_path(self):
        _image_path = self.project().image_path()
        _path = "{}/{}".format(_image_path, self.path())
        return _path

    def cache_path(self):
        _cache_path = self.project().cache_path()
        _path = "{}/{}".format(_cache_path, self.path())
        return _path

    def review_path(self):
        """ get assembly review path

        rtype: str
        """
        _review_project_path = self.project().config["Review"]
        _path = "{}/assembly/{}".format(_review_project_path, self.full_code())
        return _path

    def thumbnail(self):
        """ get thumbnai name
        """
        return self.global_dict[self._id]["Thumbnail"]

    def get_thumbnail(self, is_version = False):
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
        # get task history
        _historys = self.get("assembly_history", filter = {"AssemblyId": self._id})
        if _historys:
            _data = _historys[0]
            _note = {"user_id": _data["CreatedBy"],
                     "notes": _data,
                     "type": "create",
                     "time": _data["CreatedTime"]}
            _notes.append(_note)
            if len(_historys) > 1:
                for _history in _historys:
                    _his_notes = []
                    for _key, _value in _history.items():
                        if _key in ["CreatedTime", "Id", "ChangeTime", "ChangeBy"]:
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

        # get assembly task
        _tasks = self.get("task", filter = {"ProjectEntityType": "assembly", "ProjectEntityId": self._id})
        if _tasks:
            for _task in _tasks:
                _note = {"user_id": _task["CreatedBy"],
                         "time": _task["CreatedTime"],
                         "notes":_task,
                         "type": "task"}
                _notes.append(_note)

        def get_sort(elem):
            return elem["time"]
        _notes.sort(key = get_sort)

        return _notes

    def tag_ids(self):
        """ get assembly link tag ids
        """
        if self._id not in self.global_tags or self.RESET:
            # _historys = self.get("tag_link", filter = {"TaskId":self._id}, sortby = ["ChangeTime"], order = ["asc"])
            _tag_links = self.get("tag_link", filter = {"LinkObject": "assembly", "LinkId": self._id})
            if _tag_links:
                self.global_tags[self._id] = [_tag_link["TagId"] for _tag_link in _tag_links]
        return self.global_tags[self._id]

    def versions(self):
        """ get task version
        
        :rtype: list
        """
        _versions = self.get("version", filter={"ProjectEntityId": self._id, "ProjectEntityType": "assembly"},
                                        sortby = ["Index"], order = ["asc"])
        return _versions if _versions else []

    def project_step_versions(self, project_step_id):
        """
        """
        # get task
        _tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityId": self._id, "ProjectEntityType": "assembly", "ProjectStepId": project_step_id})
        if not _tasks:
            return []
        _task = _tasks[0]
        _versions = self.get("version", filter={"ProjectEntityId": self._id, "ProjectEntityType": "assembly", "TaskId": _task["Id"], "IsApproval": 1},
                                        sortby = ["Index"], order = ["asc"])
        if not _versions:
            return []
        return _versions

    def history(self):
        """ get history

        :rtype: list
        """
        _history = self.get("assembly_history", filter = {"AssemblyId":self._id}, sortby = ["ChangeTime"], order = ["asc"])
        if _history:
            return _history
        else:
            return []

    def new_task(self, project_step_id, assigned_to):
        """ create new task
        """
        return

    def tasks(self, project_step_id_list = []):
        if self._id not in self.global_tasks or zfused_api.zFused.RESET:
            _tasks = self.get("task", filter = {"ProjectEntityType": "assembly", "ProjectEntityId": self._id})
            self.global_tasks[self._id] = _tasks
        _tasks = self.global_tasks[self._id]
        if not _tasks:
            return []
        if project_step_id_list:
            __tasks = []
            for _task in _tasks:
                if _task["ProjectStepId"] in project_step_id_list:
                    __tasks.append(_task)
            return __tasks
        else:
            return _tasks

    def user_ids(self):
        _user_ids = [zfused_api.zFused.USER_ID]

        _project_step_ids = self.project().task_step_ids()
        if _project_step_ids:
            for _project_step_id in _project_step_ids:
                _project_step = zfused_api.step.ProjectStep(_project_step_id)
                _user_ids += _project_step.review_user_ids() + _project_step.cc_user_ids() + _project_step.approvalto_user_ids()

        _tasks = self.tasks()
        if _tasks:
            for _task in _tasks:
                _task = zfused_api.task.Task(_task.get("Id"))
                _project_step = _task.project_step()
                _user_ids += [_task.assigned_to()]

        _group_user_ids = list(set(_user_ids))
        # insert 
        _user_id = zfused_api.zFused.USER_ID
        _create_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _group_users = self.get("group_user", filter = {"EntityType":self._type, "EntityId":self._id})
        if _group_users:
            for _group_user in _group_users:
                _user_id_un = int(_group_user["UserId"])
                if _user_id_un in _group_user_ids:
                    _group_user_ids.remove(_user_id_un)
        if _group_user_ids:
            for _user_id_un in _group_user_ids:
                self.post( "group_user", { "EntityType":self._type, 
                                           "EntityId":self._id, 
                                           "UserId":_user_id_un,
                                           "CreatedBy": _user_id,
                                           "CreatedTime": _create_time })

        return list(set(_user_ids))

    def _tasks(self, project_step_id_list = []):
        """ get task 
        """
        if project_step_id_list:
            _ids = "|".join([str(_step_id) for _step_id in project_step_id_list])
            _key = "{}_{}".format(self._id, _ids)
            _tasks = self.task_dict[_key]
        else:
            _tasks = self.get("task", filter = { "ProjectEntityId": self._id, 
                                                 "ProjectEntityType": "assembly"} )
        if not _tasks:
            return []
        return _tasks

    def source_relatives(self):
        """ 
        """
        _relatives = zfused_api.zFused.get("relative", filter = {"TargetObject": "assembly", 
                                                                  "TargetId": self._id})
        return set([(_relative["SourceObject"], _relative["SourceId"]) for _relative in _relatives if _relative["SourceId"] != self._id] if _relatives else [])

    def target_relatives(self):
        """
        """
        _relatives = zfused_api.zFused.get("relative", filter = {"SourceObject": "assembly", 
                                                                  "SourceId": self._id})
        return set([(_relative["TargetObject"], _relative["TargetId"]) for _relative in _relatives if _relative["TargetId"] != self._id] if _relatives else [])

    # @classmethod
    # def load_task(cls, assembly_id, project_step_id, task):
    #     _key = "{}_{}".format(assembly_id, project_step_id)    
    #     cls.task_dict[_key].append(task)

    def update_status(self, status_id):
        """ update project step check script
        
        :param status_id: 状态id
        :rtype: bool
        """
        self.global_dict[self._id]["StatusId"] = status_id
        self._data["StatusId"] = status_id
        v = self.put("assembly", self._data["Id"], self._data, "status_id")
        if v:
            return True
        else:
            return False

    def update_thumbnail(self, _thumbnail):
        """
        """
        self.global_dict[self._id]["Thumbnail"] = _thumbnail
        self._data["Thumbnail"] = _thumbnail
        v = self.put("assembly", self._data["Id"], self._data, "thumbnai", False)
        if v:
            return True
        else:
            return False

    def update_thumbnail_path(self, thumbnail_path):
        if self.global_dict[self._id]["ThumbnailPath"] == thumbnail_path:
            return True
        self.global_dict[self._id]["ThumbnailPath"] = thumbnail_path
        self._data["ThumbnailPath"] = thumbnail_path
        v = self.put("assembly", self._data["Id"], self._data, "thumbnail_path", False)
        if v:
            return True
        else:
            return False

    def update_description(self, _description):
        self.global_dict[self._id]["Description"] = _description
        self._data["Description"] = _description
        v = self.put("assembly", self._data["Id"], self._data, "description")
        if v:
            return True
        else:
            return False

    def create_project_step_task(self, project_step_id):
        """ create default task

        """
        _project_step_id = project_step_id
        # project id
        _project_id = self._data["ProjectId"]
        # get default status id
        _waiting_ids = zfused_api.status.waiting_status_ids()
        if not _waiting_ids:
            return
        _status_id = _waiting_ids[0]
        # get project step id
        _project_step_handle = zfused_api.step.ProjectStep(_project_step_id)
        _step_id = _project_step_handle.data()["StepId"]

        #
        # fix file code
        _task_name = "{}_{}".format(self.file_code(), _project_step_handle.code()).replace("/", "_") 
        
        _create_id = zfused_api.zFused.USER_ID
        _assigned_id = 0
        _object = "assembly"
        _link_id = self._id
        _software_id = _project_step_handle.data()["SoftwareId"]
        _current_time = "%s+00:00" % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


        _task = self.get("task", filter = { "ProjectStepId": _project_step_id,
                                            "ProjectId": _project_id,
                                            "StepId": _step_id,
                                            "ProjectEntityType": _object,
                                            "ProjectEntityId": _link_id,
                                            "SoftwareId": _software_id})
        if _task:
            return False, "%s is exists"%_task_name

        _task, _status = self.post(key = "task", data = { "SelfObject": "task", 
                                                           "Name": _task_name,
                                                           "ProjectStepId": _project_step_id, 
                                                           "ProjectId": _project_id,
                                                           "ProjectEntityType": _object,
                                                           "ProjectEntityId": _link_id,
                                                           "StepId": _step_id,
                                                           "StatusId": _status_id,
                                                           "AssignedTo": _assigned_id,
                                                           "SoftwareId": _software_id,
                                                           "Description": "",
                                                           "EstimatedTime": 0,
                                                           "StartTime": None,
                                                           "DueTime": None,
                                                           "IsOutsource": 0,
                                                           "Active": "true",
                                                           "CreatedBy": _create_id,
                                                           "CreatedTime": _current_time })
        if _status:
            if not self.global_tasks[self._id]:
                self.global_tasks[self._id] = []
            self.global_tasks[self._id].append(_task)

            _task = zfused_api.task.Task(_task["Id"])
            zfused_api.im.submit_message( "user",
                                        zfused_api.zFused.USER_ID,
                                        self.user_ids(),
                                        { "msgtype": "new", 
                                        "new": {"object": "task", "object_id": _task.id()} }, 
                                        "new",
                                        self.object(),
                                        self.id(),
                                        self.object(),
                                        self.id() )

            return _task.id(), "%s create success"%_task_name
        return False,"%s create error"%_task_name

    def derivatives(self):
        """ get all derivatives
        """
        all_objects = []
        _object = self.object()
        sub_objects = self.get("derivative", filter = {"Object": _object, "MainObjectId":self._id})
        if sub_objects:
            for obj in sub_objects:
                object_dict = {"object":_object, "id":obj["SubObjectId"]}
                all_objects.append(object_dict)
        main_objects = self.get("derivative", filter = {"Object": _object,"SubObjectId":self._id})
        if main_objects:
            for main_object in main_objects:
                object_dict = {"object":_object,"id":main_object["MainObjectId"]}
                if object_dict not in all_objects:
                    all_objects.append(object_dict)
                sub_objects = self.get("derivative", filter = {"Object": _object,"MainObjectId":main_object["MainObjectId"]})
                if sub_objects:
                    for obj in sub_objects:
                        object_dict = {"object":_object,"id":obj["SubObjectId"]}
                        if object_dict not in all_objects and obj["SubObjectId"] != self._id:
                            all_objects.append(object_dict)
        return all_objects

    def percent(self):
        _percent =  self.global_dict[self._id].get("Percent")
        return _percent if _percent else - 100

    def update_percent(self, value):
        if self.global_dict[self._id]["Percent"] == value:
            return True
        self.global_dict[self._id]["Percent"] = value
        self._data["Percent"] = value
        v = self.put("assembly", self._data["Id"], self._data, "percent")
        if v:
            return True
        else:
            return False