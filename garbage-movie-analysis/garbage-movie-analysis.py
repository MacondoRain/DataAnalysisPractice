#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 10:13:39 2019

@author: KevinTang
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

'''
1.load data
'''
df = pd.read_excel('/Users/KevinTang/DataAnalysist/06 DataAnalysisPractics/Project11/moviedata.xlsx', sheet=0)


'''
2. 烂片top20
'''
data1 = df.dropna(subset=['豆瓣评分'])
data1['豆瓣评分'].hist(bins=50)
plt.boxplot(data1['豆瓣评分'],vert=False)

k = data1['豆瓣评分'].quantile(0.25) #上四分位数为烂片标准
data_lp = data1[data1['豆瓣评分']<k]

data_lp.sort_values(by = ['豆瓣评分'], inplace=True)
data_lp_top20 = data_lp[:20].reset_index()

'''
3. 烂片题材分析
'''

data2 = data1.dropna(subset=['类型'])

'''
把有多个类型的行，拆分成多行
'''
lx = data2['类型'].str.replace(' ', '').str.split('/', expand=True).stack() #expand为一个dataframe，stack成一个Series
lx = lx.reset_index(level=1, drop=True).rename('type')
data3 = data2.join(lx)
data3 = data3[['电影名称', '豆瓣评分', 'type']]

'''
给烂片打标签
'''
data31 = data3[data3['豆瓣评分']<k]
data31['烂片'] =True
data32 = data3[data3['豆瓣评分'] >= k]
data32['烂片'] =False
data4 = pd.concat([data31, data32])

'''
按照类型统计电影数量和烂片数量
'''
lx_typecount = data4.groupby('type').count()['电影名称'].rename('typecount')
lp_typecount = data4[data4['烂片']==True].groupby('type').count()['电影名称'].rename('lp_typecount')

lp_fx = pd.merge(pd.DataFrame(lx_typecount), pd.DataFrame(lp_typecount), left_index=True, right_index=True, how='outer')
lp_fx.fillna(0, inplace=True)
lp_fx['type_lp_pre'] = lp_fx['lp_typecount']/lp_fx['typecount']

lp_fx.sort_values(by=['type_lp_pre'], inplace=True, ascending=False)
lp_lx_top20 = lp_fx[:20]

'''
4. 烂片分析boke出图
'''
from bokeh.plotting import figure,show,output_file
from bokeh.models import ColumnDataSource, HoverTool

lp_lx_top20.index.name='index'
lp_lx_top20['size'] = lp_lx_top20['typecount']/10
x_range = lp_lx_top20.index.tolist()

source = ColumnDataSource(data=lp_lx_top20)

hover = HoverTool(tooltips=[
                            ('数据量','@typecount'),
                            ('烂片比例', '@type_lp_pre')])

p = figure(plot_width=800, plot_height=400,x_range=x_range,
           tools=[hover, 'box_select,reset,wheel_zoom,pan,crosshair'])

p.circle('index','type_lp_pre',size='size',source=source,
         fill_color='red', fill_alpha=0.7,
         line_color='black', line_dash='dashed', line_alpha=0.9)

output_file('/Users/KevinTang/DataAnalysist/06 DataAnalysisPractics/Project11/result/烂片类型分析.html', 
            mode='inline')
show(p)


'''
5. 合拍烂片分析
'''
data5 = data1.dropna(subset=['制片国家/地区'])
data5 = data5[data5['制片国家/地区'].str.contains('/')]
data5['制片国家/地区'] = data5['制片国家/地区'].str.replace(' ', '')

data5 = data5[data5['制片国家/地区'].str.contains('中国大陆')]

data5['制片国家/地区'] = data5['制片国家/地区'].str.replace('中国大陆', '')
data5['制片国家/地区'] = data5['制片国家/地区'].str.replace('香港','')
data5['制片国家/地区'] = data5['制片国家/地区'].str.replace('台湾', '')

hp_gj = data5['制片国家/地区'].str.split('/', expand=True).stack()
hp_gj = hp_gj.reset_index(level=1, drop=True).rename('hp_gj')
data6 = data5.join(hp_gj)
data6 = data6[data6['hp_gj'] != '']

hp_gj_count = data6.groupby('hp_gj')['电影名称'].count().rename('hp_count')
hp_lp_count = data6[data6['豆瓣评分']<k].groupby('hp_gj')['电影名称'].count().rename('c')

hp_fx = pd.merge(pd.DataFrame(hp_gj_count),pd.DataFrame(hp_lp_count), right_index=True, 
                 left_index=True, how='outer')

hp_fx = hp_fx[hp_fx['hp_count'] >= 3].fillna(0)
hp_fx['lp_pre'] = hp_fx['hp_lp_count']/hp_fx['hp_count']

hp_fx.sort_values(by=['lp_pre'], inplace=True, ascending=False)

