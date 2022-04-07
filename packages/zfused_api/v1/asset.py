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


def delete(asset_id):
    """ delete asset

    """
    zfused_api.zFused.delete("asset", asset_id)

def new(project_id, name, code, type_id, status_id, active = "true", create_by = None, description = None):
    """ create new asset

    """
    # asset is exists
    _assets = zfused_api.zFused.get( "asset", 
                                     filter = {"ProjectId": project_id, "Code": code})
    if _assets:
        return "{} is exists".format(name), False

    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if create_by:
        _create_by_id = create_by
    else:
        _create_by_id = zfused_api.zFused.USER_ID
    _value, _status = zfused_api.zFused.post(key = "asset", data = { "Name": name,
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
        return Asset(_value["Id"], _value), True
    return "{} create error".format(name), False

def new_asset(project_id, name, code, type_id, status_id, active = "true", create_by = None, description = None):
    """ create new asset

    """
    # asset is exists
    _assets = zfused_api.zFused.get( "asset", 
                                     filter = {"ProjectId": project_id, "Code": code})
    if _assets:
        return "{} is exists".format(name), False

    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if create_by:
        _create_by_id = create_by
    else:
        _create_by_id = zfused_api.zFused.USER_ID
    _value, _status = zfused_api.zFused.post(key = "asset", data = { "Name": name,
                                                                     "Code": code,
                                                                     "ProjectId": project_id,
                                                                     "TypeId": type_id,
                                                                     "Description":description,
                                                                     "StatusId":status_id,
                                                                     # "CreateTime":_current_time, 
                                                                     "StartTime":"0001-01-01T00:00:00Z", 
                                                                     "EndTime":"0001-01-01T00:00:00Z",
                                                                     # "CreateBy":_create_by_id,
                                                                     "Active":active,
                                                                     "CreatedBy":_create_by_id,
                                                                     "CreatedTime":_current_time })
    if _status:
        return _value["Id"], True
    return "{} create error".format(name), False

def clear(lis):
    del lis[:]

def cache(project_id_list = [], extract_freeze = True):
    """ init project assets
    """

    _s_t = time.clock()
    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status", fields = ["Id"])
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0}, fields = ["Id"])
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])

    if not project_id_list:
        # _assets = zfused_api.zFused.get("asset", sortby = ["Code"], order = ["asc"])
        _assets = zfused_api.zFused.get("asset", filter = {"StatusId__in": _status_ids})
        # _asset_historys = zfused_api.zFused.get("asset_history")
        _asset_tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityType": "asset", "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])
    else:
        _project_ids = "|".join(map(str,project_id_list))
        # _assets = zfused_api.zFused.get("asset", filter = {"ProjectId__in": _project_ids}, sortby = ["Code"], order = ["asc"])
        _assets = zfused_api.zFused.get("asset", filter = {"ProjectId__in": _project_ids, "StatusId__in": _status_ids})
        # _asset_historys = zfused_api.zFused.get("asset_history", filter = {"ProjectId__in": _project_ids})
        _asset_tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityType": "asset", "ProjectId__in": _project_ids, "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])
    if _assets:
        list(map(lambda _asset: Asset.global_dict.setdefault(_asset["Id"],_asset), _assets))
        list(map(lambda _asset: clear(Asset.global_tasks[_asset["Id"]]) if Asset.global_tasks[_asset["Id"]] else False, _assets))
    # if _asset_historys:
    #     list(map(lambda _asset: Asset.global_historys[_asset["AssetId"]].append(_asset), _asset_historys))
    if _asset_tasks:
        from . import task
        list(map(lambda _task: Asset.global_tasks[_task["ProjectEntityId"]].append(_task), _asset_tasks))
        list(map(lambda _task: task.Task.global_dict.setdefault(_task["Id"],_task), _asset_tasks))
    # cache tags
    _str_asset_ids = [str(_asset_id) for _asset_id in Asset.global_dict]
    _tag_links = zfused_api.zFused.get("tag_link", filter = {"LinkObject": "asset", "LinkId__in": "|".join(_str_asset_ids)}, fields = ["LinkId", "TagId"] )
    if _tag_links:
        for _tag_link in  _tag_links:
            _asset_id = _tag_link["LinkId"]
            Asset.global_tags[_asset_id].append(_tag_link["TagId"])
    _e_t = time.clock()
    logger.info("asset cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _assets

def cache_from_ids(ids, extract_freeze = False):
    _s_t = time.clock()
    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status", fields = ["Id"])
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0}, fields = ["Id"])
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])

    ids = "|".join(map(str, ids))
    _assets = zfused_api.zFused.get("asset", filter = {"Id__in": ids, "StatusId__in": _status_ids})
    _asset_tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityType": "asset", "ProjectEntityId__in": ids, "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])

    if _assets:
        list(map(lambda _asset: Asset.global_dict.setdefault(_asset["Id"],_asset), _assets))
        list(map(lambda _asset: clear(Asset.global_tasks[_asset["Id"]]) if Asset.global_tasks[_asset["Id"]] else False, _assets))
    # if _asset_historys:
    #     list(map(lambda _asset: Asset.global_historys[_asset["AssetId"]].append(_asset), _asset_historys))
    if _asset_tasks:
        from . import task
        list(map(lambda _task: Asset.global_tasks[_task["ProjectEntityId"]].append(_task), _asset_tasks))
        list(map(lambda _task: task.Task.global_dict.setdefault(_task["Id"],_task), _asset_tasks))

    return _assets


class Asset(_Entity):
    global_dict = {}
    global_historys = defaultdict(list)
    global_tasks = defaultdict(list)
    global_tags = defaultdict(list)
    task_dict = defaultdict(list)
    def __init__(self, entity_id, entity_data = None):
        super(Asset, self).__init__("asset", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                # _data = self.get("asset", filter={"Id": self._id})
                _data = self.get_one("asset", self._id)
                if not isinstance(_data, dict):
                    logger.error("asset id {0} not exists".format(self._id))
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
        """
        get full path code

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
        """
        get full path name

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
        """
        get full path name and code

        rtype: str
        """
        return u"{}({})".format(self.full_name(), self.full_code())

    def type(self):
        """get type handle
        """
        _type_id = self._data.get("TypeId")
        if _type_id:
            return zfused_api.types.Types(_type_id)
        return None

    def type_id(self):
        return self._data.get("TypeId")

    def project(self):
        _project_id = self._data.get("ProjectId")
        if _project_id:
            return zfused_api.project.Project(_project_id)
        return None

    def project_id(self):
        """ get project id
        """
        return self._data["ProjectId"]

    def status_id(self):
        """ get status id 
        """
        return self.global_dict[self._id]["StatusId"]

    def status(self):
        return zfused_api.status.Status(self._data.get("StatusId"))

    def level(self):
        """ get asset level

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
        """ get asset production path

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
        """ get asset backup path

        rtype: str
        """
        _backup_project_path = self.project().backup_path()
        _path = "{}/{}".format(_backup_project_path, self.path())
        return _path

    def work_path(self, absolute = True):
        """ get asset work path
        rtype: str
        """
        if absolute:
            _work_project_path = self.project().work_path()
            _path = "{}/{}".format(_work_project_path, self.path())
        else:
            _path = self.path()
        return _path

    def temp_path(self):
        """ get asset publish path

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
        """ get asset review path

        rtype: str
        """
        _review_project_path = self.project().config["Review"]
        _path = "{}/asset/{}".format(_review_project_path, self.full_code())
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
        _historys = self.get("asset_history", filter = {"AssetId": self._id})
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

        # get asset task
        _tasks = self.get("task", filter = {"ProjectEntityType": "asset", "ProjectEntityId": self._id})
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
        """ get asset link tag ids
        """
        if self._id not in self.global_tags or self.RESET:
            # _historys = self.get("tag_link", filter = {"TaskId":self._id}, sortby = ["ChangeTime"], order = ["asc"])
            _tag_links = self.get("tag_link", filter = {"LinkObject": "asset", "LinkId": self._id})
            if _tag_links:
                self.global_tags[self._id] = [_tag_link["TagId"] for _tag_link in _tag_links]
        return self.global_tags[self._id]

    def versions(self):
        """ get task version
        
        :rtype: list
        """
        _versions = self.get("version", filter={"ProjectEntityId": self._id, "ProjectEntityType": "asset"},
                                        sortby = ["Index"], order = ["asc"])
        return _versions if _versions else []

    def project_step_versions(self, project_step_id):
        """
        """
        # get task
        _tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityId": self._id, "ProjectEntityType": "asset", "ProjectStepId": project_step_id})
        if not _tasks:
            return []
        _task = _tasks[0]
        _versions = self.get("version", filter={"ProjectEntityId": self._id, "ProjectEntityType": "asset", "TaskId": _task["Id"], "IsApproval": 1},
                                        sortby = ["Index"], order = ["asc"])
        if not _versions:
            return []
        return _versions

    def history(self):
        """ get history

        :rtype: list
        """
        _history = self.get("asset_history", filter = {"AssetId":self._id}, sortby = ["ChangeTime"], order = ["asc"])
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
            _tasks = self.get("task", filter = {"ProjectEntityType": "asset", "ProjectEntityId": self._id})
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
                                                 "ProjectEntityType": "asset"} )
        if not _tasks:
            return []
        return _tasks

    def source_relatives(self):
        """ 
        """
        _relatives = zfused_api.zFused.get("relative", filter = {"TargetObject": "asset", 
                                                                  "TargetId": self._id})
        return set([(_relative["SourceObject"], _relative["SourceId"]) for _relative in _relatives if _relative["SourceId"] != self._id] if _relatives else [])

    def target_relatives(self):
        """
        """
        _relatives = zfused_api.zFused.get("relative", filter = {"SourceObject": "asset", 
                                                                  "SourceId": self._id})
        return set([(_relative["TargetObject"], _relative["TargetId"]) for _relative in _relatives if _relative["TargetId"] != self._id] if _relatives else [])

    # @classmethod
    # def load_task(cls, asset_id, project_step_id, task):
    #     _key = "{}_{}".format(asset_id, project_step_id)    
    #     cls.task_dict[_key].append(task)

    def update_status(self, status_id):
        """ update project step check script
        
        :param status_id: 状态id
        :rtype: bool
        """
        self.global_dict[self._id]["StatusId"] = status_id
        self._data["StatusId"] = status_id
        v = self.put("asset", self._data["Id"], self._data, "status_id")
        if v:
            return True
        else:
            return False

    def update_thumbnail(self, _thumbnail):
        """
        """
        self.global_dict[self._id]["Thumbnail"] = _thumbnail
        self._data["Thumbnail"] = _thumbnail
        v = self.put("asset", self._data["Id"], self._data, "thumbnai", False)
        if v:
            return True
        else:
            return False

    def update_thumbnail_path(self, thumbnail_path):
        if self.global_dict[self._id]["ThumbnailPath"] == thumbnail_path:
            return True
        self.global_dict[self._id]["ThumbnailPath"] = thumbnail_path
        self._data["ThumbnailPath"] = thumbnail_path
        v = self.put("asset", self._data["Id"], self._data, "thumbnail_path", False)
        if v:
            return True
        else:
            return False

    def update_description(self, _description):
        self.global_dict[self._id]["Description"] = _description
        self._data["Description"] = _description
        v = self.put("asset", self._data["Id"], self._data, "description")
        if v:
            return True
        else:
            return False

    def create_project_step_task(self, project_step_id):
        """ create default task
        """
        _project_step_id = project_step_id
        _project_id = self.project_id()
        _waiting_ids = zfused_api.status.waiting_status_ids()
        if not _waiting_ids:
            return False, "has not set waiting status"
        _status_id = _waiting_ids[0]
        # get project step id
        _project_step = zfused_api.step.ProjectStep(_project_step_id)
        _step_id = _project_step.data()["StepId"]

        # fix file code
        _task_name = "{}_{}".format(self.file_code(), _project_step.code()).replace("/", "_") 
        
        _assigned_id = 0
        _object = self.object()
        _project_entity_id = self.id()
        _software_id = _project_step.data()["SoftwareId"]
        _create_id = zfused_api.zFused.USER_ID
        _current_time = "%s+00:00" % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        _task = self.get("task", filter = { "ProjectStepId": _project_step_id,
                                            "ProjectId":_project_id,
                                            "StepId":_step_id,
                                            "ProjectEntityType": _object,
                                            "ProjectEntityId": _project_entity_id,
                                            "SoftwareId":_software_id})
        if _task:
            return False, "%s is exists"%_task_name

        _task, _status = self.post(key = "task", data = { "SelfObject": "task", 
                                                          "Name": _task_name,
                                                          "ProjectStepId": _project_step_id, 
                                                          "ProjectId": _project_id,
                                                          "ProjectEntityType": _object,
                                                          "ProjectEntityId": _project_entity_id,
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
        v = self.put("asset", self._data["Id"], self._data, "percent")
        if v:
            return True
        else:
            return False