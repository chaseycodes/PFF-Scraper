

import os
import csv
import time
import requests
import pandas as pd

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
        self.years      = list(range(2006,2019))
        self.categories = ['/returns.htm','/passing.htm','/receiving.htm','/rushing.htm','/kicking.htm','/opp.htm']
    
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
                                uri = stat.find('a')['href']
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
        self.player_id  = player_id
        self.url        = url
        self.scraper    = scraper
        self.profile    = {
            'player_id': player_id,
            'name': None,
            'position': None,
            'height': None,
            'weight': None,
            'current_team': None,
            'birth_date': None,
            'birth_state': None,
            'college': None,
            'death_date': None,
            'high_school': None,
            'draft_team': None,
            'draft_round': None,
            'draft_position': None,
            'draft_year': None,
            'hof_year': None
        }
    
    def scrape_profile(self): #fill self.profile
        res = self.scraper.get_player_html(self.url) #extract html from Scraper class in line 75
        #profile information
        profile_info  = res.find('div', {'itemtype': 'https://schema.org/Person'})
        profile_rows  = profile_info.find_all('p')
        index_counter = 1 #profile_rows index counter

        #find name attribute
        self.profile['name'] = profile_info.find('h1').get_text().encode('utf-8')

        #find position attribute
        if profile_rows[index_counter].contents == [u'\n']:
            index_counter += 2 #if no position skip 2 rows
        else:
            try:
                self.profile['position'] = profile_rows[index_counter].contents[2].split('\n')[0].split(' ')[1]
                index_counter += 1
            except:
                pass

        #find height and weight attributes
        height = profile_rows[index_counter].find('span', {'itemprop': 'height'})
        if height is not None:
            self.profile['height'] = height.contents[0].encode('utf-8')
        weight = profile_rows[index_counter].find('span', {'itemprop': 'weight'})
        if weight is not None:
            self.profile['weight'] = weight.contents[0].replace('lb','').encode('utf-8')
        if height is not None or weight is not None:
            index_counter += 1

        #find current team attribute
        affiliation = profile_rows[index_counter].find('span', {'itemprop': 'affiliation'})
        if affiliation is not None:
            self.profile['current_team'] = profile_rows[index_counter].contents[2].get_text()
            index_counter += 1
        
        #find birth date and state attributes
        birth_info = profile_rows[index_counter].find('span', {'itemprop': 'birthDate'})
        if birth_info is not None:
            self.profile['birth_date'] = birth_info['data-birth'].encode('utf-8')
        try:
            birth_place = profile_rows[index_counter].find('span', {'itemprop': 'birthPlace'})
            if birth_place is not None:
                self.profile['birth_state'] = birth_place.contents[1].get_text().encode('utf-8')
        except IndexError:
            pass
        if birth_info is not None or len(birth_place) > 0:
            index_counter += 1
        
        #find death_date attribute if present
        death_section = profile_rows[index_counter].find('span', {'itemprop': 'deathDate'})
        if death_section is not None:
            self.profile['death_date'] = death_section['data-death'].encode('utf-8')
            index_counter += 1
        
        #find college attribute
        if profile_rows[index_counter].contents[0].get_text() == 'College':
            self.profile['college'] = profile_rows[index_counter].contents[2].contents[0].encode('utf-8')
            index_counter += 2 #skip AAV
        
        #find high school name attribute
        try:
            if profile_rows[index_counter].contents[0].get_text() == 'High School':
                self.profile['high_school'] = profile_rows[index_counter].contents[2].contents[0].encode('utf-8') + ', ' + profile_rows[index_counter].contents[4].contents[0].replace('"','').encode('utf-8')
                index_counter += 1
        except IndexError:
            pass
        
        #find draft attributes if present
        try:
            if profile_rows[index_counter].contents[0].get_text() == 'Draft':
                self.profile['draft_team']     = profile_rows[index_counter].contents[2].get_text().encode('utf-8')
                self.profile['draft_year']     = profile_rows[index_counter].contents[4].get_text().split(' ')[0].encode('utf-8')
                self.profile['draft_round']    = profile_rows[index_counter].contents[3].split(' ')[3].encode('utf-8')
                self.profile['draft_position'] = profile_rows[index_counter].contents[3].split(' ')[5].replace('(','').encode('utf-8')
                index_counter += 1
        except IndexError:
            pass
        
        #find HOF credits if present
        try:
            if profile_rows[index_counter].contents[0].contents[0] == 'Hall of Fame':
                self.profile['hof_year'] = profile_rows[index_counter].contents[2].contents[0].encode('utf-8')
        except IndexError:
            pass

        self.create_player_profile(self.profile)

    def create_player_profile(self,obj):
        headers = obj.keys()
        with open('./csv/players/NFL-Player-Profiles(06-18).csv','a') as f:
            dict_writer = csv.DictWriter(f, headers)
            dict_writer.writerow(obj)

    def image_link(self):
        pass

class CSV():

    def __init__(self,scraper):
        self.scraper     = scraper
        self.player_path = './csv/players/NFL-Player-Profiles(06-18).csv'
    
    def load(self,attribute):
        if attribute == 'player':
            df = pd.read_csv(self.player_path)
            return df

if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_sites()