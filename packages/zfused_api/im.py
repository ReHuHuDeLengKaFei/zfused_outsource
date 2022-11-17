# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

"""
    rabbitmq message
        root bugeinishuo1
"""

import os
import pika
import time
import datetime
import shutil
import logging
import threading

import zfused_api
from .v1 import message

__all__ = ["submit_message"]

logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.WARNING)

def get_mq_server_addr():
    import zfused_api
    _ip, _port = zfused_api.zFused.MQ_SERVER_ADDR.split(":")
    return _ip, int(_port)


class Conn:
    _channel = None

    @classmethod
    def bind(cls):
        # bind host
        _credentials = pika.PlainCredentials('root', 'bugeinishuo1')
        _host, _port = get_mq_server_addr()
        _connection = pika.BlockingConnection(pika.ConnectionParameters(_host, _port,"/",_credentials))   
        Conn._channel = _connection.channel()
        Conn._channel.exchange_declare( exchange = 'direct_logs',
                                   exchange_type = 'topic')

def message_notification(message_id, submitter_object, submitter_id, receiver_ids = []):
    # if not Conn._channel:
    #     Conn.bind()
    # host = [zfused_api.zFused.SERVER_PATH.split("http://")[-1].split(":")[0], 5672]
    _credentials = pika.PlainCredentials('root', 'bugeinishuo1')
    _host, _port = get_mq_server_addr()
    _connection = pika.BlockingConnection(pika.ConnectionParameters(_host, _port,"/",_credentials))  
    _channel = _connection.channel()
    _channel.exchange_declare( exchange = 'direct_logs',
                               exchange_type = 'topic')
    # 发送消息
    _message_id = message_id
    _message = {
                  "message_id":_message_id,
                  "submitter_object":submitter_object,
                  "submitter_id":submitter_id
               }

    _submitter = "%s"%submitter_object

    if receiver_ids:
        if submitter_object == "system":
            severity = "message.system"
            _channel.basic_publish(exchange='direct_logs',
                                  routing_key = severity,
                                  body = str(_message),
                                  properties = pika.BasicProperties(  
                                             delivery_mode = 2, # make message persistent  
                                          ))
        else:

            for _receiver_id in receiver_ids:
                _submitter_id = "%s.%s"%(_submitter, _receiver_id)
                severity = "message.%s"%_submitter_id
                _channel.basic_publish( exchange='direct_logs',
                                        routing_key = severity,
                                        body = str(_message),
                                        properties = pika.BasicProperties(  
                                        delivery_mode = 2, # make message persistent  
                                         ))
        logger.info(" [x] Sent {}:{}".format(severity, _message))
    else:
        severity = "message.%s"%_submitter
        _channel.basic_publish(exchange='direct_logs',
                              routing_key = severity,
                              body = str(_message),
                              properties = pika.BasicProperties(  
                                         delivery_mode = 2, # make message persistent
                                      ))
        logger.info(" [x] Sent {}:{}".format(severity, _message))
    _connection.close()

def submit_message(submitter_object, submitter_id, receiver_ids, msg_data, msgtype, link_object = "", link_id = 0, group_type = "", group_id = 0, at_user_ids = []):
    """ submit message 
        0 代表全部
    """
    # 写入数据库
    _, _message_id = message.send_message( submitter_object, 
                                           submitter_id, 
                                           receiver_ids,
                                           msg_data,
                                           msgtype,
                                           link_object,
                                           link_id,
                                           group_type,
                                           group_id,
                                           at_user_ids )
    
    # _s_t = time.time()
    # 发送消息
    message_notification(_message_id, submitter_object, submitter_id, receiver_ids)
    # # 启用现成
    # _thread = threading.Thread(target = message_notification, args = (_message_id, submitter_object, submitter_id, receiver_ids))
    # _thread.start()
    # print("多线程发送消息: ", time.time() - _s_t)

    return _message_id