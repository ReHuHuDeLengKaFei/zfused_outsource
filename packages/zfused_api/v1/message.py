# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from collections import defaultdict

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


def send_message(submitter_object, submitter_id, receiver_ids, data, msgtype = "", link_object = "", link_id = 0, group_type = "", group_id = 0, at_user_ids = []):
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")    
    _is_global = 1
    if receiver_ids:
        _is_global = 0
    
    # is global 为真的时候及是 广播式 的，全员隐藏式接受
    # is global 为假的时候及是 一对一或一堆N式

    # 发送消息 写入数据库
    _value, _status = zfused_api.zFused.post(key = "message", data = { "Data": str(data),
                                                     "SubmitterObject": submitter_object,
                                                     "SubmitterId": submitter_id,
                                                     "SubmitTime": _current_time,
                                                     "MsgType": msgtype,
                                                     "LinkObject": link_object,
                                                     "LinkId": link_id,
                                                     "IsGlobal": _is_global,
                                                     "GroupType": group_type,
                                                     "GroupId": group_id,
                                                     "CreatedBy": zfused_api.zFused.USER_ID,
                                                     "CreatedTime": _current_time  })

    if _status:
        _id = _value["Id"]
        if receiver_ids:
            for _receiver_id in receiver_ids:
                _is_read = "0"
                _is_at = 0
                if _receiver_id == zfused_api.zFused.USER_ID:
                    _is_read = "1"
                if _receiver_id in at_user_ids:
                    _is_at = 1
                zfused_api.zFused.post(key = "message_link", data = { "MessageId":_id, 
                                                                      "ReceiverObject": "user",
                                                                      "ReceiverId":_receiver_id,
                                                                      "ReceiveTime":None,
                                                                      "SubmitterObject": submitter_object,
                                                                      "SubmitterId": submitter_id,
                                                                      "IsRead":_is_read,
                                                                      "IsAt": _is_at,
                                                                      "GroupType": group_type,
                                                                      "GroupId": group_id,
                                                                      "CreatedBy": zfused_api.zFused.USER_ID,
                                                                      "CreatedTime": _current_time  } )
    return True, _id

def user_submit_message(submitter_id):
    """ get submitter message
    """
    _message_link = zfused_api.zFused.get("message", filter = {"SubmitterId":submitter_id})
    if not _message_link:
        return []
    return _message_link

def unread_message(receiver_id):
    _message_link = zfused_api.zFused.get("message_link", filter = {"ReceiverId":receiver_id,"IsRead":0})
    if not _message_link:
        return []
    _messgae_id = ["%s"%_handle["MessageId"] for _handle in _message_link]
    _message_data = zfused_api.zFused.get("message",filter = {"id.in":"|".join(_messgae_id)})
    return _message_data

def clear(lis):
    del lis[:]

def cache_from_ids(ids):
    _messages = []
    _message_links = []
    if ids:
        _in_list_str = "|".join([str(_id) for _id in ids])
        _messages = zfused_api.zFused.get("message", filter = {"Id__in": _in_list_str})
        _message_links = zfused_api.zFused.get("message_link", filter = {"MessageId__in": _in_list_str})
    else:
        _messages = zfused_api.zFused.get("message")
        _message_links = zfused_api.zFused.get("message_link")
    if _messages:
        if isinstance(_messages, list):
            list(map(lambda _message: Message.global_dict.setdefault(_message["Id"],_message), _messages))
            list(map(lambda _message: clear(Message.global_link[_message["Id"]]) if Message.global_link[_message["Id"]] else False, _messages))
    if _message_links:
        if isinstance(_message_links, list):
            list(map(lambda _message_link: Message.global_link[_message_link["MessageId"]].append(_message_link), _message_links))
            list(map(lambda _message_link: MessageLink.global_dict.setdefault(_message_link["Id"],_message_link), _message_links))

    return _messages


def cache(id_list = []):
    _messages = []
    if id_list:
        _in_list_str = "|".join([str(_id) for _id in id_list])
        _messages = zfused_api.zFused.get("message", filter = {"Id__in": _in_list_str})
        _message_links = zfused_api.zFused.get("message_link", filter = {"MessageId__in": _in_list_str})
    else:
        _messages = zfused_api.zFused.get("message")
        _message_links = zfused_api.zFused.get("message_link")
    if _messages:
        list(map(lambda _message: Message.global_dict.setdefault(_message["Id"],_message), _messages))
        list(map(lambda _message: clear(Message.global_link[_message["Id"]]) if Message.global_link[_message["Id"]] else False, _messages))
    if _message_links:
        list(map(lambda _message_link: Message.global_link[_message_link["MessageId"]].append(_message_link), _message_links))
        list(map(lambda _message_link: MessageLink.global_dict.setdefault(_message_link["Id"],_message_link), _message_links))
    return _messages


class Message(_Entity):
    global_dict = {}
    global_link = defaultdict(list)
    def __init__(self, entity_id, entity_data = None):
        super(Message, self).__init__("message", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("message", self._id)
                if not _data:
                    logger.error("message id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data

        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    @_Entity._recheck
    def submitter_id(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        return self._data.get("SubmitterId")
    
    def message_links(self):
        return self.global_link.get(self._id)



class MessageLink(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(MessageLink, self).__init__("message_link", entity_id, entity_data)
        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one( "message_link", self._id )
                if not _data:
                    logger.error("message link id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    @_Entity._recheck
    def is_read(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data
        return int(self._data.get("IsRead"))

    def update_is_read(self, is_read = 1):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data
        if self._data.get("IsRead") == str(is_read):
            return 

        self.global_dict[self._id]["IsRead"] = str(is_read)
        self._data["IsRead"] = str(is_read)
        v = self.put("message_link", self._data["Id"], self._data, "IsRead")
        if v:
            return True
        else:
            return False