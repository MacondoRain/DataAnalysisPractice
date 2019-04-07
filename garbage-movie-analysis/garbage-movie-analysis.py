#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 10:13:39 2019

@author: KevinTang
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

'''
from bokeh.plotting import figure,show,output_file
# 导入图表绘制、图标展示模块
# output_file → 非notebook中创建绘图空间
from bokeh.models import ColumnDataSource
#导入数据类型
from bokeh.core.properties import value
from bokeh.models import HoverTool
#导入工具栏编辑模块
from bokeh.layouts import gridplot
from bokeh.models.annotations import BoxAnnotation
'''
#手动添加matplotlib中文字体，避免中文字体显示乱码
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']


import warnings
warnings.filterwarnings('ignore')

'''
1.load data
'''
df = pd.read_excel('/Users/KevinTang/DataAnalysist/GithubProjects/DataAnalysisPractice/garbage-movie-analysis/moviedata.xlsx')


'''
2. 烂片 top20
'''
data1 = df.dropna(subset=['豆瓣评分'])

fig,axes = plt.subplots(2,1, figsize=(10,10))
data1['豆瓣评分'].plot.hist(bins=50, ax=axes[0], 
     colormap='Greens_r', alpha=0.5, edgecolor='k', title="豆瓣评分数据分布-直方图")
data1['豆瓣评分'].plot.box(vert=False, ax=axes[1], title="豆瓣评分数据分布-箱型图")

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
           tools=[hover, 'box_select,reset,wheel_zoom,pan,crosshair'],
           title='电影类型烂片率分析')

p.circle('index','type_lp_pre',size='size',source=source,
         fill_color='red', fill_alpha=0.7,
         line_color='black', line_dash='dashed', line_alpha=0.9,
         )

output_file('/Users/KevinTang/DataAnalysist/GithubProjects/DataAnalysisPractice/garbage-movie-analysis/烂片类型分析.html', 
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
hp_lp_count = data6[data6['豆瓣评分']<k].groupby('hp_gj')['电影名称'].count().rename('hp_lp_count')

hp_fx = pd.merge(pd.DataFrame(hp_gj_count),pd.DataFrame(hp_lp_count), right_index=True, 
                 left_index=True, how='outer')

hp_fx = hp_fx[hp_fx['hp_count'] >= 3].fillna(0)
hp_fx['lp_pre'] = hp_fx['hp_lp_count']/hp_fx['hp_count']

hp_fx.sort_values(by=['lp_pre'], inplace=True, ascending=False)

# 6.烂片与主演数量

#主演字段数据清洗
data7 = data1.dropna(subset=["主演"])
data7['主演'] = data7['主演'].str.replace(' ', '')

#拆分“主演”字段
lp_yy = data7['主演'].str.split('/', expand=True).stack()
lp_yy = lp_yy.reset_index(level=1, drop=True).rename('演员')
data_yy = data7.join(lp_yy)

#主演人数分类:'1-2人', '3-4人', '5-6人', '7-9人', '10以上'
yy_count = data_yy.groupby('电影名称')['演员'].count()
listBins = [0, 3, 5, 7, 10, 10000000]
listLabels = ['1-2人', '3-4人', '5-6人', '7-9人', '10以上']
yy_count_fx = pd.cut(yy_count, bins=listBins, labels=listLabels)
yy_count_fx.name = '主演人数分类'
data_yy_count = pd.merge(data7, yy_count_fx, left_on='电影名称', right_index=True)

#按照主演人数分类分析烂片率
yy_type_count = data_yy_count.groupby('主演人数分类')['电影名称'].count().rename('电影数量')
yy_type_lp_count = data_yy_count[data_yy_count['豆瓣评分']<k].groupby('主演人数分类')['电影名称'].count().rename('烂片数量')
yy_type_fx01 = pd.merge(pd.DataFrame(yy_type_count),pd.DataFrame(yy_type_lp_count), right_index=True, 
                 left_index=True, how='outer')
yy_type_fx01['烂片比例'] = yy_type_fx01['烂片数量']/yy_type_fx01['电影数量']

#查看明星的烂片率
yy_dy_count = data_yy.groupby('演员')['电影名称'].count().rename('电影数量')
yy_lp_count = data_yy[data_yy['豆瓣评分']<k].groupby('演员')['电影名称'].count().rename('烂片数量')
yy_lp_fx = pd.merge(pd.DataFrame(yy_dy_count),pd.DataFrame(yy_lp_count), right_index=True, 
                 left_index=True, how='outer')
yy_lp_fx.fillna(0, inplace=True)
yy_lp_fx['烂片比例'] = yy_lp_fx['烂片数量']/yy_lp_fx['电影数量']
yy_lp_fx01 = yy_lp_fx.sort_values('烂片比例', ascending=False)
wyf_lp_fx = yy_lp_fx01[yy_lp_fx01.index == '吴亦凡']
wyf_dy = data7[data7['主演'].str.contains('吴亦凡')]

# 7.导演的产出率、烂片率和平均分

#统计导演电影数量，去掉电影数量少于10部的导演
data8 = data1.dropna(subset=['导演', '上映日期'])
dircount = data8.groupby(['导演']).count()
dircount10 = dircount[dircount['电影名称'] >= 10]
dircount10 = dircount10['电影名称'].rename('电影数量')

dir_data = pd.merge(data8, dircount10, left_on='导演', right_index=True)
dir_data = dir_data[['电影名称', '豆瓣评分', '上映日期', '导演', '电影数量']]

#导演的烂片率
dir_lp_count = dir_data[dir_data['豆瓣评分']<k].groupby('导演')['电影名称'].count().rename('烂片数量')
dir_lpl = pd.merge(dircount10, dir_lp_count, right_index=True, left_index=True, how='outer').fillna(0)
dir_lpl['烂片率'] = dir_lpl['烂片数量']/dir_lpl['电影数量']

#筛选出上映年份
dir_data['year'] = dir_data['上映日期'].str.replace(' ', '').str[:4]

#导演每年产量、平均分
dir_cl_year = dir_data.groupby(['导演', 'year'])['电影名称'].count().rename('fil_count')
dir_averscore_year = dir_data.groupby(['导演', 'year'])['豆瓣评分'].mean().rename('aver_score')

dir_data_fx = pd.merge(dir_cl_year, dir_averscore_year, left_index=True, right_index=True).reset_index()
dir_data_fx.columns = ['dir', 'year', 'fil_count', 'aver_score']

#Bokeh出散点图
dir_data_fx = dir_data_fx.sort_values('year')
dir_data_fx = dir_data_fx[dir_data_fx['year'] > '2007']

x_range = dir_data_fx['year'].unique().tolist()
dir_data_fx['size'] = dir_data_fx['fil_count']**0.5*10
colors = ['red', "olive", "darkred", "goldenrod" ]

hover = HoverTool(tooltips=[
                            ('该年电影平均分','@aver_score'),
                            ('该年电影产量', '@fil_count')])

p1 = figure(plot_width=800, plot_height=400,x_range=x_range, 
           tools=[hover, 'box_select,reset,wheel_zoom,pan,crosshair'],
           title='导演年产量和平均评分')

color_num = 0
for dire in dir_data_fx['dir'].unique():

    source = ColumnDataSource(data=dir_data_fx[dir_data_fx['dir'] == dire])

    p1.circle('year', 'aver_score', size = 'size', source = source,
              fill_color = colors[color_num], fill_alpha = 0.7, 
              line_color = 'black', line_dash = 'dashed', line_alpha = 0.9,
              legend = dire)
    color_num += 1

output_file('/Users/KevinTang/DataAnalysist/GithubProjects/DataAnalysisPractice/garbage-movie-analysis/导演年产量和平均分.html', 
            mode='inline')
show(p1)















