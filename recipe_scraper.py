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

base = 'https://www.brewersfriend.com/homebrew-recipes/page/'

soup = open_url(base, 1)

ul = soup.find_all('ul', {'class':'pagination'})
page_text = ul[1].find_all('li')[0].text.strip()
page_num = int(page_text.split()[-1].replace(',',''))

brewpart_ids = ['fermentables', 'hops', 'others', 'yeasts', 'mashsteps']

recipes = []

for pg_idx in range(1, page_num+1):
    recipe_base = 'https://www.brewersfriend.com'
    soup = open_url(base, pg_idx)
    
    for recipe in soup.find_all('a', {'class':'recipetitle'}):
        href = recipe.get('href')
        beer = recipe.text
        
        recipe_url = recipe_base + href
        recipe_req = Request(recipe_url, headers={'User-Agent' : 'Mozilla/5.0'})
        recipe_page = urlopen(recipe_req)
        recipe_html = recipe_page.read().decode('utf-8')
        recipe_soup = BeautifulSoup(recipe_html, 'html.parser')
        
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
                    
                    if re.search('\d\s[a-zA-Z]', entry):
                        stat = float(entry.split()[0])
                        units = entry.split()[1]
                        
                        stats[name + ' ' + '(' + units + ')'] = stat
                    elif re.search('%', entry):
                        stats[name] = float(entry.strip().strip('%')) / 100
                    else:
                        try:
                            stats[name] = float(entry.strip())
                        except ValueError:
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
        
        recipes.append(stats)
        
with open('Data/recipes.json') as out:
    json.dumps(recipes, out)