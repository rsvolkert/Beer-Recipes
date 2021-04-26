from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

def open_url(path, pg_num):
    url = path + str(pg_num)
    req = Request(url, headers={'User-Agent' : 'Mozilla/5.0'})
    page = urlopen(req)
    html = page.read().decode('utf-8')
    return BeautifulSoup(html, 'html.parser')

def get_recipe(href):
    recipe_url = recipe_base + href
    recipe_req = Request(recipe_url, headers={'User-Agent' : 'Mozilla/5.0'})
    recipe_page = urlopen(recipe_req)
    recipe_html = recipe_page.read().decode('utf-8')
    recipe_soup = BeautifulSoup(recipe_html, 'html.parser')
    
    beer = recipe_soup.title.text.split('|')[0].strip()
    
    stats = {'Name' : beer,
             'ID' : int(re.search('view/(.+?)/', href).group(1))}
    
    for stat in recipe_soup.find_all('span', {'class':'viewStats'}):
        name = stat.find('span').text.strip(':')
            
        if name == 'Rating':
            stats['Rating'] = float(stat.find('span', {'itemprop':'ratingValue'}).text)
            stats['Reviews'] = int(stat.find('span', {'itemprop':'reviewCount'}).text)
        else:
            if stat.find('strong'):
                entry = stat.find('strong').text
                stats[name] = entry.strip()
                        
    for brewpart in recipe_soup.find_all('div', {'class':'brewpart'}):
        part_id = brewpart.get('id')
            
        if part_id in brewpart_ids:
            if part_id == 'yeasts':
                stats['yeasts'] = brewpart.find('th').text.strip()
            else:
                if brewpart.tfoot:
                    brewpart.tfoot.extract()
                        
                df = pd.read_html(str(brewpart))[0]
                df.rename({u'\N{DEGREE SIGN}L'.upper() : 'L'}, inplace=True, axis=1)
                df_dict = df.transpose().to_dict()
                    
                stats[part_id] = df_dict
        elif part_id == None:
            if brewpart.find('div', {'class':'ui message'}):
                stats['notes'] = brewpart.find('div', {'class':'ui message'}).text.strip()
    
    return stats
    

base = 'https://www.brewersfriend.com/homebrew-recipes/page/'
recipe_base = 'https://www.brewersfriend.com'

soup = open_url(base, 1)

ul = soup.find_all('ul', {'class':'pagination'})
page_text = ul[1].find_all('li')[0].text.strip()
page_num = int(page_text.split()[-1].replace(',',''))

brewpart_ids = ['fermentables', 'hops', 'others', 'yeasts', 'mashsteps']

recipes = []

for pg_idx in range(2608, page_num+1):
    soup = open_url(base, pg_idx)
    
    hrefs = [recipe.get('href') for recipe in soup.find_all('a', {'class':'recipetitle'})]
    
    for recipe in hrefs:
        recipes.append(get_recipe(recipe))
                
with open('Data/recipes.json') as out:
    json.dumps(recipes, out)