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

import backend

from pprint import pprint

__author__ = "Willem Jan Faber"
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

@backend.backend
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
            backend.log("Redirect to %s" %  record["redirect_to"])
            record=get_data_record(record["redirect_to"])
        print(len(record["data"]))
    elif record["doesnotexist"]:
        log("Recordoesnotexist")
