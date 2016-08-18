#!/usr/bin/env python
import pprint
from configlib import getConfig, OptionParser
import json
from urllib2 import Request, urlopen
import netaddr

intel = ''

class iqr():

    def __init__(self, intel):
        self.reputation = {}
        self.intel = intel
        self.config_file = './iqr.conf'
        self.config = None
        myparser = OptionParser()
        (self.config, args) = myparser.parse_args([])
        self.config.apiurl = getConfig('apiurl', '', self.config_file)
        self.config.apikey = getConfig('apikey', '', self.config_file)
        self.config.allowedipreptypes = getConfig('allowedipreptypes', '', self.config_file)
        self.config.alloweddomainreptypes = getConfig('alloweddomainreptypes', '', self.config_file)

    def prepareRequest(self, reqtype):
        if netaddr.valid_ipv4(self.intel):
            self.request = Request("https://"+self.config.apiurl+"/ips/"+self.intel+"/"+reqtype)
        else:
            # FIXME - could use a check for a domain
            self.request = Request("https://"+self.config.apiurl+"/domains/"+self.intel+"/"+reqtype)
        self.request.add_header("Authorization", self.config.apikey)

    def sendRequest(self):
        try:
            self.result = urlopen(self.request)
        except (URLError, HTTPError) as e:
            sys.stderr.write('Error when sending HTTP request: '.format(e))
        try:
            self.rawdata = json.load(self.result)
        except ValueError as e:
            sys.stderr.write('Error when parsing reveived JSON data: '.format(e))

    def ip_reputation(self, type):
        if type in self.config.allowedipreptypes:
            self.prepareRequest(type)
            self.sendRequest()
            if self.rawdata['response']:
                self.reputation[type] = self.rawdata['response']

    def domain_reputation(self, type):
        if type in self.config.alloweddomainreptypes:
            self.prepareRequest(type)
            self.sendRequest()
            if self.rawdata['response']:
                self.reputation[type] = self.rawdata['response']
