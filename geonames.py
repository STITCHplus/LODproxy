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

backend.DEBUG = False

if __name__ == "__main__":
    record = get_data_record("Utrecht", baseurl = "http://ws.geonames.org/searchJSON?q=%s", name = "geonames")
    if type(record["data"]) == dict:
        if record["data"]["totalResultsCount"] > 0:
            result = record["data"]["geonames"][0]
            for item in result:
                print("%12s : %s" % (item, result[item]))
    else:
        print("Geonames is down..")
