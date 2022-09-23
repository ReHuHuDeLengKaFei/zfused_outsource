# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import shutil
import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


def cache( project_id ):
    """ init project versions
    """
    Review.global_dict = {}
    if not project_id:
        _reviews = zfused_api.zFused.get("review", sortby = ["Id"], order = ["desc"])
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_id])
        _reviews = zfused_api.zFused.get("review", filter = {"ProjectId__in": _project_ids}, sortby = ["Id"], order = ["desc"])
    if _reviews:
        for _review in _reviews:
            Review.global_dict[_review["Id"]] = _review
    return _reviews

def cache_from_ids(ids):
    ids = "|".join(map(str, ids))
    _reviews = zfused_api.zFused.get("review", filter = {"Id__in": ids})
    if _reviews:
        list(map(lambda _review: Review.global_dict.setdefault(_review["Id"],_review), _reviews))
    return _reviews


class Review(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Review, self).__init__("review", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("review", self._id)
                if not _data:
                    logger.error("review id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data

    def entity(self):
        return zfused_api.objects.Objects(self._data.get("EntityType"),self._data.get("EntityId"))

    def code(self):
        return self.entity().code()

    def description(self):
        return self._data["Description"]

    def project(self):
        _entity = self.entity()
        return _entity.project()

    def project_id(self):
        _entity = self.entity()
        return _entity.project_id()

    def project_entity(self):
        _entity = self.entity()
        return _entity.project_entity()

    def project_step(self):
        _entity = self.entity()
        return _entity.project_step()

    def project_step_id(self):
        _entity = self.entity()
        return _entity.project_step_id()

    def full_name_code(self):
        return zfused_api.objects.Objects(self._data["EntityType"], self._data["EntityId"]).full_name_code()

    def file_code(self):
        """ project step file code

        :rtype: str
        """
        return self.code().replace("/", "_")

    def file_path(self):
        return self.code()

    def production_path(self):
        """ get version task production path
        rtype: str
        """
        return self.task().production_path()

    def color(self):
        """ return review color
        """
        return self._data["Coloe"]

    def sort(self):
        """ 返回排序序号
        """
        return self._data["Sort"]

    def status(self):
        return self._data["Status"]

    def task(self):
        return zfused_api.task.Task(self._data.get("TaskId"))

    def task_id(self):
        return self._data.get("TaskId")

    def submit_reply(self, name,
                           reviewer_ids = [], 
                           ccer_ids = [], 
                           thumbnail = None, 
                           description = None ):
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
        _all_review = self.get("report", filter = { "EntityType": "task","EntityId": _task_id })
        _index = 0
        if _all_review:
            _last_review = _all_review[-1]
            _index = len(_all_review) + 1
        else:
            _index = 1
        if _index:
            _name = "{}.{}".format(name, str(_index).zfill(4))
            _report, _status = self.post(key = "report", data = { "Name": _name,
                                                                  "ProjectId": _project_id,
                                                                  "EntityType": "task",
                                                                  "EntityId": _task_id,
                                                                  "Index": _index,
                                                                  "ThumbnailPath": thumbnail,
                                                                  "Description": description,
                                                                  "CreatedTime": _create_time,
                                                                  "CreatedBy": _user_id })
            # _last_report = self.get("report", filter = { "Name": _name,
            #                                               "ProjectId":_project_id,
            #                                               "EntityType": "task",
            #                                               "EntityId": _task_id,
            #                                               "Index":_index,
            #                                               "CreatedBy": _user_id
            #                                                } )
            if not _status:
                return False, "{} submit error".format(name)
            # _last_report = _last_report[0]
        _report_id = _report["Id"]
        # 提交审查人员
        _review, _status = self.post(key = "review", data = { "EntityType": "report", 
                                                               "EntityId": _report_id, 
                                                               "ReviewerId": _reviewer_id,
                                                               "Status":"0",
                                                               "SubmitterId": _user_id,
                                                               "SubmitTime": _create_time,
                                                               "ThumbnailPath": thumbnail,
                                                               "CreatedBy": _user_id,
                                                               "CreatedTime": _create_time })
        # _review_data = self.get("review", filter = { "EntityType": "report", 
        #                                              "EntityId": _report_id, 
        #                                              "ReviewerId": _reviewer_id,
        #                                              "Status":"0",
        #                                              "SubmitterId":_user_id})
        if not _status:
            return False,"%s review create error"%name
        _review_id = _review["Id"]
        #  抄送人员
        if ccer_ids:
            for _ccer_id in ccer_ids:
                self.post(key = "cc", data = { "Object": "report",
                                               "ObjectId": _report_id, 
                                               "UserId": _ccer_id,
                                               "CreatedBy": _user_id,
                                               "CreatedTime": _create_time })
        #  发送通知信息
        #  组成员 新添加组成员
        _user_ids = reviewer_ids + ccer_ids
        _group_users = zfused_api.zFused.get("group_user", filter = {"EntityType":"task", "EntityId":self._id})
        if _group_users:
            for _group_user in _group_users:
                _user_id = _group_user["UserId"]
                _user_ids.remove(_user_id)
        if _user_ids:
            for _user_id in _user_ids:
                zfused_api.zFused.post("group_user", { "EntityType":"task", 
                                                       "EntityId":_link_id, 
                                                       "UserId":_user_id,
                                                       "CreatedBy": _user_id,
                                                       "CreatedTime": _create_time })
        _user_id = zfused_api.zFused.USER_ID
        zfused_api.im.submit_message( "user",
                                      _user_id,
                                      reviewer_ids + ccer_ids,
                                      {"entity_type": "report",
                                       "entity_id": _report_id},
                                      "review", 
                                      "review",
                                      _review_id)
        zfused_api.im.submit_message( "user",
                                      _user_id,
                                      reviewer_ids + ccer_ids,
                                      {"entity_type": "report",
                                       "entity_id": _report_id},
                                      "review", 
                                      "review",
                                      _review_id,
                                      "task",
                                      self._id )
        #发送系统通知
        #im.submit_message(['192.168.103.19',5672],{"msgtype":"review","review":{"review_id":id,"title":"Title"}},"user",34,[111,34])
        return _report_id, "%s submit review success"%name

    def update_color(self, color):
        self.global_dict[self._id]["Color"] = color
        self._data["Color"] = color
        v = self.put("project_step", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False

    def get_thumbnail(self, is_review = True):
        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None

    def thumbnail(self):
        """ get thumbnail
        """
        return self._data["ThumbnailPath"]

    def submit(self, _s, _des = None):
        currentTime = "%s+00:00" % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _next_review_process_id = 0
        # get current 
        _review_process_id = self._data.get("ReviewProcessId")
        if _review_process_id:
            _review_record = zfused_api.zFused.get("review_record", filter = {"ReviewId":self._id, "ReviewProcessId":_review_process_id})
            if _review_record:
                _review_record = _review_record[0]
                _review_record["Value"] = int(_s)
                _review_record["SubmitterId"] = zfused_api.zFused.USER_ID
                _review_record["SubmitTime"] = currentTime
                self.put("review_record", _review_record["Id"], _review_record)
            if _s == "1":
                _review_process_handle = zfused_api.review.ReviewProcess(_review_process_id)
                _review_process_list = zfused_api.zFused.get("review_process", filter = { "EntityType":_review_process_handle.data().get("EntityType"), 
                                                                                          "EntityId":_review_process_handle.data().get("EntityId") },
                                                                               sortby = ["Sort"], order = ["asc"] )
                for _index, _review_process in enumerate(_review_process_list):
                    if _review_process.get("Id") == _review_process_id:
                        if _index < len(_review_process_list) - 1:
                            _next_review_process_id = _review_process_list[_index + 1].get("Id")
                            # 提交新的记录
                            self.post(key = "review_record", data = { "ReviewId": self._id,
                                                                      "ReviewProcessId": _next_review_process_id,
                                                                      "CreatedBy": zfused_api.zFused.USER_ID,
                                                                      "CreatedTime": currentTime } )
                            break
            # _review_process_ids = [str(_review_process["Id"]) for _review_process in _review_process_list]
            # _review_records = zfused_api.zFused.get("review_record", filter = {"ReviewId":self._id, "ReviewProcessId__in":"|".join(_review_process_ids)})
            # if _review_records:
        if _next_review_process_id:
            self.global_dict[self._id]["ReviewProcessId"] = _next_review_process_id
            self._data["ReviewProcessId"] = _next_review_process_id
            self.global_dict[self._id]["ReviewProcessValue"] = 0
            self._data["ReviewProcessValue"] = 0
            self.global_dict[self._id]["Status"] = "0"
            self._data["Status"] = "0"
        else:
            self.global_dict[self._id]["Status"] = _s
            self._data["Status"] = _s
            self.global_dict[self._id]["ReviewProcessValue"] = int(_s)
            self._data["ReviewProcessValue"] = int(_s)
        currentTime = "%s+00:00" % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.global_dict[self._id]["ReviewerId"] = self.USER_ID
        self.global_dict[self._id]["ReviewTime"] = currentTime
        self._data["ReviewerId"] = self.USER_ID
        self._data["ReviewTime"] = currentTime
        v = self.put("review", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False



class ReviewProcess(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(ReviewProcess, self).__init__("review_process", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("review_process", self._id)
                if not _data:
                    logger.error("review process id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]


class Review_(_Entity):
    global_dict = {}
    task_dict = {}
    global_approval = {}
    def __init__(self, id, data = None):
        self._id = id
        self._data = data

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get("review", filter = {"Id":self._id})
                if not _data:
                    logger.error("review id {0} not exists".format(self._id))
                    return
                self._data = _data[0]
                self.global_dict[self._id] = _data[0]
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def object(self):
        return "review"

    def id(self):
        return self._id

    def data(self):
        return self._data

    def name(self):
        return self._data["Name"]

    def approvals(self):
        if self._id not in self.global_approval.keys():
            _app = self.get("approval", filter = {"Object":"review", "ObjectId":self._id})
            if _app:
                self.global_approval[self._id] = _app[0]
            #return _app[0]
        return self.global_approval[self._id]

    def get_thumbnail(self):
        """ get thumbnail
        """
        taskHandle = zfused_api.task.Task(self._data["TaskId"])
        return taskHandle.get_thumbnail()
        
        path = taskHandle.backup_path()        
        local_path = taskHandle.work_path()
        thumbnail = "%s%s"%(path, self._data["Thumbnail"])
        if not thumbnail or not os.path.isfile(thumbnail):
            return None
        thumbnail_local = thumbnail.replace(path,local_path)
        if not os.path.isfile(thumbnail_local):
            if not os.path.isdir(os.path.dirname(thumbnail_local)):
                os.makedirs(os.path.dirname(thumbnail_local))
            shutil.copy(thumbnail, thumbnail_local)
        thumbnail = thumbnail_local
        return thumbnail
