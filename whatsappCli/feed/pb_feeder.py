from collections import OrderedDict
import os
import io
import json
import requests
import threading
import time

from feeder import Feeder
import pb_stream
from pb_stream import contacts
from pb_stream import config
from pkg_resources import resource_string

class PBFeeder(Feeder):
    """ whatsapp chat feed using pushbullet"""

    def __init__(self, pb_token, dir=os.path.join(os.path.expanduser("~"),".whatsapp-cli")):
        self.pb_token = pb_token
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.dir = dir
        self.starting_lines = 10
        self.reply_template = json.loads(resource_string(__name__, 'data/reply.json'), object_pairs_hook=OrderedDict)
        self.__pb_start_stream()

    def __pb_start_stream(self):
        pb_stream.init(self.dir)
        thread = threading.Thread(
            target=pb_stream.start_stream, args=(self.pb_token,))
        thread.daemon = True
        thread.start()

    def users(self):
        return contacts.values()
  
    def add_user(self, number, name):
        pb_stream.update_user_info(None, name, number + '@s.whatsapp.net')
 
    def get(self, user = None):
        if user is not None:
            tag = self.resolve_user(user)
            full_name = contacts[tag]
            return self.__tail(self.__filter(full_name))
        else:
            return self.__tail()

    def post(self, user, msg):
        tag = self.resolve_user(user)
        req = self.reply_template.copy()
        req["push"]["conversation_iden"]["tag"] = tag
        req["push"]["message"] = msg
        req["push"]["source_user_iden"] = config["source_user_iden"]
        req["push"]["target_device_iden"] = config["source_device_iden"]

        headers = {}
        headers["Content-Type"] = "application/json"
        headers["Access-Token"] = self.pb_token
        url = 'https://api.pushbullet.com/v2/ephemerals'
        requests.post(url, data=json.dumps(req), headers=headers)

    def resolve_user(self, name):
        results = []
        if name.isnumeric() and len(name) == 12:
            results.append(name + '@s.whatsapp.net')
        else:
            for c_tag, c_name in contacts.iteritems():
                if name.lower() in c_name.lower():
                    results.append(c_tag)
        if len(results) == 1:
            return results[0]
        else:
            raise ValueError('0 or more than 1 matches', results)

    def __filter(self, pattern):
        return lambda line: line.startswith(pattern)

    def __seek_to_n_lines_from_end(self, f, numlines=10):
	"""
	Seek to `numlines` lines from the end of the file `f`.
	"""
        f.seek(0, 2)  # seek to the end of the file
        file_pos = f.tell()
        avg_line_len = 100
        toread = min(avg_line_len*numlines, file_pos)
    	f.seek(file_pos - toread, 1)

    def __tail(self, filter = None):
        """
        A generator for reading new lines off of the end of a file.  To start with,
        the last `starting_lines` lines will be read from the end.
        """
        filename = self.dir + "/msg"
	with io.open(filename,mode='r',encoding='utf-8') as f:
	    current_size = os.stat(filename).st_size
        #no seek to n lines. read from beginning instead
	    #self.__seek_to_n_lines_from_end(f, self.starting_lines)
	    while True:
		new_size = os.stat(filename).st_size

		where = f.tell()
		line = f.readline()
		if not line:
		    if new_size < current_size:
			# the file was probably truncated, reopen
                        f.close()
			f = io.open(filename,mode='r',encoding='utf-8')
			current_size = new_size
			dashes = "-" * 20
			yield "\n"
			yield "\n"
			yield "%s messages might be missing %s" % (dashes, dashes)
			yield "\n"
			yield "\n"
			#time.sleep(0.25)
		    else:
			#time.sleep(0.25)
			f.seek(where)
		else:
		    current_size = new_size
                    if filter is not None and not filter(line):
		        pass  #filtered out
                    else:
                        yield line

    
