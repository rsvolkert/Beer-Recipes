from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

url = 'https://www.beeradvocate.com/beer/top-rated/'
req = Request(url, headers={'User-Agent' : 'Mozilla/5.0'})
page = urlopen(req)
html = page.read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')
beer_urls = soup.find_all(href=re.compile('/beer/profile/[0-9]+/[0-9]+'))

base_url = 'https://www.beeradvocate.com'
beer_df = pd.DataFrame(columns = ['Name', 'Type', 'ABV', 'Score', 'Avg_Rating', 'Reviews', 'Ratings', 'Brewery', 'Location', 'Availability'],
                       index = range(len(beer_urls)))
idx = 0
for link in beer_urls:
    work_url = base_url + link.get('href')
    work_req = Request(work_url, headers={'User-Agent' : 'Mozilla/5.0'})
    work_page = urlopen(work_req)
    work_html = work_page.read().decode('utf-8')
    work_soup = BeautifulSoup(work_html, 'html.parser')
    
    stats = []
    title = work_soup.title.text.split('|')
    stats.append(title[0].strip())
    
    for stat in work_soup.find_all('dd', {'class' : 'beerstats'})[0:9]:
        contents = stat.contents
        
        if contents[0] == ' ':
            if len(contents) > 1:
                stats.append(contents[1].text)
            else:
                stats.append('')
        else:
            stats.append(contents[0].text)
            
    beer_df.loc[idx] = stats
    idx = idx + 1

def strtopct(abv):
    if abv == 'not listed':
        return np.nan
    else:
        return float(abv.strip('%')) / 100

def commasep(num):
    return int(num.replace(',',''))

beer_df.ABV = beer_df.ABV.apply(lambda x : strtopct(x))
beer_df.Score = pd.to_numeric(beer_df.Score)
beer_df.Avg_Rating = pd.to_numeric(beer_df.Avg_Rating)
beer_df.Reviews = beer_df.Reviews.apply(lambda x : commasep(x))
beer_df.Ratings = beer_df.Ratings.apply(lambda x : commasep(x))

if __name__ == '__main__':
    beer_df.to_csv('Data/Ratings.csv', index=False)