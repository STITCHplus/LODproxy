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

__author__ = "Willem Jan Faber"

import os
import sys
import urllib2
import backend

from pprint import pprint

backend.DEBUG = True

@backend.backend
def get_data_record(*args, **nargs):
    od = backend.OpenData()
    baseurl = nargs["baseurl"]
    record_name = args[0]
    name = nargs["name"]

    if record_name.find('http://') > -1:
        record_name=record_name.split('/')[-1]

    url = baseurl % (urllib2.quote(record_name.replace(' ', '_')))

    if not "force_type" in nargs:
        data = od.get_json(url)
    else:
        if nargs["force_type"] == "xml":
            data = od.get_xml(url)
        elif nargs["force_type"] == "feed":
            data = od.get_feed(url)
        else:
            data = od.get_json(url)


    #key = urllib2.quote(record_name)
    key = record_name

    res = { "error" : False,
            "key" : key,
            "name" : name,
            "data" : "", 
            "url" : url }
    if data:
        res["data"] = data
    else:
        res["error"] = True
    return(res)


if __name__ == "__main__":
    #record = get_data_record("Appel", baseurl = "http://dbpedia.org/sparql?default-graph-uri=http://dbpedia.org&query=DESCRIBE+<http://dbpedia.org/resource/%s>&format=json", name = "dbpedia_sparql")
    #print(record)
    backend.DEBUG = True
    #try:
    #    record = get_data_record("0743264738", baseurl = "http://www.librarything.com/api/thingISBN/%s", name = "LIBRARYTHING_ISBN", force_type = "xml")
    #    pprint(record)
    #except:
    #    pass

    #http://www.google.com/books/feeds/volumes/?q=Amsterdam
    record = get_data_record("0743254748", baseurl = "http://www.google.com/books/feeds/volumes/?q=%s", name = "LIBRARYTHING_ISBN", force_type = "feed")
    pprint(record)

