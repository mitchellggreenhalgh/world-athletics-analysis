import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import re

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from os import makedirs
from tqdm.auto import tqdm
from glob import glob

sns.set_theme(style='whitegrid')

class WorldAthleticsScraper:
    '''A module to scrape the data tables on the World Athletics All Time and Season Bests lists.'''

    def __init__(self, event: str | None = None) -> None:
        '''Initialize a WorldAthleticsScraper Object.
        
        Args:
          -  event (`str` | `None`): The running event of interest. Choose one from the following list or specify the event in a data download method:
          
            * '60m'
            * '100m'
            * '200m'
            * '400m'
            * '800m'
            * '1500m'
            * 'mile'
            * '3000m'
            * '2mile'
            * '5000m'
            * '10000m'
            * 'half_marathon'
            * 'marathon'
        '''

        self.event = event
        self.data_dir = self.make_data_dir()

        self.all_time_html_dicts = {
            '60m': {
                'men': f'https://worldathletics.org/records/all-time-toplists/sprints/60-metres/all/men/senior?regionType=world&timing=electronic&windReading=regular&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229683&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/sprints/60-metres/all/women/senior?regionType=world&timing=electronic&windReading=regular&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229684&ageCategory=senior'
            },
            '100m': {
                'men': f'https://worldathletics.org/records/all-time-toplists/sprints/100-metres/all/men/senior?regionType=world&timing=electronic&windReading=regular&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229630&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/sprints/100-metres/all/women/senior?regionType=world&timing=electronic&windReading=regular&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229509&ageCategory=senior'
            },
            '200m': {
                'men': f'https://worldathletics.org/records/all-time-toplists/sprints/200-metres/all/men/senior?regionType=world&timing=electronic&windReading=regular&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229605&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/sprints/200-metres/all/women/senior?regionType=world&timing=electronic&windReading=regular&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229510&ageCategory=senior'
            },
            '400m': {
                'men': f'https://worldathletics.org/records/all-time-toplists/sprints/400-metres/all/men/senior?regionType=world&timing=electronic&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229631&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/sprints/400-metres/all/women/senior?regionType=world&timing=electronic&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229511&ageCategory=senior'
            },
            '800m': {
                'men': f'https://worldathletics.org/records/all-time-toplists/middlelong/800-metres/all/men/senior?regionType=world&timing=electronic&page=1&bestResultsOnly=false&firstDay=1899-12-31&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229501&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/middlelong/800-metres/all/women/senior?regionType=world&timing=electronic&page=1&bestResultsOnly=false&firstDay=1899-12-31&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229512&ageCategory=senior'
            },
            '1500m': {
                'men': f'https://worldathletics.org/records/all-time-toplists/middlelong/1500-metres/all/men/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229502&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/middlelong/1500-metres/all/women/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229513&ageCategory=senior'
            },
            'mile': {
                'men': f'https://worldathletics.org/records/all-time-toplists/middlelong/one-mile/all/men/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229503&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/middlelong/one-mile/all/women/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229517&ageCategory=senior'
            },
            '3000m': {
                'men': f'https://worldathletics.org/records/all-time-toplists/middlelong/3000-metres/all/men/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229607&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/middlelong/3000-metres/all/women/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229519&ageCategory=senior'
            },
            '2mile': {
                'men': f'https://worldathletics.org/records/all-time-toplists/middlelong/two-miles/all/men/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229608&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/middlelong/two-miles/all/women/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229520&ageCategory=senior'
            },
            '5000m': {
                'men': f'https://worldathletics.org/records/all-time-toplists/middlelong/5000-metres/all/men/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229609&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/middlelong/5000-metres/all/women/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229514&ageCategory=senior'
            },
            '10000m': {
                'men': f'https://worldathletics.org/records/all-time-toplists/middlelong/10000-metres/all/men/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229610&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/middlelong/10000-metres/all/women/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229521&ageCategory=senior'
            },
            'half_marathon': {
                'men': f'https://worldathletics.org/records/all-time-toplists/road-running/half-marathon/all/men/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229633&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/road-running/half-marathon/all/women/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229541&ageCategory=senior'
            },
            'marathon': {
                'men': f'https://worldathletics.org/records/all-time-toplists/road-running/marathon/all/men/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229634&ageCategory=senior',
                'women': f'https://worldathletics.org/records/all-time-toplists/road-running/marathon/all/women/senior?regionType=world&page=1&bestResultsOnly=false&firstDay=1899-12-30&lastDay={datetime.today() - timedelta(days=1):%Y-%m-%d}&maxResultsByCountry=all&eventId=10229534&ageCategory=senior'
            }
        }
        self.valid_events = ['60m', '100m', '200m', '400m', 
                             '800m', '1500m', 'mile', '3000m', '2mile',
                             '5000m', '10000m', 'half_marathon', 'marathon']
        
        if self.event not in self.valid_events and self.event is not None:
            raise ValueError('Please choose a valid running event that is offered in this module.')


    def make_data_dir(self) -> None:
        '''Set up a data directory in the overall directory with the format: 'data/[yyyy_mm]', where the year and numeric month match the date of the download event.'''
        makedirs(f'data/{datetime.today():%Y_%m}', exist_ok=True)
        return f'data/{datetime.today():%Y_%m}'


    def download_season_bests_800m(self, sex: str, export: bool = False) -> pd.DataFrame:
        '''Download and Concatenate all Seasons Bests for a season, then concatenates all the seasons' season best performances across all years into a single `pd.DataFrame`.
        
        Args:
        -  sex (`str`): 'men' or 'women'
        -  export (`bool`): whether or not to export the download as a .csv file

        Returns:
        - dfs (`pd.DataFrame`): a DataFrame containing all of the Season Bests for All Years in the World Athletics Database
        '''
        
        match sex:
            case 'men':
                html_path = 'https://worldathletics.org/records/toplists/middlelong/800-metres/all/men/senior/2001?regionType=world&timing=electronic&page=1&bestResultsOnly=false&maxResultsByCountry=all&eventId=10229501&ageCategory=senior'

            case 'women':
                html_path = 'https://worldathletics.org/records/toplists/middlelong/800-metres/all/women/senior/2001?regionType=world&timing=electronic&page=1&bestResultsOnly=false&maxResultsByCountry=all&eventId=10229512&ageCategory=senior'

        num_pages = self.find_last_page_num(html_path)

        dfs = None
        for i in np.arange(2001, 2025):
            new_path_1 = html_path.replace('2001', f'{i}')
            num_pages = self.find_last_page_num(new_path_1)

            for j in np.arange(1, num_pages + 1):
                new_path_2 = new_path_1.replace('page=1', f'page={j}')
                df = pd.read_html(new_path_2)[0]        

                if dfs is None:
                    dfs = df
                    continue

                dfs = pd.concat([dfs, df])

        dfs = dfs.reset_index(drop=True)

        if export:
            dfs.to_csv(f'data/season_bests_{sex}_800m.csv', index=False)

        return dfs
        

    def find_last_page_num(self, html_path: str) -> int:
        '''Uses `requests`, `re`, and `bs4`'s `BeautifulSoup` to find the maximum page number of a given dataset.
        
        Args:
        -  html_path (`str`): the html path of the first page of the dataset
        
        Returns:
        -  last_page_num (`int`): the page number of the last page of data'''
        
        page = requests.get(html_path)
        soup = BeautifulSoup(page.text, 'html.parser')
        last_page_num = int(soup.find_all('a', attrs={'data-page': re.compile('[0-9]+')})[-1]['data-page'])

        return last_page_num


    def download_all_time_data(self, sex: str, event: str | None = None, export: bool = False) -> pd.DataFrame:
        '''Downloads all the pages of the world athletics all-time, all-performances (more than one entry per athlete is possible) list for an event and exports them as a single DataFrame.
        
        Args:
        -  sex (`str`): 'men' or 'women'
        -  event (`str`): choose one from the following list. The default is the event specified in the initializer.

                * '60m'
                * '100m'
                * '200m'
                * '400m'
                * '800m'
                * '1500m'
                * 'mile'
                * '3000m'
                * '2mile'
                * '5000m'
                * '10000m'
                * 'half_marathon'
                * 'marathon'

        -  export (`bool`): If `True`, export the data to a .csv file in the data directory. Default is `False`.
        
        Returns:
        -  dfs (`pd.DataFrame`): a single table of all the concatenated pages of the World Athletics Database'''

        if event is None:
            event = self.event

        dfs = None
        html_path = self.all_time_html_dicts[event][sex]
        num_pages = self.find_last_page_num(html_path=html_path)

        for i in np.arange(1, num_pages + 1):
            df = pd.read_html(html_path.replace('page=1', f'page={i}'))[0]        

            if dfs is None:
                dfs = df
                continue

            dfs = pd.concat([dfs, df])

        dfs = dfs.reset_index(drop=True)

        match event:
            case '60m' | '100m' | '200m' | '400m':
                dfs['Mark_Seconds'] = dfs['Mark']
            case 'half_marathon' | 'marathon':
                dfs['Mark_Seconds'] = dfs['Mark'].apply(self.convert_marathons)
            case _:
                dfs['Mark_Seconds'] = dfs['Mark'].apply(lambda row: float(row.split(':')[0]) * 60 + float(row.split(':')[1].replace('h', '')))

        if export:
            dfs.to_csv(f'{self.data_dir}/all_time_{sex}_{event}.csv', index=False)

        return dfs
    

    def convert_marathons(self, row: str) -> float:
        '''Takes a cell of a half-marathon or marathon time from a `pd.DataFrame` and converts it to seconds.'''
        if len(row.split(':')) == 3:
            return float(row.split(':')[0]) * 3600 + float(row.split(':')[1]) * 60 + float(row.split(':')[2])
        
        return float(row.split(':')[0]) * 60 + float(row.split(':')[1])
    

    def download_all_time_data_all_events(self) -> None:
        '''Download all all-time, all-performances datasets for all the events covered by this module.'''
        for event in tqdm(self.valid_events):
            for sex in ('men', 'women'):
                self.download_all_time_data(sex=sex, event=event, export='True')
        
        return None
    

    def compile_all_time_tables(self) -> None:
        '''Compile all all-time datasets in the data directory into two files: one for all men's records, and one for all women's records'''
        
        # Men's Table
        file_list_men = glob('all_time_men*.csv', root_dir=self.data_dir)
        dfs = None

        for file in file_list_men:
            df = pd.read_csv(f'{self.data_dir}/{file}')
            
            if dfs is None:
                dfs = df.assign(event=file.split('_')[-1].split('.')[0])
                continue

            dfs = pd.concat([dfs, df.assign(event=file.split('_')[-1].split('.')[0])])

        dfs.to_csv(f'{self.data_dir}/all_time_men_all_events.csv', index=False)

        # Women's Table
        file_list_women = glob('all_time_women*.csv', root_dir=self.data_dir)
        dfs = None

        for file in file_list_women:
            df = pd.read_csv(f'{self.data_dir}/{file}')
            
            if dfs is None:
                dfs = df.assign(event=file.split('_')[-1].split('.')[0])
                continue

            dfs = pd.concat([dfs, df.assign(event=file.split('_')[-1].split('.')[0])])

        dfs.to_csv(f'{self.data_dir}/all_time_women_all_events.csv', index=False)

        return None