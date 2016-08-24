#!/usr/bin/env python
import pprint
from configlib import getConfig, OptionParser
import json
import requests
import netaddr
import sys

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

    def sendRequest(self, reqtype):
        headers = {'Authorization': self.config.apikey}
        url = ''
        self.rawdata = dict()
        if netaddr.valid_ipv4(self.intel):
            url = "https://" + self.config.apiurl + "/ips/" + self.intel + "/" + reqtype
        else:
            url = "https://" + self.config.apiurl + "/domains/" + self.intel + "/" + reqtype
        if len(reqtype) and len(url) > 1:
            try:
                request = requests.get(url=url, headers=headers, timeout=0.5)
            except (
                    requests.exceptions.ConnectionError, requests.exceptions.TooManyRedirects,
                    requests.exceptions.Timeout) as e:
                sys.stderr.write('Failed to fetch IQRisk data: {0}\n'.format(e))
            if 'request' in locals() and hasattr(request, 'json'):
                if request.status_code == 200:
                    try:
                        self.rawdata = request.json()
                    except (ValueError) as e:
                        sys.stderr.write('Failed to decode IQRisk data: {0}\n'.format(e))

    def get_reputation(self, type, objtype):
        self.reputation[type] = dict()
        if objtype == 'ip':
            if type in self.config.allowedipreptypes:
                self.sendRequest(type)
        if objtype == 'domain':
            self.sendRequest(type)
        if 'response' in self.rawdata:
            if self.rawdata['response'] and self.rawdata['success']:
                self.reputation[type] = self.rawdata['response']

