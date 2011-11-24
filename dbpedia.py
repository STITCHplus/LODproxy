#!/usr/bin/env python
#-*- coding: utf-8 -*-

##
## dbpedia.py - LODproxy.
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

#if name == "dbpedia":
#    for key in res["data"]["http://dbpedia.org/resource/"+urllib2.quote(record_name)].iteritems():
#        if "http://dbpedia.org/ontology/wikiPageRedirects" in key:
#            res["redirect_to"] = res["data"]["http:/

__author__ = "Willem Jan Faber"

from LODproxy import *
from pprint import pprint

backend.DEBUG = False

def _add_record(label, value, record):
    if not label in record:
        record[label] = value
    else:
        if not type(record[label]) == list:
            val = record[label]
            record[label]=[]
            record[label].append(val)
            record[label].append(value)
        else:
            record[label].append(value)
    return(record)



def get_dbpedia_entry(entry_name):
    dbpedia_entry = get_data_record(entry_name, baseurl = "http://dbpedia.org/data/%s.json", name = "dbpedia")
    return(dbpedia_entry)

def parse_dbpedia_entry(entry_name, dbpedia_entry, *arg):
    if not dbpedia_entry["error"]:
        #print(dbpedia_entry["data"].keys())
        result = dbpedia_entry["data"]
        #result = record["data"]["http://dbpedia.org/resource/Amsterdam"]
        record = {}
        for item in result:
            for name in result[item]:
                for val in result[item][name]:
                    if "lang" in val:
                        if not val["lang"] == "en":
                            label = name.split('/')[-1].split('#')[-1] + "_" + val["lang"]
                        else:
                            label = name.split('/')[-1].split('#')[-1]
                        record = _add_record(label, val["value"], record)
                    else:
                        label = name.split('/')[-1].split('#')[-1] 
                        if not val["value"] == "http://dbpedia.org/resource/%s" % entry_name:
                            if "value" in val:
                                record = _add_record(label, val["value"], record)
                            else:
                                print(label, val)
                                #record = _add_record(label, val["value"], record)
        if len(arg) > 0:
            for item in record:
                if item in arg:
                    print(record[item])
        else:
            pprint(record)
    else:
        print("Error while fetching record: %s" % entry_name)

if __name__ == "__main__":
    entry = "Utrecht"
    dbpedia_entry = get_dbpedia_entry(entry)
    parse_dbpedia_entry(entry, dbpedia_entry, "depiction","appel")
