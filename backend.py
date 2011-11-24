#!/usr/bin/env python
#-*- coding: utf-8 -*-

##
## backend.py - LODproxy.
##
## Copyright (c) 2010-2012 Koninklijke Bibliotheek - National library of the Netherlands.
##
## this program is free software: you can redistribute it and/or modify
## it under the terms of the gnu general public license as published by
## the free software foundation, either version 3 of the license, or
## (at your option) any later version.
##
## this program is distributed in the hope that it will be useful,
## but without any warranty; without even the implied warranty of
## merchantability or fitness for a particular purpose. see the
## gnu general public license for more details.
##
## you should have received a copy of the gnu general public license
## along with this program. if not, see <http://www.gnu.org/licenses/>.
##

__author__ = "Willem Jan Faber"

import os
import sys
import tempfile
import logging
import urllib2
import hashlib

from pprint import pprint

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        sys.stdout.write("Could not import json, please install python-json\n")
        sys.exit(-1)
try:
    from lxml.etree import parse as xml_parse
    from lxml.etree import Element as xml_Element
    from lxml.etree import fromstring as xml_fromstring
except ImportError:
    try:
        from xml.etree.cElementTree.etree import parse as xml_parse
        from xml.etree.cElementTree.etree import Element as xml_Element
        from xml.etree.cElementTree.etree import fromstring as xml_fromstring
    except ImportError:
        sys.stdout.write("Could not import xmllib, please install python-elementtree\n")
        sys.exit(-1)

DEBUG = False

def log(message, log_level = logging.CRITICAL):
    if DEBUG:
        logging.log(log_level, message)

class OpenData(object):
    headers = {'Accept' : '*/*'}

    def get_data(self, url, force_type = False):

        response_type = "unknown"
        req = urllib2.Request(url = url, headers = self.headers)
        data = False

        log(self.__class__.__name__ + ": Trying to open %s." % url)

        try:
            response = urllib2.urlopen(req)
        except (urllib2.URLError, urllib2.HTTPError) as e:
            if DEBUG:
                log(self.__class__.__name__ + ": %s" % str(e))
                log(self.__class__.__name__ + ": Error while opening %s, Fatal." % url )
            return(False, response_type)
     
        if response.getcode() == 200:
            response_info = response.info()
            if "Content-Type" in response_info:
                if (response_info["Content-Type"].lower().find('json')) > -1:
                    response_type="json"
                elif (response_info["Content-Type"].lower().find('xml')) > -1:
                    response_type = "xml"
                else:
                    print(response_info["Content-Type"])

            if force_type:
                if not force_type == response_type:
                    response_type = force_type
                    log(self.__class__.__name__ + ": Response-type data forced to '%s' from %s." % (response_type, url))
                else: 
                    log(self.__class__.__name__ + ": Response-type data '%s' from %s." % (response_type, url))
            else:
                log(self.__class__.__name__ + ": Response-type data '%s' from %s." % (response_type, url))

            if "Content-Length" in response_info:
                if int(response_info["Content-Length"]) < 5:    # No json data available, #doesnotexist
                    log(self.__class__.__name__ + ": Getting %s bytes from %s" % (response_info["Content-Length"], url))
                else:
                    log(self.__class__.__name__ + ": Getting %s bytes from %s" % (response_info["Content-Length"], url))
            else:
                log(self.__class__.__name__+ ": Getting ? bytes from %s" % (url))

            try:
                data = response.read()
                log(self.__class__.__name__+ ": Got %i bytes from %s" % (len(data), url))
            except:
                log(self.__class__.__name__ + ": Error while reading data")
                return(False, response_type)

            if not len(data) > 0:
                log(self.__class__.__name__+ ": Data size to small (%i bytes) from %s" % (len(data), url))
                return(False, response_type)
        else:
            log(self.__class__.__name__ + ": Did not get a 200 ok response, got %i" % (response.getcode()))
            return(False, response_type)

        if response_type == "xml":
            try:
                data = xml_fromstring(data)
                log(self.__class__.__name__ + ": Converted raw data to xmletree object.")
            except:
                log(self.__class__.__name__ + ": Error while converting raw data to json.")
                return(False, response_type)


        if response_type == "json":
            try:
                data = json.loads(data)
                log(self.__class__.__name__ + ": Converted raw data to json.")
            except:
                log(self.__class__.__name__ + ": Error while converting raw data to json.")
                return(False, response_type)

        return(data, response_type)

    def get_json(self, url):
        return(self.get_data(url, "json")[0])

    def get_xml(self, url):
        return(self.get_data(url, "xml")[0])


class Storage():
    config = {}
    data = {}
    def __init__(self, config):
        self.config = config

    def get(self, *args, **nargs):
        key = args[0]
        log(self.__class__.__name__ + ": Getting %s" % (key))
        if key in self.data:
            if not self.data[key] == None:
                log(self.__class__.__name__ + ": Got %s" % (key))
            else:
                log(self.__class__.__name__ + ": No data for %s" % (key))
                return(False)
            return(self.data[key])
        else:
            log(self.__class__.__name__ + ": No data for %s" % (key))
            return(False)
    
    def store(self, key, data=""):
        if not key in self.data:
            self.data[key] = data
            log("Storing %s via backend : %s" % (key, self.__class__.__name__))
        return(True)

class Files(Storage):
    def __init__(self, config):
        Storage.__init__(self, config)

class Memcache(Storage):
    # mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    def __init__(self, config):
        Storage.__init__(self, config)
        self.mc_handler = memcache.Client(["%s:%s" % (config["hostname_memcache"], config["portname_memcache"])])
        # check to see if memcache is up?

    def get(self, *args, **nargs):
        key = args[0]
        name = nargs["name"]
        record_key = name + "_" + key
        if not record_key in self.data:
            data = self.mc_handler.get(record_key)
            self.data[record_key] = data
        data = Storage.get(self, record_key)
        return(data)

    def store(self, *args, **nargs):
        key = args[0]
        data = args[1]
        name = data["name"]
        record_key = name + "_" + key
        log(self.__class__.__name__ + ": Storing %s" % (record_key))
        self.mc_handler.set(record_key, data)
        Storage.store(self, record_key, data)

class Pickle(Storage):
    def __init__(self, config):
        Storage.__init__(self, config)

    def get(self, *args, **nargs):
        key = args[0]
        filename = self.config["tmp_path"] + os.sep + nargs["name"] + os.sep + hashlib.md5(key).hexdigest()
        if os.path.isfile(filename) and not key in self.data:
            size = os.path.getsize(filename)
            log(self.__class__.__name__ + ": Reading %i bytes for %s from %s" % (size, key, filename))
            with open(filename) as fh:
                data = pickle.load(fh)
                self.data[key] = data
        data = Storage.get(self, key)
        return(data)

    def store(self, *args, **nargs):
        key = args[0]
        data = args[1]
        Storage.store(self, key, data)
        if not os.path.isdir(self.config["tmp_path"]):
            try:
                os.makedirs(self.config["tmp_path"])
            except:
                sys.stderr.write(self.__class__.__name__ + ": Could not create directory %s" % self.config["tmp_path"])
                sys.exit(-1)
        if not os.path.isdir(self.config["tmp_path"]+os.sep+data["name"]):
            try:
                os.makedirs(self.config["tmp_path"]+os.sep+data["name"])
            except:
                sys.stderr.write(self.__class__.__name__ + "Could not create directory %s" % self.config["tmp_path"]+os.sep+data["name"])
                sys.exit(-1)

        filename = self.config["tmp_path"] + os.sep + data["name"] + os.sep + hashlib.md5(key).hexdigest()
    
        log(self.__class__.__name__ + ": Storing %s into %s" % (key, filename))

        with open(filename, "wb") as fh:
            pickle.dump(data, fh)

class backend(object):
    current_backend = False

    #prefered_backends = "pymongo", "couchdb", "sqlite3", "memcache", "pickle", "files"
    prefered_backends = "memcache",""

    config = {"tmp_path" : tempfile.gettempdir()+os.sep+"lod",
              "hostname_memcache" : "127.0.0.1",
              "portname_memcache" : "11211"}

    def __init__(self, func, *arg, **narg):
        self.func = func
        for backend in self.prefered_backends:
            try:
                module = __import__(backend)
                try:
                    if getattr(sys.modules[__name__], backend.title()):
                        setattr(sys.modules[__name__], backend, module)
                        self.current_backend = getattr(sys.modules[__name__], backend.title())(self.config)
                        if DEBUG:
                            log(self.__class__.__name__ + ": Setting backend to %s" % backend)
                        break
                except AttributeError:
                    log(self.__class__.__name__ + ": %s not implemented yet" % backend.title())
            except ImportError:
                log(self.__class__.__name__ + ": %s not found on this system" % backend.title())

        if self.current_backend == False:
            if DEBUG:
                log(self.__class__.__name__ + ": Falling back to native file backend")
            self.current_backend = getattr(sys.modules[__name__],  self.prefered_backends[-1].title())(self.config)
            setattr(self, "store", self.current_backend.store)
            setattr(self, "get", self.current_backend.get)
        else:
            setattr(self, "store", self.current_backend.store)
            setattr(self, "get", self.current_backend.get)

    def __repr__(self):
        return("Selected backend : %s " % self.current_backend)

    def __call__(self, *args, **nargs): # call the calling module from the decorator.
        data = self.get(*args, **nargs)
        if not data:
            data = self.func(*args, **nargs)
            if not data["error"]: self.store(args[0], data)
            return(data)
        else:
            return(data) 

def main(arg):
    if len(arg)>1:
        print("arguments : "+ ",".join(arg[2:]))
    pass

if __name__ == "__main__":
    main(sys.argv)
