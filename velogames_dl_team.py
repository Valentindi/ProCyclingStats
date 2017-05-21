# -*- coding: utf-8 -*-
"""
Velogames - download team points per stage

Author: Klemen Ziberna
"""


#####################################
# GLOBAL VARIABLES

# Template url
#overall_url = "https://www.velogames.com/giro-ditalia/2017/teamroster.php?tid=590be698bbe75142"
#stage_url = "https://www.velogames.com/giro-ditalia/2017/teamroster.php?tid=590be698bbe75142&ga=13&st=1"

BASE_URL = "https://www.velogames.com/giro-ditalia/2017/teamroster.php"
Teams_dict_url = {
                  'Klemen': 'tid=590be698bbe75142',
                  'Toby': 'tid=590b0e844a4d1742',
                  'Peter': 'tid=590c2b16e6eba921',
                  'James': 'tid=590c35d156952570',
                  'Parag': 'tid=590739ca1d1c8610',
                  'Andy': 'tid=590c4b26d04bf397',
                  'Pip': 'tid=590b9e73d6bf2899'
                  }


#####################################
# LIBRARIES

from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#####################################
# FUNCTIONS
 
def get_stage_score(main_page_url, team_id, stage_N):
    # Load page
    stage_url = main_page_url + "?" + team_id + "&st=" + str(stage_N)
    stage_page = requests.get(stage_url)
    stage_page_bs = \
        bs(stage_page.content.decode('utf-8', 'ignore'), 'html.parser')
        
    # Extract stage score
    stage_find_string = 'Stage ' + str(stage_N) + ' Score:'
    stage_score_find = stage_page_bs.find(string=re.compile(stage_find_string))
    stage_score = stage_score_find.next_sibling.string
    
    return int(stage_score)
    

def get_team_riders(main_page_url, team_id):
        
    # Load page
    team_url = main_page_url + "?" + team_id
    team_page = requests.get(team_url)
    team_page_bs = \
        bs(team_page.content.decode('utf-8', 'ignore'), 'html.parser')
    
    # Find riders' names
    team_riders_find = \
        team_page_bs.findAll('a', href = re.compile('riderprofile.php?'))
    
    team_riders = []
    for item in team_riders_find:
        team_riders.append(item.text)
    
    return team_riders


#####################################
# MAIN PROGRAM

# Dowload a list of riders for every team

team_riders = {}

for item in Teams_dict_url:
    print('Dowloading riders for: ' + item)
    team_riders[item] = get_team_riders(BASE_URL, Teams_dict_url[item])
    

# Download scores

Giro_N_stages = 21

# Get scores for every team

result_list = []

for item in Teams_dict_url:
    print('Dowloading data for: ' + item)
    team_dict_out = {}
    stage_score_list = []
    team_dict_out['Name'] = item
    
    for n in range(0,Giro_N_stages):
        print('Stage number: ' + str(n+1))
        stage_score_list.insert(n, \
                                get_stage_score(BASE_URL, \
                                                Teams_dict_url[item], n+1))
    
    team_dict_out['Stage_Score'] = stage_score_list
    team_dict_out['Cumulative_Score'] = np.cumsum(stage_score_list).tolist()
    team_dict_out['Stage_N'] = list(range(1,Giro_N_stages+1))
    
    result_list.append(team_dict_out)

    


# Create outputs
team_riders_df = pd.DataFrame(team_riders)

result_list_df = pd.DataFrame(result_list)

stage_scores = result_list_df['Stage_Score'].apply(pd.Series).transpose()
stage_scores.columns = result_list_df['Name']

cum_scores = result_list_df['Cumulative_Score'].apply(pd.Series).transpose()
cum_scores.columns = result_list_df['Name']


# Stage winners and overall leaders
winners_df = pd.DataFrame()
winners_df['Stage_N'] = list(range(1,Giro_N_stages+1))
winners_df['Stage_Score_Winner'] = stage_scores.idxmax(axis=1)
winners_df['Stage_Score_Winner_Pts'] = stage_scores.max(axis=1)
winners_df['Overall_Score_Leader'] = cum_scores.idxmax(axis=1)
winners_df['Stage_Score_Leader_Pts'] = cum_scores.max(axis=1)


# Save to csv file
team_riders_df.to_csv('team_riders.csv')
stage_scores.to_csv('stage_scores.csv')
cum_scores.to_csv('cum_scores.csv')
winners_df.to_csv('winners.csv')


# Plot figures
Giro_last_stage = 14

stage_scores[0:Giro_last_stage].plot(linestyle='None', marker='o', grid=1)
plt.xlim(-1,Giro_last_stage)
plt.xticks(list(range(0,Giro_last_stage)), list(range(1,Giro_last_stage+1)))
plt.title('Giro 2017: Individual stage scores')
plt.legend(bbox_to_anchor=(1, 0.5), loc='center left', ncol=1, numpoints=1)
plt.ylabel('Points')
plt.xlabel('Stage')
plt.savefig('stage_scores.png', bbox_inches='tight')

cum_scores[0:Giro_last_stage].plot(linestyle='-', marker='|', grid=1)
plt.xlim(0,Giro_last_stage-1)
plt.xticks(list(range(0,Giro_last_stage)), list(range(1,Giro_last_stage+1)))
plt.title('Giro 2017: Cumulative scores')
plt.legend(bbox_to_anchor=(1, 0.5), loc='center left', ncol=1, numpoints=1)
plt.ylabel('Points')
plt.xlabel('Stage')
plt.savefig('cum_scores.png', bbox_inches='tight')





































