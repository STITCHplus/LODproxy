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
import urllib2
import backend

from pprint import pprint

backend.DEBUG = DEBUG = True

__author__ = "Willem Jan Faber"

@backend.backend
def get_data_record(*args, **nargs):
    od = backend.OpenData()
    baseurl = nargs["baseurl"]
    record_name = args[0]
    name = nargs["name"]

    if record_name.find('http://') > -1:
        record_name=record_name.split('/')[-1]

    url = baseurl % (urllib2.quote(record_name))
    data = od.get_json(url)
    key = urllib2.quote(record_name)

    res = { "error" : False,
            "redirect_to" : False,
            "doesnotexist" : False,
            "key" : key,
            "name" : name,
            "data" : "", 
            "url" : url }

    if data:
        res["data"] = data
    else:
        res["error"] = True
     
    #if name == "dbpedia":
    #    for key in res["data"]["http://dbpedia.org/resource/"+urllib2.quote(record_name)].iteritems():
    #        if "http://dbpedia.org/ontology/wikiPageRedirects" in key:
    #            res["redirect_to"] = res["data"]["http://dbpedia.org/resource/"+urllib2.quote(record_name)]["http://dbpedia.org/ontology/wikiPageRedirects"][0]["value"]
    return(res)

if __name__ == "__main__":
    record = get_data_record("Amsterdam", baseurl = "http://dbpedia.org/data/%s.jsond", name = "dbpedia")
    print(type(record))
    record = get_data_record("Appel", baseurl = "http://dbpedia.org/sparql?default-graph-uri=http://dbpedia.org&query=DESCRIBE+<http://dbpedia.org/resource/%s>&format=json", name = "dbpedia_sparql")
    print(type(record))
