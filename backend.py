#!/usr/bin/env python

import os, sys, tempfile
import logging, urllib2, hashlib

from pprint import pprint

"""
    Program written by : Willem Jan Faber
    This program is licensed under the LGPLv2 or LGPLv3 license using following text:

      This program is free software; you can redistribute it and/or
      modify it under the terms of the GNU Lesser General Public
      License as published by the Free Software Foundation; either
      version 2 of the License, or (at your option) version 3.
      
      This program is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
      Lesser General Public License for more details.
      
      You should have received a copy of the GNU Lesser General Public
      License along with the program; if not, see <http://www.gnu.org/licenses/>
"""

DEBUG = True

def log(message, log_level = logging.CRITICAL):
    if DEBUG:
        logging.log(log_level, message)

class Storage():
    config = {}
    data = {}
    def __init__(self, config):
        self.config = config

    def get(self, *args, **nargs):
        key = args[0]
        log("Getting %s via backend : %s" % (key, self.__class__.__name__))
        if key in self.data:
            log("Got %s via backend : %s" % (key, self.__class__.__name__))
            return(self.data[key])
        else:
            log("No data for %s via backend : %s" % (key, self.__class__.__name__))
            return(False)
    
    def store(self, key, data=""):
        if not key in self.data:
            self.data[key] = data
            log("Storing %s via backend : %s" % (key, self.__class__.__name__))
        return(True)

class Files(Storage):
    def __init__(self, config):
        Storage.__init__(self, config)

class Pickle(Storage):
    def __init__(self, config):
        Storage.__init__(self, config)

    def get(self, *args, **nargs):
        key = args[0]
        self.config["tmp_path"] = self.config["tmp_path"] 
        if os.path.isfile(self.config["tmp_path"] + os.sep + nargs["name"] + os.sep + hashlib.md5(key).hexdigest()) and not key in self.data:
            log("Reading %s from %s%s" % (key, self.config["tmp_path"] +os.sep + nargs["name"], hashlib.md5(key).hexdigest()))
            with open(self.config["tmp_path"] + os.sep + nargs["name"] + os.sep + hashlib.md5(key).hexdigest()) as fh:
                data = pickle.load(fh)
                self.data[key] = data
        data = Storage.get(self, key)
        return(data)

    def store(self, *args, **nargs):
        key = args[0]
        data = nargs["data"]
        Storage.store(self, key, data)
        if not os.path.isdir(self.config["tmp_path"]):
            try:
                os.makedirs(self.config["tmp_path"])
            except:
                sys.stderr.write("Could not create directory %s" % self.config["tmp_path"])
                sys.exit(-1)
        if not os.path.isdir(self.config["tmp_path"]+os.sep+data["name"]):
            try:
                os.makedirs(self.config["tmp_path"]+os.sep+data["name"])
            except:
                sys.stderr.write("Could not create directory %s" % self.config["tmp_path"]+os.sep+data["name"])
                sys.exit(-1)

        log("Storing %s into %s%s" % (key, self.config["tmp_path"] + os.sep + data["name"] + os.sep, hashlib.md5(key).hexdigest()))
        with open("%s%s" % (self.config["tmp_path"] + os.sep + data["name"] + os.sep, hashlib.md5(key).hexdigest()) , "wb") as fh:
            pickle.dump(data, fh)

class backend(object):
    prefered_backends = "pymongo", "couchdb", "sqlite3", "memcache", "pickle", "files"
    current_backend = False
    config = { "tmp_path" : tempfile.gettempdir()+os.sep+"lod",
                 "hostname" : None,
                 "portname" : None }

    def __init__(self, func, *arg, **narg):
        self.func = func
        for backend in self.prefered_backends:
            try:
                module = __import__(backend)
                try:
                    if getattr(sys.modules[__name__], backend.title()):
                        setattr(sys.modules[__name__], backend, module)
                        self.current_backend = getattr(sys.modules[__name__], backend.title())(self.config)
                        log("Setting backend to %s" % backend)
                        break
                except AttributeError:
                    log("Backend %s not implemented yet" % backend)
            except ImportError:
                log("Module %s not found on this system" % backend)

        if self.current_backend == False:
            log("Falling back to native file backend")
            self.current_backend = getattr(sys.modules[__name__],  self.prefered_backends[-1].title())(self.config)
            setattr(self, "store", self.current_backend.store)
            setattr(self, "get", self.current_backend.get)
        else:
            setattr(self, "store", self.current_backend.store)
            setattr(self, "get", self.current_backend.get)

    def __repr__(self):
        return("Selected backend : %s " % self.current_backend)

    def __call__(self, *args, **nargs):
        data = self.get(*args, **nargs)
        if not data:
            data = self.func(*args, **nargs)
            if not data["error"]: self.store(*args, data=data)
            return(data)
        else:
            return(data)   # else return cahed data.


def main(arg):
    if len(arg)>1:
        print("arguments : "+ ",".join(arg[2:]))
    pass

if __name__ == "__main__":
    main(sys.argv)

