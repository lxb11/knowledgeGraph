# -*- coding:utf-8 -*-
import os
import re
import json

from modules import gossip_robot, medical_robot, classifier
from utils.json_utils import dump_user_dialogue_context, load_user_dialogue_context


def text_replay(user, msg):
    user_intent = classifier(msg)
    if user_intent in ["greet", "goodbye", "deny", "isbot"]:
        reply = gossip_robot(user_intent)
    elif user_intent == "accept":
        reply = load_user_dialogue_context(user)
        reply = reply.get("choice_answer")
    else:
        reply = medical_robot(msg, user)
        if reply["slot_values"]:
            dump_user_dialogue_context(user, reply)
        reply = reply.get("replay_answer")

    return reply


hello = """
=========================================
=  欢迎使用智能医疗机器人服务，退出按 Q  =
=========================================

"""


def main():
    print(hello)
    print("机器人小智：请问怎么称呼您呢？")
    user_name = input("用户：")
    print("\n")
    print("机器人小智：你好 {0}，有什么可以帮您？".format(user_name))

    while True:
        question = input("用户：")
        if question.lower() == 'q':
            break
        answer = text_replay(user_name, question)
        print("机器人小智：{0}".format(answer.replace('\n', '\n      ')))
        print("\n")


if __name__ == '__main__':
    main()
