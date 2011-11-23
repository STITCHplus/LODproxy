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
import urllib2
import backend

from pprint import pprint

backend.DEBUG = DEBUG = True
__author__ = "Willem Jan Faber"

try:
    import json
except ImportError:
    import simplejson as json

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
        sys.stdout.write("Could not import xmllib, please install elementtree\n")
        sys.exit(-1)

class OpenData(object):
    headers = {'Accept' : '*/*'}

    def get_data(self, url, force_type = False):
        req = urllib2.Request(url = url, headers = self.headers)
        data = False
        response_type = "unknown"

        backend.log(self.__class__.__name__ + ": Trying to open %s." % url)
        try:
            response = urllib2.urlopen(req)
        except (urllib2.URLError, urllib2.HTTPError) as e:
            backend.log(self.__class__.__name__ + ": %s" % str(e))
            backend.log(self.__class__.__name__ + ": Error while opening %s, Fatal." % url )
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
                    backend.log(self.__class__.__name__ + ": Response-type data forced to '%s' from %s." % (response_type, url))
                else: 
                    backend.log(self.__class__.__name__ + ": Response-type data '%s' from %s." % (response_type, url))
            else:
                backend.log(self.__class__.__name__ + ": Response-type data '%s' from %s." % (response_type, url))

            if "Content-Length" in response_info:
                if int(response_info["Content-Length"]) < 5:    # No json data available, #doesnotexist
                    backend.log(self.__class__.__name__ + ": Getting %s bytes from %s" % (response_info["Content-Length"], url))
                else:
                    backend.log(self.__class__.__name__ + ": Getting %s bytes from %s" % (response_info["Content-Length"], url))
            else:
                backend.log(self.__class__.__name__+ ": Getting ? bytes from %s" % (url))

            try:
                data = response.read()
                backend.log(self.__class__.__name__+ ": Got %i bytes from %s" % (len(data), url))
            except:
                backend.log(self.__class__.__name__ + ": Error while reading data")
                return(False, response_type)
        else:
            backend.log(self.__class__.__name__ + ": Did not get a 200 ok response, got %i" % (response.getcode()))
            return(False, response_type)

        if response_type == "xml":
            data = xml_fromstring(data)

        if response_type == "json":
            data = json.loads(data)

        return(data, response_type)

    def get_json(self, url):
        return(self.get_data(url, "json")[0])

    def get_xml(self, url):
        return(self.get_data(url, "xml")[0])

@backend.backend
def get_data_record(*args, **nargs):
    od = OpenData()

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

