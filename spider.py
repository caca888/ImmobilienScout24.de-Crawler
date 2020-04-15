import configparser
from pandas import DataFrame
import requests
from bs4 import BeautifulSoup
import re
import datetime
import sys
import os
from functions import *

class Spider:
    def __init__(self, config_file):
        self.config_file = config_file
        self.immoscout_data = DataFrame()
        self.config()
        self.boot()

    def config(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        defaultConfig = config['DEFAULT']
        self.projectname = defaultConfig['PROJECT_NAME']
        self.domain = defaultConfig['DOMAIN']
        self.urllocation = defaultConfig['URL_LOCATION']
        self.urltype = defaultConfig['URL_TYPE']
        self.urlpayment = defaultConfig['URL_PAYMENT']
        self.parsermethod = defaultConfig['PARSER_METHOD']
        self.maxcounttag = defaultConfig['MAX_COUNT_TAG']
        self.rawdatatag = defaultConfig['RAW_DATA_TAG']
        self.rawdatacssselector = defaultConfig['RAW_DATA_TAG_CSS_SELECTOR']
        self.addcssselector = defaultConfig['LOCATION_CSS_SELECTOR']
        self.maxcount = int(defaultConfig['MAX_COUNT_LIMIT'])
        

    def boot(self):
        create_project_dir('/output/' + self.projectname)
        base_url = self.domain+self.urllocation+self.urltype+self.urlpayment
        max_pages = self.get_max(base_url)
        link_count = 1
        link_list_full = []
        for i in range(1, max_pages):
            link_list_full.append(base_url+"?pagenumber="+str(i))
        for link in link_list_full:
            print("Crawling: "+link+" (link #"+str(link_count)+" of "+max_pages+")")#print progress
            link_count += 1#add to progress indicator
            self.get_data(link)

        


    def get_max(self, url):
        try:
            url = requests.get(url)
        except Exception:
            print("Fehler beim Oeffnen der Website")
        try:
            site_extract = BeautifulSoup(url.text, self.parsermethod)
        except Exception:
            print("Fehler beim Einlesen in BeautifulSoup")
        try:
            max_link = max([int(n["value"]) for n in site_extract.find_all(self.maxcounttag)])#get the maximum value for links in a specific sub-site
        except Exception:
            print("Fehler beim Loop")
        else:
            if max_link > self.maxcount:
                return self.maxcount
            else: 
                return max_link

    def get_data(self, url):
        try:
            url_raw = url#save url as string for real estate type
            url = requests.get(url)
        except Exception:
            return None
        except Exception:
            return None
        try:
            site_extract = BeautifulSoup(url.text, self.parsermethod)
            rawdata_extract = site_extract.find_all(self.rawdatatag, {"class":self.rawdatacssselector})#extract every result box
        except AttributeError as e:
            return None

        price = []
        size = []
        location = []
        ownership = []
        immo_type = []
        for i in range(0,len(rawdata_extract)):
            try:
                price.append(rawdata_extract[i].find_all("dd")[0].get_text().strip())#extract price
            except Exception:
                price.append(-1)
            try:
                size.append(rawdata_extract[i].find_all("dd")[1].get_text().strip())#extract size
            except Exception:
                size.append(0)
            try:
                location.append(rawdata_extract[i].find_all(self.rawdatatag, {"class":self.addcssselector})[0].get_text().strip())#extract location
            except Exception:
                location.append("#")
                
            if "/wohnung" in self.urltype:
                immo_type.append("Wohnung")
            elif "/haus" in self.urltype:
                immo_type.append("Haus")
            if "-mieten" in self.urlpayment:
                ownership.append("Miete")
            elif "-kaufen" in self.urlpayment:
                ownership.append("Kauf")
        self.immoscout_data = self.immoscout_data.append(DataFrame({"price":price, 
                                                    "size":size,
                                                    "location":location, 
                                                    "real_estate":immo_type, 
                                                    "ownership":ownership}), 
        ignore_index=True)