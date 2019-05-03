

import os
import csv
import time
import requests

from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, ChunkedEncodingError

PATH = '/Users/ahn.ch/Projects/Fantasy-Football-Analysis'

class Scraper():

    def __init__(self):
        """
        Args:
        1) URL: Base url for concatenation.
        2) Years: Starts at 2006 - when PFR first starting tracking QBR.
        3) Categories: Fantasy football relevant only. No individual defensive stats. 
        """
        self.url        = 'https://www.pro-football-reference.com'
        self.years      = list(range(2017,2019))
        self.categories = ['/passing.htm','/receiving.htm','/rushing.htm','/kicking.htm','/opp.htm','/returns.htm']
    
    def scrape_sites(self):
        obj  = {} #final object for list_to_csv
        href = [] #list container for scrape_player_profiles
        for cat in self.categories: #iterate through instances
            data_list = [] #list container for total years per category
            key  = cat.replace('/','').replace('.htm','') #clean key
            for year in self.years:
                print(str(year)+': '+key)
                url  = self.url+'/years/'+str(year)+cat
                res  = requests.get(url)
                html = BeautifulSoup(res.content, 'html.parser')
                if html:
                    div   = html.find('div', {'id': 'content'})
                    table = div.find('tbody') #search for table container
                    rows  = table.find_all('tr')
                    for row in rows:
                        data = {'year': year}
                        for stat in row.find_all('td'):
                            if stat['data-stat'] == 'player': #look for href
                                href = stat.find('a')['href'] #TODO ADD PLAYER SCRAPER make counter and checker
                                data[stat['data-stat']] = stat.get_text().strip().replace('*','')
                            else:
                                data[stat['data-stat']] = stat.get_text().strip()
                        if len(data) == 1: #clean empty data from list
                            pass
                        else:
                            data_list.append(data) #add {year} into data_list on line 26
            obj[key] = data_list #add every year as one key to obj on line 23
        self.list_to_csv(obj)

    def list_to_csv(self,obj): #utilize in scrape_sites() on line 48 
        for cat in self.categories: 
            key     = cat.replace('/','').replace('.htm','')
            to_csv  = obj[key] #list object
            headers = to_csv[0].keys()
            with open('./csv/statistics/{}.csv'.format(key),'w') as f:
                dict_writer = csv.DictWriter(f, headers)
                dict_writer.writeheader()
                dict_writer.writerows(to_csv)
    
    def get_player_page_html(self,href)
        url  = self.url+href
        res  = requests.get(url)
        html = BeautifulSoup(res.content, 'html.parser')
        if html:
            return html
        else:
            return None 

class Player():

    def __init__(self,player_id,url,scraper):
        """
        Args:
        1) ID: Unique Identifier.
        2) Href: Player link. 
        """
        self.url        = url
        self.scraper    = scraper
        self.player_id  = player_id
        self.profile = {
            'player_id': player_id,
            'name': None,
            'position': None,
            'height': None,
            'weight': None,
            'current_team': None,
            'birth_date': None,
            'birth_place': None,
            'death_date': None,
            'college': None,
            'high_school': None,
            'draft_team': None,
            'draft_round': None,
            'draft_position': None,
            'draft_year': None,
            'current_salary': None,
            'hof_induction_year': None
        }
    
    def scrape_profile():
        pass

if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_sites()