
import csv
import requests

from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, ChunkedEncodingError

class Scraper():

    def __init__(self):
        self.url        = 'https://www.pro-football-reference.com/years/'
        self.years      = list(range(8,19))
        self.categories = ['/passing.htm','/recieving.htm','/rushing.htm','/opp.htm']
    
    def scrape_sites(self):
        for year in self.years:
            for cat in self.categories:
                url  = self.url+str(year)+cat
                res  = request.get(url)
                html = BeautifulSoup(res.content, ‘html.parser’)
                if html:
                    div = html.find(“div”, class_=”col-xs-6 col-md-6 zero”)