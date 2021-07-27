# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


def new_qc(code, link_object, link_id, approver_id, description, url = None, priority = 0):
    """ 新的反馈数据
    """
    _index = 1
    # 查看qc数据
    _qcs = zfused_api.zFused.get("qc", filter = {"LinkObject": link_object, "LinkId": link_id})
    if _qcs:
        _index += len(_qcs)

    _submit_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _submitter_id = zfused_api.zFused.USER_ID

    _qc, _status = zfused_api.zFused.post(key = "qc", data = { "Code": code,
                                                               "LinkObject": link_object,
                                                               "LinkId": link_id,
                                                               "Index": _index,
                                                               "ApproverId": approver_id,
                                                               "SubmitterId": _submitter_id,
                                                               "SubmitTime": _submit_time,
                                                               "Description":description,
                                                               "Url": url,
                                                               "Priority": priority,
                                                               "Status": "0",
                                                               "CreatedBy": _submitter_id,
                                                               "CreatedTime": _submit_time } )

    # _qcs = zfused_api.zFused.get("qc", filter = {"LinkObject": link_object, "LinkId": link_id})
    if _status:
        return _qc["Id"], True
    return "{} create error".format(code), False


class QC(_Entity):
    global_dict = {}

    def __init__(self, id, data=None):
        self._id = id
        self._data = data

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get("qc", filter={"Id": self._id})
                if not _data:
                    logger.error("qc id {0} not exists".format(self._id))
                    return
                self._data = _data[0]
                self.global_dict[self._id] = _data[0]

        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def object(self):
        return "qc"

    def id(self):
        return self._id

    def data(self):
        return self._data

    def url(self):
        return self._data["Url"]

    def submit_time(self):
        _time_text = self._data["SubmitTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")