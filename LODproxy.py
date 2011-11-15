#!/usr/bin/env python
#-*- coding: utf-8 -*-

##
## LODproxy.py - LODproxy.
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

import os
import sys
import time
import logging
import urllib2
import tempfile
import hashlib
import simplejson

from pprint import pprint

__author__ = "Willem Jan Faber"

def log(message, log_level = logging.CRITICAL):
    logging.log(log_level, message)

class Storage():
    config = {}
    data = {}
    def __init__(self, config):
        self.config = config

    def get(self, key):
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

    def get(self, key):
        if os.path.isfile(self.config["tmp_path"] + os.sep + hashlib.md5(key).hexdigest()) and not key in self.data:
            log("Reading %s from %s%s" % (key, self.config["tmp_path"]+os.sep, hashlib.md5(key).hexdigest()))
            with open(self.config["tmp_path"] + os.sep + hashlib.md5(key).hexdigest()) as fh:
                data = pickle.load(fh)
                self.data[key] = data
        data = Storage.get(self, key)
        return(data)

    def store(self, key, data=""):
        Storage.store(self, key, data)
        if not os.path.isdir(self.config["tmp_path"]):
            try:
                os.makedirs(self.config["tmp_path"])
            except:
                sys.stderr.write("Could not create directory %s" % self.config["tmp_path"])
                sys.exit(-1)

        log("Storing %s into %s%s" % (key, self.config["tmp_path"]+os.sep, hashlib.md5(key).hexdigest()))
        with open("%s%s" % (self.config["tmp_path"]+os.sep, hashlib.md5(key).hexdigest()) , "wb") as fh:
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
        data = self.get(*args)
        if not data:
            data = self.func(*args)
            if not data["error"]: self.store(*args, data=data)
            return(data)
        else:
            return(data)   # else return cahed data.

class OpenData(object):
    res = { "error"         : False,
            "redirect_to"   : False,
            "doesnotexist"  : False,
            "sameas"        : False,
            "key" : "",
            "data" : "" }
 
    def get_lod_resource():
        pass

    def get_json():
        pass

    def get_xml():
        pass

@backend
def get_data_record(record_name = "Amsterdam", baseurl = "http://dbpedia.org/data/%s.jsond", name = "dbpedia"):
    headers = {'Accept' : '*/*'}
    if record_name.find('http://') > -1:
        record_name=record_name.split('/')[-1]

    url = baseurl % (urllib2.quote(record_name))
    key = urllib2.quote(record_name)
    req = urllib2.Request(url = url, headers = headers)
    res = { "error" : False,
            "redirect_to" : False,
            "doesnotexist" : False,
            "key" : "",
            "data" : "" }

    res["key"] = key

    try:
        response = urllib2.urlopen(req)
    except (urllib2.URLError, urllib2.HTTPError) as e:
        log(e, logging.FATAL)   
        res["error"] = True
        return(res)
 
    if response.getcode() == 200:
        response_info = response.info()
        if "Content-Type" in response_info:
            if (response_info["Content-Type"].lower().find('json')) > -1:
                response_type="json"

        if "Content-Length" in response_info:
            if int(response_info["Content-Length"]) < 5:    # No json data available, #doesnotexist
                log(u"Got %s bytes from %s" % (response_info["Content-Length"], url))
                res["doesnotexist"] = True
                log("Doesnotexists")
                return(res)
            else:
                log("Getting %s bytes from %s" % (response_info["Content-Length"], url))
        else:
            log("Getting ? bytes from %s" % (url))

        try:
            res["data"] = simplejson.loads(response.read())
            log("Converted into dict for %s" % (url))
        except:
            log("Failed to convert to dict for %s" % (url) , logging.FATAL)
            return(res)
    else:
        log("Did not get a 200 ok response, got %i" % (response.getcode()))
        return(res)
    if name == "dbpedia":
        for key in res["data"]["http://dbpedia.org/resource/"+urllib2.quote(record_name)].iteritems():
            if "http://dbpedia.org/ontology/wikiPageRedirects" in key:
                res["redirect_to"] = res["data"]["http://dbpedia.org/resource/"+urllib2.quote(record_name)]["http://dbpedia.org/ontology/wikiPageRedirects"][0]["value"]
    return(res)

if __name__ == "__main__":
    record = get_data_record("Einstein")
    if not (record["error"] or record["doesnotexist"]):
        if record["redirect_to"]:
            log("Redirect to %s" %  record["redirect_to"])
            record=get_data_record(record["redirect_to"])
        print(len(record))
    elif record["doesnotexist"]:
        log("Recordoesnotexist")
