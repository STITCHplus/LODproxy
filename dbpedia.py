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

__author__ = "Willem Jan Faber"

from LODproxy import *
from pprint import pprint
from urllib2 import unquote
from urllib2 import quote

backend.DEBUG = False

def _add_record(label, value, record):
    if value.find('http://dbpedia.org/resource/') > -1 and not value.find('/class/') > -1:
        value = unquote(value.replace("http://dbpedia.org/resource/", "").encode('utf-8')).replace('_', ' ')
    else:
        value = value.encode('utf-8')

    if not label in record:
        record[label] = value
    else:
        if not type(record[label]) == list:
            val = record[label]
            record[label]=[]
            record[label].append(val)
            if not val == value:
                record[label].append(value)
        else:
            if not value in record[label]:
                record[label].append(value)
    return(record)

def get_dbpedia_entry(entry_name):
    dbpedia_entry = get_data_record(entry_name, baseurl = "http://dbpedia.org/data/%s.json", name = "dbpedia")
    entry_name = unicode(quote(entry_name.replace(' ','_')),'utf-8')
    if "http://dbpedia.org/ontology/wikiPageRedirects" in dbpedia_entry["data"]["http://dbpedia.org/resource/%s" % entry_name]:
        entry_name = dbpedia_entry["data"]["http://dbpedia.org/resource/%s" % entry_name]["http://dbpedia.org/ontology/wikiPageRedirects"][0]["value"]
        dbpedia_entry = get_data_record(entry_name, baseurl = "http://dbpedia.org/data/%s.jsond", name = "dbpedia")
    return(dbpedia_entry)

def parse_dbpedia_entry(entry_name, dbpedia_entry, *arg):
    entry_name = unicode(quote(entry_name.replace(' ','_')),'utf-8')
    if not dbpedia_entry["error"]:
        result = dbpedia_entry["data"]
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
                                if not val["value"] == entry_name:
                                    record = _add_record(label, val["value"], record)
                            else:
                                if not val == entry_name:
                                    record = _add_record(label, val, record)
        ret = {}
        if len(arg) > 0:
            for item in record:
                if item in arg:
                    if type(record[item]) == list:
                        line = ", ".join(record[item])
                        ret[item.encode('utf-8')] = line
                    else:
                        ret[item.encode('utf-8')] = record[item]
            return(ret)
        else:
            return(record)
    else:
        print("Error while fetching record: %s" % entry_name)
        return(False)

if __name__ == "__main__":
    entry = "Einstein"
    dbpedia_entry = get_dbpedia_entry(entry)
    print parse_dbpedia_entry(dbpedia_entry["key"], dbpedia_entry, "name")["name"]
    print parse_dbpedia_entry(dbpedia_entry["key"], dbpedia_entry, "abstract_nl")["abstract_nl"]
    print parse_dbpedia_entry(dbpedia_entry["key"], dbpedia_entry, "spouse")["spouse"]
    entry = parse_dbpedia_entry(dbpedia_entry["key"], dbpedia_entry, "spouse")["spouse"]
    dbpedia_entry = get_dbpedia_entry(entry)
    print parse_dbpedia_entry(dbpedia_entry["key"], dbpedia_entry, "abstract_nl")["abstract_nl"]
    
