import pandas as pd
import re

def generate_ingredients(recipe):
    ingredients = 'INGREDIENTS'
    
    def add_fermentables(fermentables):
        ferment_str = '\n\n\tFERMENTABLES'
        
        for key in fermentables:
            ingred = fermentables[key]
            ferment_str = ferment_str + '\n\t\t' + ingred['Amount'] + ' ' + ingred['Fermentable']
            
        return ferment_str
    
    def add_hops(hops):
        if hops == None:
            return ''
        
        hops_str = '\n\n\tHOPS'
        
        for key in hops:
            ingred = hops[key]
            hops_str = hops_str + '\n\t\t' + str(ingred['Amount']) + ' ' + str(ingred['Variety']) + ', ' + ingred['Type'] + ', ' + ingred['Use'] + ', ' + str(ingred['Time'])
            
        return hops_str
    
    def add_others(others):
        if others == None:
            return ''
        
        others_str = '\n\n\tOTHER'
        
        for key in others:
            ingred = others[key]
            others_str = others_str + '\n\t\t' + ingred['Amount'] + ' ' + str(ingred['Name']) + ', ' + ingred['Type'] + ', ' + ingred['Use'] + ', ' + ingred['Time']
            
        return others_str
    
    def add_yeast(yeast):
        if yeast == None:
            return ''
        
        return '\n\n\tYEAST\n\t\t' + yeast
    
    ingredients = ingredients + add_fermentables(recipe['fermentables']) + add_hops(recipe['hops']) + add_others(recipe['others']) + add_yeast(recipe['yeasts'])
    return ingredients

def generate_recipe(recipe):
    
    def schedule(recipe):
        hops = recipe['hops']
        others = recipe['others']
        schedule = {}
        
        for key in hops:
            hop = hops[key]
            
            time = hop['Time'].strip('.').split()
            
            if len(time) > 1:
                if time[0].lower() == 'day':
                    time_in_min = 21 - int(time[1])
                    unit = 'days'
                elif re.search('hr', time[1]):
                    try:
                        time_in_min = int(time[0]) * 60
                    except ValueError:
                        time_in_min = float(time[0]) * 60
                    unit = 'minutes'
                else:
                    try:
                        time_in_min = int(time[0])
                    except ValueError:
                        time_in_min = float(time[0])
                    unit = time[1]
            
            if hop['Use'] in schedule:
                if time_in_min in schedule[hop['Use']]:
                    schedule[hop['Use']][time_in_min]['Amount'].append(hop['Amount'])
                    schedule[hop['Use']][time_in_min]['Name'].append(str(hop['Variety']) + ' hops')
                else:
                    schedule[hop['Use']][time_in_min] = {'Amount' : [hop['Amount']],
                                                         'Name' : [str(hop['Variety']) + ' hops'],
                                                         'Unit' : unit}
            else:
                schedule[hop['Use']] = {time_in_min : {'Amount' : [hop['Amount']],
                                                       'Name' : [str(hop['Variety']) + ' hops'],
                                                       'Unit' : unit}}
        if others is not None:
            for key in others:
                other = others[key]
                
                time = other['Time'].strip('.').split()
                
                if len(time) > 1:
                    if time[0].lower() == 'day':
                        time_in_min = 21 - int(time[0])
                        unit = 'days'
                    elif re.search('hr', time[1]):
                        try:
                            time_in_min = int(time[0]) * 60
                        except ValueError:
                            time_in_min = float(time[0]) * 60
                        unit = 'minutes'
                    else:
                        try:
                            time_in_min = int(time[0])
                        except ValueError:
                            time_in_min = float(time[0])
                        unit = time[1]
                
                if other['Use'] in schedule:
                    if time_in_min in schedule[other['Use']]:
                        schedule[other['Use']][time_in_min]['Amount'].append(other['Amount'])
                        schedule[other['Use']][time_in_min]['Name'].append(other['Name'])
                    else:
                        schedule[other['Use']][time_in_min] = {'Amount' : [other['Amount']],
                                                               'Name' : [other['Name']],
                                                               'Unit' : unit}
                else:
                    schedule[other['Use']] = {time_in_min : {'Amount' : [other['Amount']],
                                                             'Name' : [other['Name']],
                                                             'Unit' : unit}}
                
        return schedule
    
    def print_schedule(scheduling, step):
        return_str = ''
        
        if re.search('Primary', step):
            if 'Primary' in scheduling:
                if step == 'Boil Primary':
                    scheduling = {'Primary' : {key:val for key,val in scheduling['Primary'].items() if re.search('min', val['Unit'])}}
                    step = 'Primary'
                else:
                    scheduling = {'Primary' : {key:val for key,val in scheduling['Primary'].items() if re.search('day', val['Unit'])}}
                    step = 'Primary'
        elif re.search('Secondary', step):
            if 'Secondary' in scheduling:
                if step == 'Boil Secondary':
                    scheduling = {'Secondary' : {key:val for key,val in scheduling['Secondary'].items() if re.search('min', val['Unit'])}}
                    step = 'Secondary'
                else:
                    scheduling = {'Secondary' : {key:val for key,val in scheduling['Secondary'].items() if re.search('day', val['Unit'])}}
                    step = 'Secondary'
        
        for key in dict(filter(lambda item : step in item[0], scheduling.items())):
            if step == 'Whirlpool' or step == 'Hopback' or step == 'Hop Stand':
                return_str = return_str + '\n   Complete the following after the boil but before chilling.\n   '
            elif step == 'Aroma':
                return_str = return_str + '\n   At flame out, complete the following.\n   '
            keys = sorted(scheduling[key].keys())[::-1]
            
            for key2 in keys:
                for i in range(0, len(scheduling[key][key2]['Amount'])):
                    return_str = return_str + f"With {key2} {scheduling[key][key2]['Unit']} left, {key} {scheduling[key][key2]['Amount'][i]} of {scheduling[key][key2]['Name'][i]}.\n   "
                    
        return return_str.strip()
    
    def print_step(scheduling, step):
        return_str = ''
        
        for key in dict(filter(lambda item : step in item[0], scheduling.items())):
            if step == 'First Wort':
                return_str = return_str + ' Add to boil kettle: '
            else:
                return_str = return_str + ' Add '
            for key2 in scheduling[key]:
                for i in range(len(scheduling[key][key2]['Amount'])):
                    if i == 0:
                        return_str = return_str + scheduling[key][key2]['Amount'][i] + ' ' + str(scheduling[key][key2]['Name'][i])
                        if len(scheduling[key][key2]['Amount']) > 2:
                            return_str = return_str + ', '
                        if len(scheduling[key][key2]['Amount']) == 1:
                            return_str = return_str + '.'
                    elif i == len(scheduling[key][key2]['Amount']) - 1:
                        return_str = return_str + ' and ' + scheduling[key][key2]['Amount'][i]+ ' ' + str(scheduling[key][key2]['Name'][i]) + '.'
                    else:
                        return_str = return_str + scheduling[key][key2]['Amount'][i] + ' ' + str(scheduling[key][key2]['Name'][i]) + ', '
                        
        return return_str
        
    def method_specific(recipe):
        scheduling = schedule(recipe)
        
        header = f"""NAME
{recipe['Name']}

STYLE
{recipe['Style']}

METHOD
{recipe['Method']}

{recipe['ingredients']}

INSTRUCTIONS
Santize any equipment that will be in contact with the brew after the boil process. This is very important as we do not want to introduce foreign bacteria to the brew. Brewing santitizer is widely avaialble and labeled with instructions."""
                
        base = f"""
   Bring the wort to a rolling boil. Hold there for {recipe['Boil Time']}.
   {print_schedule(scheduling, 'Boil')}\n{print_schedule(scheduling, 'Boil Primary')}\n{print_schedule(scheduling, 'Boil Secondary')}\n{print_schedule(scheduling, 'Aroma')}\n{print_schedule(scheduling, 'Hop Stand')}\n{print_schedule(scheduling, 'Whirlpool')}{print_schedule(scheduling, 'Hopback')}""".strip() + f"""
3. THE CHILL
   Chill the wort to around room tempterature. The method for this depends on your volume.
4. FERMENTATION
   Pour the wort into your fermentation vessel. Add water to reach {recipe['Batch Size']} Agitate the mixture to bring oxygen into the wort.
   Add your {recipe['yeasts']} to the wort, following the instructions given by the yeast manufacturer.
   Cover your fermenter, fill the airlock to the line with water, and place the airlock in hole in the fermenter lid.
   Fermentation times vary by style of beer. Make sure that you are fermenting for enough time.
   {print_schedule(scheduling, 'Dry Hop')}\n{print_schedule(scheduling, 'Fermentation Primary')}\n{print_schedule(scheduling, 'Fermentation Secondary')}""".strip() + """
5. SERVING VESSEL
   You can choose to bottle or keg your beer. Carbonation instructions vary by choice, so make sure you are equipped to carbonate.
6. ENJOY!"""
        
        if recipe['Method'] == 'All Grain':
            return header + f"""

1. THE MASH
   Start by milling your grain.
   Heat 1.3 quarts of water for every pound of grain to 145-162 degrees, and add it to the mash tun.{print_step(scheduling, 'Mash')}
   Add the grains and stir to make sure that there are no clumps. Make sure that the mash reaches a temperature of 148-158 degrees.
   Allow the mash to rest for about one hour.
   After the rest, raise the mash temperature to 170 degrees by adding near boiling water. Stir well. Leave the mash for another 10 minutes.
   Begin heating the sparge water to 175 degrees.
   Recirculate the mash by siphoning it between two containers and pouring them back down the sides of the mash tun until the wort appears clear.{print_step(scheduling, 'First Wort')}
   {print_step(scheduling, 'Sparge')} Disperse the sparge water over the top of the grain bed while siphoning the wort into the boil kettle at equal rates (1 quart per minute) until you reach {recipe['Pre Boil Size']}.
2. THE BOIL
""" + base

        elif recipe['Method'] == 'BIAB':
            return header + f"""
        
 1. THE MASH
   Heat {recipe['Pre Boil Size']} of water to about 160 degrees in your brew kettle.
   Add your grains to your grain bag.
   Once the water reaches the desired temperature, add the grains to the water, and turn off the heat. Stir gently to remove clumping, and cover with a lid.
   Monitor the heat, making sure that it does not get too low.
   After about 60 minutes, slowly remove the bag from the wort, letting it drain into the kettle.
2. THE BOIL
""" + base

        elif recipe['Method'] == 'Partial Mash':
            return header + f"""
        
1. THE MASH
   Crush your grain, putting it in your grain bag.
   Begin heating 1.5 quarts of water for every pound of grain to 167 degrees.
   Once the water is at the desired temperature, turn off the heat, and add the grain bag. Stir the grain bag around the water. Cover and insulate the kettle, letting the mash steep for 60 minutes.
   In another pot, heat about as much water as used for the mash to 170 degrees.
   Once the mash is done steeping, place the grain bag on a colander on top of the kettle. Slowly pour the water from the second pot over the grains, sparging them until you reach {recipe['Pre Boil Size']} in the kettle.
   Begin heating the kettle until the water reaches 180 degrees. Now, add your malt extract, stirring to make sure it infuses.
 2. THE BOIL
 """ + base
 
        else:
             return header + f"""
         
1. THE MASH
   Begin heating {recipe['Pre Boil Size']} of water in your brew kettle.
   If you have steeping grains, put them in a straining bag. When the water temperature reaches 140 degrees, put the bag into the water. Remove the grains when the temperature reaches 170 degrees.
   When the water reaches 180 degree, add your malt extract, stirring to make sure it infuses.
2. THE BOIL
"""

    return method_specific(recipe)


recipes = pd.read_json('Data/recipes.json')
recipes.dropna(subset=['hops'], inplace=True)

recipes['ingredients'] = recipes.apply(generate_ingredients, axis=1)
recipes['recipe'] = recipes.apply(generate_recipe, axis=1)

if __name__ == '__main__':
    recipes.to_csv('Data/recipes.csv', index=False)
