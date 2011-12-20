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
import feedparser

from pprint import pprint

try:
    from cjson import decode as loads
except ImportError:
    try:
        from json import loads
    except ImportError:
        try:
            from simplejson import loads
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

DEBUG = True

def log(message, log_level = logging.CRITICAL):

    global DEBUG
    if DEBUG:
        logging.log(log_level, message)

class OpenData(object):
    headers = {'Accept' : '*/*'}

    def get_data(self, url, force_type = False):
    
        response_type = "unknown"
        print(url)
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
                log(self.__class__.__name__+ ": Getting ? bytes from %s." % (url))

            try:
                data = response.read()
                log(self.__class__.__name__+ ": Got %i bytes from %s." % (len(data), url))
            except:
                log(self.__class__.__name__ + ": Error while reading data.")
                return(False, response_type)

            if not len(data) > 0:
                log(self.__class__.__name__+ ": Data size to small (%i bytes) from %s." % (len(data), url))
                return(False, response_type)
        else:
            log(self.__class__.__name__ + ": Did not get a 200 ok response, got %i." % (response.getcode()))
            return(False, response_type)

        if response_type == "xml":
            try:
                data = xml_fromstring(data)
                log(self.__class__.__name__ + ": Converted raw data to xmletree object.")
                walker=data.iter()
                for item in walker:
                    print(item, item.tag, item.text)
            except:
                log(self.__class__.__name__ + ": Error while converting raw data to xml.")
                return(False, response_type)

        if response_type == "feed":
            try:
                data = feedparser.parse(data)
                try:
                    data["feed"].pop("updated_parsed")
                except:
                    pass
                log(self.__class__.__name__ + ": Converted raw data to feed object.")
                #walker=data.iter()
                #for item in walker:
                #    print(item, item.tag, item.text)
            except:
                log(self.__class__.__name__ + ": Error while converting raw data to feed.")
                return(False, response_type)

        if response_type == "json":
            try:
                data = loads(data)
                log(self.__class__.__name__ + ": Converted raw data to json.")
            except:
                log(self.__class__.__name__ + ": Error while converting raw data to json.")
                return(False, response_type)

        return(data, response_type)

    def get_feed(self, url):
        return(self.get_data(url, "feed")[0])

    def get_json(self, url):
        return(self.get_data(url, "json")[0])

    def get_xml(self, url):
        return(self.get_data(url, "xml")[0])

class Storage():
    config = {}
    data = {}
    MAX_INMEM = 2

    def __init__(self, config):
        self.config = config

    def get(self, *args, **nargs):
        key = args[0]
        log(self.__class__.__name__ + ": Getting %s (mem)." % (key))
        if key in self.data:
            if not self.data[key] == None:
                log(self.__class__.__name__ + ": Got %s (mem)." % (key))
            else:
                log(self.__class__.__name__ + ": No data for %s." % (key))
                return(False)
            return(self.data[key])
        else:
            log(self.__class__.__name__ + ": No data for %s (mem)." % (key))
            return(False)
    
    def store(self, key, data=""):
        log(self.__class__.__name__ + ": Storing %s (mem)." % (key))
        if not key in self.data:
            if len(self.data.keys()) > self.MAX_INMEM-1:
                r = self.data.keys()[0]
                self.data.pop(r)
            self.data[key] = data
        return(True)

    def is_sane(self):
        log("%s: Running sanity test." % (self.__class__.__name__))
        data = self.get("test", name="test")
        if type(data) == dict:
            if "data" in data:
                if data["data"] == "appel":
                    log("%s: Is sane." % (self.__class__.__name__))
                    return(True)

        self.store("test", {"name" : "test", "data" : "appel"})
        data = self.get("test", name="test")
        if type(data) == dict:
            if data["data"] == "appel":
                log("%s: Is sane." % (self.__class__.__name__))
                return(True)
        log("%s: Is not sane." % (self.__class__.__name__))
        return(False)


class Files(Storage):
    def __init__(self, config):
        Storage.__init__(self, config)

class Pymongo(Storage):
    """
        Mongodb store backend.

    """
    def __init__(self, config):
        import string
        from pymongo.bson import BSON
        self.BSON = BSON
        Storage.__init__(self, config)
        try:
            port = string.atoi(config["portname_pymongo"])
        except ValueError:
            sys.stdout.write("Mongodb portname must be Integer.\nExit with errors.\n")
            sys.exit(-1)
        try:
            self.pymongo_handler = pymongo.Connection(config["hostname_pymongo"], port, network_timeout=1)
            self.pymongo_db = self.pymongo_handler["lod_proxy"]
        except:
            raise EnvironmentError("Not sane.")
            
    def get(self, *args, **nargs):
        key = args[0]
        name = nargs["name"]
        record_key = hashlib.md5(name + "_" + key).hexdigest()

        from pymongo import bson
        from pymongo.binary import Binary

        data = Storage.get(self, record_key)
        if data: return(data)
        log(self.__class__.__name__ + ": Getting %s." % (record_key))
        try:
            for data in self.pymongo_db[name].find({"id" : record_key}):
                data = data["data"]
                log(self.__class__.__name__ + ": Got %s." % (record_key))
                return(self.BSON(data).to_dict())
        except:
            return(False)

    def store(self, *args, **nargs):
        key = args[0]
        data = args[1]
        name = data["name"]
        record_key = name + "_" + key
        log(self.__class__.__name__ + ": Storing %s" % (record_key))
        odata = data
        from pymongo.binary import Binary
        data = Binary(self.BSON.from_dict(data))
        self.pymongo_db[name].save({"id" : hashlib.md5(record_key).hexdigest(), "data" : data})
        Storage.store(self, record_key, odata)

class Memcache(Storage):
    """
        Memcache store backend.

    """
    def __init__(self, config):
        Storage.__init__(self, config)
        try:
           self.mc_handler = memcache.Client(["%s:%s" % (config["hostname_memcache"], config["portname_memcache"])])
        except:
            raise EnvironmentError("Not sane.")

    def get(self, *args, **nargs):
        key = args[0]
        name = nargs["name"]
        record_key = name + "_" + key
        if not record_key in self.data:
            data = self.mc_handler.get(hashlib.md5(record_key).hexdigest())
            self.data[record_key] = data
        data = Storage.get(self, record_key)
        return(data)

    def store(self, *args, **nargs):
        key = args[0]
        data = args[1]
        name = data["name"]
        record_key = name + "_" + key
        log(self.__class__.__name__ + ": Storing %s" % (record_key))
        self.mc_handler.set(hashlib.md5(record_key).hexdigest(), data)
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
    prefered_backends = "pymongo", "memcache", "pickle", "files"

    config = {"tmp_path" : tempfile.gettempdir()+os.sep+"lod",
              "hostname_memcache" : "127.0.0.1",
              "portname_memcache" : "11211",
              "hostname_pymongo" : "192.87.165.3",
              "portname_pymongo" : "27017"}

    def __init__(self, func, *arg, **narg):
        self.func = func
        for backend in self.prefered_backends:
            try:
                module = __import__(backend)
                try:
                    if getattr(sys.modules[__name__], backend.title()):
                        setattr(sys.modules[__name__], backend, module)
                        try:
                            self.current_backend = getattr(sys.modules[__name__], backend.title())(self.config)
                        except EnvironmentError:
                            raise EnvironmentError("Not sane.")
                        if not self.current_backend.is_sane():
                            raise EnvironmentError("Not sane.")
                        if DEBUG:
                            log(self.__class__.__name__ + ": Setting backend to %s." % backend)
                        break
                except EnvironmentError:
                    log(self.__class__.__name__ + ": %s Failed backend sanity test." % backend.title())
                except AttributeError:
                    log(self.__class__.__name__ + ": %s not implemented yet." % backend.title())
            except ImportError:
                log(self.__class__.__name__ + ": %s not found on this system." % backend.title())

        if self.current_backend == False:
            if DEBUG:
                log(self.__class__.__name__ + ": Falling back to native file backend.")
            self.current_backend = getattr(sys.modules[__name__],  self.prefered_backends[-1].title())(self.config)
            setattr(self, "store", self.current_backend.store)
            setattr(self, "get", self.current_backend.get)
        else:
            setattr(self, "store", self.current_backend.store)
            setattr(self, "get", self.current_backend.get)

    def __repr__(self):
        return("Selected backend : %s." % self.current_backend)

    def __call__(self, *args, **nargs): # call the calling module from the decorator.
        data = self.get(*args, **nargs)
        if not data:
            data = self.func(*args, **nargs)
            if not data["error"]: self.store(args[0], data)
            return(data)
        else:
            return(data) 

def main(arguments):
    pass

if __name__ == "__main__":
    main(sys.argv)
