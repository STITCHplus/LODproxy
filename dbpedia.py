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


"""
Dbpedia a easy to use library to get a dbpedia record, cache and parse it.
    Usage: dbpedia <dbpedia_identifier>
"""

from LODproxy import *
from pprint import pprint
from urllib2 import unquote
from urllib2 import quote



__all__ = ["DBPedia"]

__author__ = "Willem Jan Faber <wjf@fe2.nl>"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 National library of the Netherlands, %s. All rights reserved." % __author__
__licence__ = "GNU GPL"


backend.DEBUG = True

class DBPedia(object):
    def __init__(self, entry_name):
        self.entry = dbpedia_entry = get_data_record(entry_name, baseurl = "http://dbpedia.org/data/%s.json", name = "dbpedia")
        self.name = unicode(quote(entry_name.replace(' ','_')),'utf-8').encode('utf-8')
        if (len(dbpedia_entry["data"])) > 0:
            if "http://dbpedia.org/ontology/wikiPageRedirects" in dbpedia_entry["data"]["http://dbpedia.org/resource/%s" % self.name]:
                self.name = dbpedia_entry["data"]["http://dbpedia.org/resource/%s" % entry_name]["http://dbpedia.org/ontology/wikiPageRedirects"][0]["value"].split('/')[-1].encode('utf-8')
                self.entry = get_data_record(self.name, baseurl = "http://dbpedia.org/data/%s.jsond", name = "dbpedia")

    def _add_record(self, label, value, record):
        if type(value) == str or type(value) == unicode:
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

    def parse(self, *arg):
        if not self.entry["error"]:
            result = self.entry["data"]
            record = {}
            for item in result:
                for name in result[item]:
                    for val in result[item][name]:
                        if "lang" in val:
                            if not val["lang"] == "en":
                                label = name.split('/')[-1].split('#')[-1] + "_" + val["lang"]
                            else:
                                label = name.split('/')[-1].split('#')[-1]
                            record = self._add_record(label, val["value"], record)
                        else:
                            label = name.split('/')[-1].split('#')[-1] 
                            if not val["value"] == "http://dbpedia.org/resource/%s" % self.name:
                                if "value" in val:
                                    if not val["value"] == self.name:
                                        record = self._add_record(label, val["value"], record)
                                else:
                                    if not val == self.name:
                                        record = self._add_record(label, val, record)
            ret = {}
            if len(arg) > 0:
                for item in record:
                    if item in arg:
                        if type(record[item]) == list:
                            line = ", ".join(record[item])
                            ret[item.encode('utf-8')] = line
                        else:
                            ret[item.encode('utf-8')] = record[item]
                if len(arg) == 1:
                    if (arg[0] in ret):
                        return(ret[arg[0]])
                    else:
                        return(ret)
                else:
                    return(ret)
            else:
                return(record)
        else:
            print("Error while fetching record: %s" % self.name)
            return(False)

def demo():
    entry = "Einstein"
    print("Getting %s.." % entry)
    dbpedia_entry = DBPedia(entry)
    print(" " +dbpedia_entry.parse("name"))
    print("Getting spouse of %s.." % entry)
    dbpedia_entry = DBPedia(dbpedia_entry.parse("spouse"))
    print(" " + dbpedia_entry.parse("abstract_nl"))

def _usage(stream):
    stream.write(__doc__ + "\n")

def main(arguments):
    from pprint import pprint
    import getopt

    try:
        opts, args = getopt.getopt(arguments, "dbpedia:", ["help", "version", "license"])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-l", "--license"):
            sys.stdout.write(__licence__)
            sys.exit(0)
        if opt in ("-h", "--help"):
            _usage(sys.stdout)
            sys.exit(0)
        if opt in ("-v", "--version"):
            sys.stdout.write(__version__)
            sys.exit(0)
    query = "_".join(args)

    if query != "":
        dbpedia_entry = DBPedia(query)
        name = dbpedia_entry.parse("name")
        if name:
            pprint(dbpedia_entry.parse())
    else:
        sys.stdout.write("Did not get any arguments.\n")
        _usage(sys.stdout)
        sys.stdout.write("Running demo..\n\n")
        demo()
        sys.stdout.write("\n\n")
        sys.exit(-1)

if __name__ == "__main__":
     main(sys.argv[1:])
