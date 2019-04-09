#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 22:54:38 2019

@author: KevinTang
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

import warnings
warnings.filterwarnings('ignore')

'''
1. first round, not considering some people has 0 money
'''

#define the players
person_n = list(range(1, 101))

#define initial wealth distribution: everyone has $100
wealth = pd.DataFrame(index=person_n, data=[100]*100)

# round 1 game
# every one give out $1
round1 = pd.DataFrame({'pre_round' : wealth[0],'lost' : 1})

# random persons gain certain money
gain = pd.Series(np.random.choice(person_n, 100)).value_counts().rename('gain')

# add the gains into the round 1 game df
round1_result = round1.join(gain).fillna(0)

#calculat the result
round1_result['result'] = round1_result['pre_round'] - round1_result['lost'] + round1_result['gain']


'''
2. first round, considering some people has 0 money
'''
#define the players
person_n = list(range(1, 101))

#define initial wealth distribution: everyone has $100
wealth = pd.DataFrame(index=person_n, data=[100]*100)
wealth[0].iloc[1] = 0
wealth[0].iloc[2] = 200

# round 1 game
# only the ones who have >0 money give out $1
round1 = pd.DataFrame({'pre_round' : wealth[0],'lost' : 0})
round1['lost'][round1['pre_round'] > 0] = 1

# random persons gain certain money of the total give-out money
gain = pd.Series(np.random.choice(person_n, round1['lost'].sum())).value_counts().rename('gain')

# add the gains into the round 1 game df
round1_result = round1.join(gain).fillna(0)

#calculat the result
round1_result['result'] = round1_result['pre_round'] - round1_result['lost'] + round1_result['gain']

# add the first round result into wealth df
wealth[1] = round1_result['result']

'''
3. build the model with function
'''

def game1(data, roundi):
    #print(data)
    round_i = pd.DataFrame({'pre_round' : data[roundi-1],'lost' : 0})
    round_i['lost'][round_i['pre_round'] > 0] = 1
    gain = pd.Series(np.random.choice(range(1,101), round_i['lost'].sum())).value_counts().rename('gain')
    round_i_result = round_i.join(gain).fillna(0)
    round_i_result['result'] = round_i_result['pre_round'] - round_i_result['lost'] + round_i_result['gain']
    data[roundi] = round_i_result['result']
    return data

#define the players
person_n = list(range(1, 101))

#define initial wealth distribution: everyone has $100
wealth = pd.DataFrame(index=person_n, data=[100]*100)

#round1 = game1(wealth, 1)

starttime = time.time()
for n in range(1, 17000):
    wealth = game1(wealth, n)
    print('已计算第%i次' % n)
endtime = time.time()
wealth = wealth.T
print('此次模拟用时%.3f秒' % (endtime - starttime))


























