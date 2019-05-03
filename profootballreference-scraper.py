

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
        p_id = 0 #player_id counter
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
                                uri = stat.find('a')['href'] #TODO ADD PLAYER SCRAPER make counter and checker
                                if uri not in href: #check for dupes
                                    href.append(uri)
                                    player = Player(p_id,self.url+uri,self) #create player class
                                    try:
                                        player.scrape_profile()
                                        p_id += 1
                                    except ConnectionError: #TODO log errors
                                        print('Error: {}'.format(stat.get_text().strip().replace('*','')))
                                data[stat['data-stat']] = stat.get_text().strip().replace('*','')
                            else:
                                data[stat['data-stat']] = stat.get_text().strip()
                        if len(data) == 1: #clean empty data from list
                            pass
                        else:
                            data_list.append(data) #add {year} into data_list on line 26
            obj[key.capitalize()] = data_list #add every year as one key to obj on line 23
        self.list_to_csv(obj)

    def list_to_csv(self,obj): #utilize in scrape_sites() on line 48 
        for cat in self.categories: 
            key     = cat.replace('/','').replace('.htm','').capitalize()
            to_csv  = obj[key] #list object
            headers = to_csv[0].keys()
            with open('./csv/statistics/NFL-Statistics-{}(06-18).csv'.format(key),'w') as f:
                dict_writer = csv.DictWriter(f, headers)
                dict_writer.writeheader()
                dict_writer.writerows(to_csv)
    
    def get_player_html(self,url):
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
        2) URL: Player link. 
        3) Scraper: Inherited Class
        4) Profile: Data object containing player information
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
            'hof_induction_year': None
        }
    
    def scrape_profile(self): #fill self.profile
        res = self.scraper.get_player_html(self.url) #extract html from Scraper class in line 75
        #profile information
        profile_information = res.find('div', {'itemtype': 'https://schema.org/Person'})
        self.profile['name'] = profile_information.find('h1').get_text()
        print(self.profile['name'])
        print(self.url)
        profile_rows = profile_information.find_all('p')
        position_row = profile_rows[1].get_text().replace('\n','').replace('\t','').replace('Throws','').replace(' ','').split(':')[1]
        size_row     = profile_rows[2]
        team_row     = profile_rows[3]
        born_row     = profile_rows[4]
        college_row  = profile_rows[5]
        hs_row       = profile_rows[7]
        try:
            draft_row    = profile_rows[8]
        except:
            pass
        print(position_row)


    def image_link():
        pass
        

if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_sites()