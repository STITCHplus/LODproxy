#!/usr/bin/env python
#-*- coding: utf-8 -*-

##
## google_isbn.py - LODproxy.
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
from pprint import pprint

backend.DEBUG = True 

def get_google_isbn(isbn):
    google_isbn = get_data_record(isbn, baseurl = "http://www.google.com/books/feeds/volumes/?q=ISBN<%s>", name = "google_isbn", force_type="feed")
    return(google_isbn)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        entry = "0743264738"
        google_isbn = get_google_isbn(entry)
        pprint(google_isbn)
    else:
        entry = quote(sys.argv[1])
        gogole_isbn = get_google_isbn(entry)
        pprint(google_isbn)

