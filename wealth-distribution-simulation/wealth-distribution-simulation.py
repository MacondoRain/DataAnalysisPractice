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

'''
4. make graphic
'''


def graphic1(data, start, end, step):
    for roundi in range(start, end, step):
        datai = data.iloc[roundi]
        fig = plt.figure(figsize=(18, 9))
        plt.bar(datai.index, datai.values,
                color = 'k', alpha=0.4,
                edgecolor='k', width=1)
        plt.xlim(-10, 110)
        plt.ylim(0, 400)
        plt.grid(linestyle = '--')
        plt.title('Round %i' % roundi)
        plt.ylabel('Wealth')
        plt.xlabel('Player ID')
        plt.savefig('./wealth-distribution-simulation/pic1/round %i.png' % roundi)
        print('绘制第%i轮图表' % roundi)

# 100轮以内，每10轮绘图
graphic1(wealth, 0, 100, 10)

#100至1000轮，按照每100轮绘制一次柱状图，查看财富变化情况
graphic1(wealth, 100, 1000, 100)

# 1000至17000轮，按照每400轮绘制一次柱状图，查看财富变化情况
graphic1(wealth, 1000, 17000, 400)

'''
5. 制作动图GIF
'''
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.animation as animation


#get the corners of the rectangles for the barplot
left = np.array(range(0,100))
right = np.array(range(1,101))
bottom = np.zeros(len(left))
top = bottom + wealth.iloc[0]
nrects = len(left)

#set up the vertex and path codes
# arrays using ``plt.Path.MOVETO``, ``plt.Path.LINETO`` and
# ``plt.Path.CLOSEPOLY`` for each rect.
nverts = nrects * (1 + 3 + 1)
verts = np.zeros((nverts, 2))
codes = np.ones(nverts, int) * path.Path.LINETO
codes[0::5] = path.Path.MOVETO
codes[4::5] = path.Path.CLOSEPOLY
verts[0::5, 0] = left
verts[0::5, 1] = bottom
verts[1::5, 0] = left
verts[1::5, 1] = top
verts[2::5, 0] = right
verts[2::5, 1] = top
verts[3::5, 0] = right
verts[3::5, 1] = bottom

patch = None


def update(roundi):
    # update "top"
    top = bottom + wealth.iloc[roundi]
    top = top.sort_values()
    verts[1::5, 1] = top
    verts[2::5, 1] = top
    return [patch, ]

# Add the patch to the `Axes` instance, and setup
# the `FuncAnimation` with our animate function.
    
fig, ax = plt.subplots(figsize=(800, 600))
barpath = path.Path(verts, codes)
patch = patches.PathPatch(
    barpath, facecolor='grey', edgecolor='black', alpha=0.5)
ax.add_patch(patch)

ax.set_xlim(left[0]-10, right[-1]+10)
ax.set_ylim(bottom.min(), 400)


frame = list(np.arange(0, 100, 10)) + list(np.arange(100, 1000, 100)) + list(np.arange(1000, 17000, 400))

anim = animation.FuncAnimation(fig, update, frames=frame, repeat=False, blit=True)
plt.show()
anim.save('./wealth-distribution-sorted.gif',writer='pillow')














