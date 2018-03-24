import websocket
import json
import io
import logging
import re
import time
import os

logging.basicConfig()

__f = None          #file for stream of messages
__u = None          #file for list of users
__c = None          #file for config
__last_message = {} #latest received message of each user
contacts = {}       #map of user names
config   = {}       #map of config

def on_message(ws, message):

    data = json.loads(message)

    if is_received(data):
        tag =   data["push"]["notification_tag"]
        title = data["push"]["title"]
        body =  data["push"]["body"].split('\n')

        (group, user) = get_user_info(title)
        update_user_info(group, user, tag)

        update_config(data)

        global __last_message
        if tag in __last_message:
            if __last_message[tag] in body:
                i = len(body) - body[::-1].index(__last_message[tag]) - 1  #find index of last occurrence of message
            else:
                i = -1 
            msg = body[i+1:]
        else:
            msg = body[-1:]
        
        if msg:
            __last_message[tag] = msg[-1] 

        update_msg_file(group, user, msg)

    if is_sent(data):
        to_user = contacts[data["push"]["conversation_iden"]["tag"]]
        to_msg = data["push"]["message"]
        if to_user and to_msg:
            update_sent_msg(to_user, to_msg)

def on_error(ws, error):
    print(error)

def on_close(ws):
    ### closed ###
    pass

def on_open(ws):
    ### opened ###
    pass

def is_received(data):
    if data is not None and \
       data.get("type") == "push" and \
       data.get("push") and \
       data["push"].get("type") == "mirror" and \
       data["push"].get("package_name") == "com.whatsapp" and \
       data["push"].get("notification_tag") and \
       data["push"].get("title") and \
       data["push"].get("body"):
        return True
    return False

def is_sent(data):
    if data is not None and \
       data.get("type") == "push" and \
       data.get("push") and \
       data["push"].get("type") == "messaging_extension_reply" and \
       data["push"].get("package_name") == "com.pushbullet.android" and \
       data["push"].get("conversation_iden") and \
       data["push"]["conversation_iden"].get("tag") and \
       data["push"].get("message"):
        return True
    return False 

def get_user_info(title):
    title = re.sub(r"\(\d+ messages\)", "", title) #remove msg number info from title
    title = title.replace(u'\u200b', "")
    title = title.strip().split(':')
    if len(title) > 1:
        if title[-1].strip():
            group = ':'.join(title[:-1]).strip()
            user = title[-1].strip()
        else:
            group = None
            user = ':'.join(title[:-1]).strip()
    else:
        group = None
        user = title[0].strip()

    return (group, user)

def update_user_info(group , user, tag):

    global contacts, __u
    if group:
        name = group
    else:
        name = user

    if tag not in contacts or contacts[tag] != name:
        __u.write(tag + '|||' + name + '\n')
        __u.flush()
        contacts[tag] = name

def update_config(data):

    global config, __c
    tags = ['source_user_iden', 'source_device_iden'] 
    for tag in tags:
        if tag not in config and data["push"][tag]:
            __c.write(tag + ',' + data["push"][tag] + '\n')
            __c.flush()
            config[tag] = data["push"][tag]

def load_user_info(usr_file):

    global contacts
    with io.open(usr_file, mode='r', encoding='utf-8') as u_file:
        for line in u_file:
            user_info = line.strip().split('|||')
            if len(user_info) > 1:
                contacts[user_info[0]] = user_info[1]

def load_config(conf_file):
    global config
    with io.open(conf_file, mode='r', encoding='utf-8') as c_file:
        for line in c_file:
            conf_info = line.strip().split(',')
            if len(conf_info) > 1:
                config[conf_info[0]] = conf_info[1]

def update_msg_file(group , user, msg):
 
    global __f
    if msg:
        if group:
            __f.write(group + " : " + user + " : " + '\n'.join(msg) + "\n")
            __f.flush()
        else:
            __f.write(user + " : " + '\n'.join(msg) + "\n")
            __f.flush()

def update_sent_msg(user, msg):
    global __f
    __f.write(user + " : You : " + msg + "\n")
    __f.flush()

def init(dir):

    global __f, __u, __c
    msg_file = os.path.join(dir,"msg")
    usr_file = os.path.join(dir,"usr")
    cnf_file = os.path.join(dir,"conf")
    __f = io.open(msg_file, mode='w+', encoding='utf-8')
    __u = io.open(usr_file, mode='a+', encoding='utf-8')
    __c = io.open(cnf_file, mode='a+', encoding='utf-8')
    load_config(cnf_file)
    load_user_info(usr_file)
    
def start_stream(token):

    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://stream.pushbullet.com/websocket/" + token,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    #infinite loop as partner might drop connection
    while True:
        ws.run_forever()
        #restarting in 5 seconds...
        time.sleep(5)
