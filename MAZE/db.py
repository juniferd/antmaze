import cPickle as pickle
import gzip
import antfarm
import copy
import os
import sys

from collections import defaultdict

import threading

db_lock = threading.RLock()

# this holds the farm and the max client counter for a world
class World(object):
    def __init__(self):
        self.farm = antfarm.AntFarm()
        self.farm.populate_farm()
        self.client_counter = 0

# this holds the saved JSON turns for a world 
class WorldJSON(object):
    def __init__(self):
        self.turns = {}

# KEYS: 
#   worlds - set([1,2,3...])
#   world/:id/bucket/:bucket - WorldJSON
#   world/:id - World

def lock_cache(func):
    def inner_locked_func(*args, **kwargs):
        #print "ACQUIRING DB LOCK"
        db_lock.acquire(True)
        ret = func(*args, **kwargs)
        db_lock.release()
        #print "RELEASING DB LOCK"

        return ret

    return inner_locked_func
# loads a key off disk if it isn't already inside our key cache
class KeyCache(object):
    def __init__(self):
        self.__cache = {}

        # keeps track of which keys are "dirty" and still need to be saved
        # to disk
        self.__dirty = defaultdict(bool)


        # stores the last op this was used
        self.__last_used = defaultdict(int)

        self.__write_ops = 0

    @lock_cache
    def get_key(self, key_name, default_value=None):
        self.__last_used[key_name] = self.__write_ops

        if key_name in self.__cache:
            #print "CACHED KEY", key_name

            return self.__cache[key_name]

        #print "GETTING KEY", key_name
        # check if file for key_name exists
        ext = os.path.dirname(os.path.realpath(sys.argv[0]))
        file_path = ext+"/db/%s" % key_name
        if not os.path.exists(file_path):
            self.__cache[key_name] = default_value
            return default_value

        data = default_value
        # open file
        with gzip.open(file_path, "rb") as f:
            try:
                data = pickle.load(f)
            except EOFError:
                print ("EOF ERROR, RETURNING DEFAULT VALUE FOR %s" % key_name)
                data = default_value

        ret = data or default_value
        self.__cache[key_name] = ret
        return ret

    @lock_cache
    def set_key(self, key_name, value):
        #print "SETTING KEY", key_name
        self.__last_used[key_name] = self.__write_ops

        # pickle value
        self.__cache[key_name] = value
        self.__dirty[key_name] = True
        self.__write_ops += 1

        # call save_keys every 50 write ops
        if self.__write_ops % 50 == 0:
            self.save_keys()


    def save_keys(self):
        t = threading.Thread(target=self.__save_keys)
        t.start()

    @lock_cache
    def __save_keys(self):
        evicted = []

        for key in self.__cache:
            if self.__dirty[key]:
                self.save_key(key)
            else:
                # check expiration on this key
                if self.__write_ops - self.__last_used[key] > 100:
                    evicted.append(key)

        for key in evicted:
            print("EVICTING KEY!", key)

            del self.__cache[key]


    @lock_cache
    def save_key(self, key_name):
        value = self.__cache[key_name]

        if not value:
            return

        self.__dirty[key_name] = False

        print("SAVING KEY TO DB", key_name)
        ext = os.path.dirname(os.path.realpath(sys.argv[0]))
        key_name = ext+"/db/%s" % (key_name)
        with gzip.open(key_name, "wb") as f:
            pickle.dump(value, f)
        # open file
        # save value to file and close file

wc = KeyCache()
get_key = wc.get_key
set_key = wc.set_key



def list_worlds():
    return get_key('worlds', default_value=set([0]))

INFO_CHUNK_SIZE=50
# This function returns the saved 'turn' associated with the 
# given world  (maze_id) at the 'action_id'
def get_info(maze_id, action_id):
    bucket = int(action_id) / INFO_CHUNK_SIZE
    info_key = 'world.%s.bucket.%s' % (maze_id, bucket)
    print("INFO KEY", info_key, "ACTION ID", action_id)

    saved_info = get_key(info_key)
    if saved_info:
        return saved_info.turns[action_id]

def save_info(info, maze_id, action_id):
    bucket = int(action_id) / INFO_CHUNK_SIZE

    info_key = 'world.%s.bucket.%s' % (maze_id, bucket)

    saved_info = get_key(info_key)
    if not saved_info:
        print("BUILDING NEW WORLD INFO", info_key)
        saved_info = WorldJSON()

    saved_info.turns[action_id] = info

    set_key(info_key, saved_info)

def get_world(maze_id):
    world_key = "world.%s" % maze_id


    if not get_key(world_key):
        world = World()
        set_key(world_key,world)

        world_list = list_worlds()
        world_list.add(maze_id)
        set_key('worlds',world_list)


    return get_key(world_key)

def save_world(maze_id, world):
    world_key = "world.%s" % maze_id
    set_key(world_key,world)
