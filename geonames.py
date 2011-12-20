#!/usr/bin/env python
#-*- coding: utf-8 -*-

##
## geonames.py - LODproxy.
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
import sys
from urllib2 import quote

backend.DEBUG = True 


def get_geoname_entry(entry_name):
    geoname_entry = get_data_record(entry_name, baseurl = "http://ws.geonames.org/searchJSON?q=%s", name = "geonames")
    return(geoname_entry)

def parse_geoname_entry(entry_name, geoname_entry, record_numer = 0):
    if not geoname_entry["error"]:
        print(geoname_entry["data"].keys())
        result = geoname_entry["data"]["geonames"][record_numer]
        for item in result:
            print("%12s : %s" % (item, result[item]))
        else:
            print("No entry for record: %s position %i"  % (entry_name, record_numer))
    else:
        print("Error while fetching record: %s" % entry_name)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        entry = "Utrecht"
        geoname_entry = get_geoname_entry(entry)
        parse_geoname_entry(entry, geoname_entry)
    else:
        entry = quote(sys.argv[1])
        geoname_entry = get_geoname_entry(entry)
        parse_geoname_entry(entry, geoname_entry)

