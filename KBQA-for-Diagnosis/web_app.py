import os
import re
import json

from modules import gossip_robot, medical_robot, classifier
from utils.json_utils import dump_user_dialogue_context, load_user_dialogue_context

from flask import Flask, request
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

# 开启一个flask应用
app = Flask(__name__)


# 机器人
def text_replay(user, msg):
    user_intent = classifier(msg)
    if user_intent in ["greet", "goodbye", "deny", "isbot"]:
        reply = gossip_robot(user_intent)
    elif user_intent == "accept":
        reply = load_user_dialogue_context(user)
        reply = reply.get("choice_answer", "")
    else:
        reply = medical_robot(msg, user)
        if reply["slot_values"]:
            dump_user_dialogue_context(user, reply)
        reply = reply.get("replay_answer", "")

    if '\n' in reply:
        reply = reply.strip().replace('\\n', '<br>')
    return reply


# 定义路由和函数功能
@app.route('/msg')
def msg():
    # 接收连接用户socket
    user_socker = request.environ.get('wsgi.websocket')
    # 保持与客户端通信
    while 1:
        # 接收客户端发来的消息
        msg = user_socker.receive()
        if str(msg) == '':
            continue
        reply = text_replay('default_user', msg)
        # 将要返回给客户端的数据封装到一个字典
        res = {
            "id": 0,
            "user": 'https://pic.qqtn.com/up/2018-2/15175580434330335.gif',
            "msg": reply
        }
        # 编码为json格式并发送给客户端
        user_socker.send(json.dumps(res))


if __name__ == '__main__':
    # 创建一个服务器，IP地址为0.0.0.0，端口是9687，处理函数是app
    http_server = WSGIServer(('0.0.0.0', 9687), app, handler_class=WebSocketHandler)
    # 开始监听请求:
    http_server.serve_forever()
