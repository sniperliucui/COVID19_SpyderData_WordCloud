#!/usr/bin/env python
# coding: utf-8

# # 背景描述
# 
# 国家疫情防控一直严格把控，但是近期广州又新增许多新冠肺炎病例。因此，本文的目的是分析全国各地的疫情防控情况进行数据分析与挖掘。
# 

# # 数据获取

# ## 疫情数据获取
# - 通过腾讯新闻公布的数据进行爬取
# - 网址：https://news.qq.com/zt2020/page/feiyan.htm#/

# In[516]:


import time
import json
import requests
import numpy as np
import pandas as pd
from datetime import datetime


# In[517]:


def Domestic():
    """国内疫情数据"""
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
    response = requests.get(url=url).json()
    data = json.loads(response['data'])
    return data

def Oversea():
    """国外疫情数据"""
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_foreign'
    response = requests.get(url=url).json()
    data = json.loads(response['data'])
    return data


# In[518]:


# 查看dict_keys
domestic = Domestic()
oversea = Oversea()
print("domestic.keys: {}".format(domestic.keys()))
print()
print("oversea.keys: {}".format(oversea.keys()))


# ## 疫情数据初步提取及分析

# ### 国内疫情数据提取

# In[519]:


# 提取国内各地区数据明细
areaTree = domestic['areaTree']
lastUpdateTime = domestic['lastUpdateTime']
# print(areaTree)
china_data = areaTree[0]['children']
china_list = []
for a in range(len(china_data)):
    province = china_data[a]['name']  
    confirm = china_data[a]['total']['confirm'] 
    heal = china_data[a]['total']['heal']  
    dead = china_data[a]['total']['dead']  
    nowConfirm = confirm - heal - dead 
    china_dict = {} 
    china_dict['province'] = province  # 地区
    china_dict['nowConfirm'] = nowConfirm  # 现有 
    china_dict['confirm'] = confirm  # 累计
    china_dict['heal'] = heal  # 治愈
    china_dict['dead'] = dead  # 死亡
    china_list.append(china_dict) 

china_data = pd.DataFrame(china_list) 
china_data.to_excel("国内疫情.xlsx", index=False) #存储为EXCEL文件
china_data.head()


# ### 国外疫情数据获取

# In[520]:


foreignList = oversea['foreignList']
foreign_data = foreignList
foreign_list = []
for a in range(len(foreign_data)):
    # 提取数据
    country = foreign_data[a]['name']
    nowConfirm = foreign_data[a]['nowConfirm']  
    confirm = foreign_data[a]['confirm']
    dead = foreign_data[a]['dead']  
    heal = foreign_data[a]['heal'] 
    # 存放数据
    foreign_dict = {}
    foreign_dict['country'] = country
    foreign_dict['nowConfirm'] = nowConfirm
    foreign_dict['confirm'] = confirm
    foreign_dict['dead'] = dead
    foreign_dict['heal'] = heal
    foreign_list.append(foreign_dict)

foreign_data = pd.DataFrame(foreign_list)
foreign_data.to_excel("国外疫情.xlsx", index=False)
foreign_data.head()


# ### 国内外疫情数据整合

# 查询海外疫情数据中是否含有中国疫情数据

# In[521]:


foreign_data.loc[foreign_data['country'] == "中国"]


# 从新增areaTree中提取中国数据，并添加至world_data

# In[522]:


confirm = areaTree[0]['total']['confirm']  # 提取中国累计确诊数据
heal = areaTree[0]['total']['heal']  # 提取中国累计治愈数据
dead = areaTree[0]['total']['dead']  # 提取中国累计死亡数据
nowConfirm = confirm - heal - dead  # 计算中国现有确诊数量

world_data = foreign_data.append(
    {
        'country': "中国",
        'nowConfirm': nowConfirm,
        'confirm': confirm,
        'heal': heal,
        'dead': dead
    },
    ignore_index=True)


# 再次查询数据中是否含有中国疫情数据

# In[523]:


world_data.loc[world_data['country'] == "中国"]


# # 总结与展示

# In[524]:


import pyecharts
import pyecharts.options as opts
from pyecharts.charts import Map
from pyecharts.globals import CurrentConfig, NotebookType
CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_LAB
from pyecharts.commons.utils import JsCode
CurrentConfig.ONLINE_HOST ='https://assets.pyecharts.org/assets/'


# ## 疫情态势可视化

# ### 国内疫情可视化

# 国内各地区现有确诊人数地图

# In[525]:


m = Map()
m.load_javascript()
m.add("", [
    list(z)
    for z in zip(list(china_data["province"]), list(china_data["nowConfirm"]))
],
      maptype="china",
      is_map_symbol_show=False)
m.set_global_opts(
    title_opts=opts.TitleOpts(title="COVID-19中国现有地区现有确诊人数地图"),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=True,
        pieces=[
            {
                "min": 5000,
                "label": '>5000',
                "color": "#893448"
            },  # 不指定 max，表示 max 为无限大
            {
                "min": 1000,
                "max": 4999,
                "label": '1000-4999',
                "color": "#ff585e"
            },
            {
                "min": 500,
                "max": 999,
                "label": '500-1000',
                "color": "#fb8146"
            },
            {
                "min": 101,
                "max": 499,
                "label": '101-499',
                "color": "#ffA500"
            },
            {
                "min": 10,
                "max": 100,
                "label": '10-100',
                "color": "#ffb248"
            },
            {
                "min": 1,
                "max": 9,
                "label": '1-9',
                "color": "#fff2d1"
            },
            {
                "max": 1,
                "label": '0',
                "color": "#ffffff"
            }
        ]))

# 保存动图的html文件
m.render('country.html')


# In[526]:


m.load_javascript();


# pyecharts 使用的所有静态资源文件存放于 pyecharts-assets 项目中，默认挂载在 https://assets.pyecharts.org/assets/
# 
# 但是我在写的时候电脑无法打开上面这个网页，所以我直接render()保存为html文件

# In[527]:


m.render_notebook()


# ### 国际疫情可视化

# In[528]:


# 国家名称中英文映射表,已根据疫情数据中的中文名称进行对应矫正，操作较为麻烦，目前尚有一些缺失国家及地区。
name_dict = {'Liechtenstein': '列支敦士登', 'Morocco': '摩洛哥', 'W. Sahara': '西撒哈拉', 'Serbia': '塞尔维亚', 'Afghanistan': '阿富汗',
                'Angola': '安哥拉', 'Albania': '阿尔巴尼亚', 'Aland': '奥兰群岛', 'Andorra': '安道尔',
                'United Arab Emirates': '阿联酋', 'Argentina': '阿根廷', 'Armenia': '亚美尼亚', 'American Samoa': '美属萨摩亚',
                'Fr. S. Antarctic Lands': '法属南半球和南极领地', 'Antigua and Barb.': '安提瓜和巴布达', 'Australia': '澳大利亚',
                'Austria': '奥地利', 'Azerbaijan': '阿塞拜疆', 'Burundi': '布隆迪', 'Belgium': '比利时', 'Benin': '贝宁',
                'Burkina Faso': '布基纳法索', 'Bangladesh': '孟加拉国', 'Bulgaria': '保加利亚', 'Bahrain': '巴林', 'Bahamas': '巴哈马',
                'Bosnia and Herz.': '波黑', 'Belarus': '白俄罗斯', 'Belize': '伯利兹', 'Bermuda': '百慕大', 'Bolivia': '玻利维亚',
                'Brazil': '巴西', 'Barbados': '巴巴多斯', 'Brunei': '文莱', 'Bhutan': '不丹', 'Botswana': '博茨瓦纳',
                'Central African Rep.': '中非', 'Canada': '加拿大', 'Switzerland': '瑞士', 'Chile': '智利', 'China': '中国',
                "Côte d'Ivoire": '科特迪瓦', 'Cameroon': '喀麦隆', 'Dem. Rep. Congo': '刚果（布）', 'Congo': '刚果（金）',
                'Colombia': '哥伦比亚', 'Comoros': '科摩罗', 'Cape Verde': '佛得角', 'Costa Rica': '哥斯达黎加', 'Cuba': '古巴',
                'Curaçao': '库拉索', 'Cayman Is.': '开曼群岛', 'N. Cyprus': '北塞浦路斯', 'Cyprus': '塞浦路斯', 'Czech Rep.': '捷克',
                'Germany': '德国', 'Djibouti': '吉布提', 'Denmark': '丹麦', 'Dominican Rep.': '多米尼加',
                'Algeria': '阿尔及利亚', 'Ecuador': '厄瓜多尔', 'Egypt': '埃及', 'Eritrea': '厄立特里亚', 'Spain': '西班牙',
                'Estonia': '爱沙尼亚', 'Ethiopia': '埃塞俄比亚', 'Finland': '芬兰', 'Fiji': '斐济', 'Falkland Is.': '福克兰群岛（马尔维纳斯）',
                'France': '法国', 'Faeroe Is.': '法罗群岛', 'Micronesia': '密克罗尼西亚', 'Gabon': '加蓬', 'United Kingdom': '英国',
                'Georgia': '格鲁吉亚', 'Ghana': '加纳', 'Guinea': '几内亚', 'Gambia': '冈比亚', 'Guinea-Bissau': '几内亚比绍',
                'Eq. Guinea': '赤道几内亚', 'Greece': '希腊', 'Grenada': '格林纳达', 'Greenland': '格陵兰', 'Guatemala': '危地马拉',
                'Guam': '关岛', 'Heard I. and McDonald Is.': '赫德岛和麦克唐纳群岛', 'Honduras': '洪都拉斯',
                'Croatia': '克罗地亚', 'Haiti': '海地', 'Hungary': '匈牙利', 'Indonesia': '印度尼西亚', 'Isle of Man': '英国属地曼岛',
                'India': '印度', 'Br. Indian Ocean Ter.': '英属印度洋领土', 'Ireland': '爱尔兰', 'Iran': '伊朗', 'Iraq': '伊拉克',
                'Iceland': '冰岛', 'Israel': '以色列', 'Italy': '意大利', 'Jamaica': '牙买加', 'Jersey': '泽西岛', 'Jordan': '约旦',
                'Japan': '日本', 'Siachen Glacier': '锡亚琴冰川', 'Kazakhstan': '哈萨克斯坦', 'Kenya': '肯尼亚',
                'Kyrgyzstan': '吉尔吉斯斯坦', 'Cambodia': '柬埔寨', 'Kiribati': '基里巴斯', 'Korea': '韩国', 'Kuwait': '科威特',
                'Lao PDR': '老挝', 'Lebanon': '黎巴嫩', 'Liberia': '利比里亚', 'Libya': '利比亚', 'Saint Lucia': '圣卢西亚',
                'Sri Lanka': '斯里兰卡', 'Lesotho': '莱索托', 'Lithuania': '立陶宛', 'Luxembourg': '卢森堡', 'Latvia': '拉脱维亚',
                'Moldova': '摩尔多瓦', 'Madagascar': '马达加斯加', 'Mexico': '墨西哥', 'Macedonia': '北马其顿', 'Mali': '马里',
                'Malta': '马耳他', 'Myanmar': '缅甸', 'Montenegro': '黑山', 'Mongolia': '蒙古', 'N. Mariana Is.': '北马里亚纳',
                'Mozambique': '莫桑比克', 'Mauritania': '毛利塔尼亚', 'Montserrat': '蒙特塞拉特', 'Mauritius': '毛里求斯',
                'Malawi': '马拉维', 'Malaysia': '马来西亚', 'Namibia': '纳米比亚', 'New Caledonia': '新喀里多尼亚', 'Niger': '尼日尔',
                'Nigeria': '尼日利亚', 'Nicaragua': '尼加拉瓜', 'Niue': '纽埃', 'Netherlands': '荷兰', 'Norway': '挪威',
                'Nepal': '尼泊尔', 'New Zealand': '新西兰', 'Oman': '阿曼', 'Pakistan': '巴基斯坦', 'Panama': '巴拿马', 'Peru': '秘鲁',
                'Philippines': '菲律宾', 'Palau': '帕劳', 'Papua New Guinea': '巴布亚新几内亚', 'Poland': '波兰',
                'Puerto Rico': '波多黎各', 'Dem. Rep. Korea': '朝鲜', 'Portugal': '葡萄牙', 'Paraguay': '巴拉圭',
                'Palestine': '巴勒斯坦', 'Fr. Polynesia': '法属波利尼西亚', 'Qatar': '卡塔尔', 'Romania': '罗马尼亚', 'Russia': '俄罗斯',
                'Rwanda': '卢旺达', 'Saudi Arabia': '沙特阿拉伯', 'Sudan': '苏丹', 'S. Sudan': '南苏丹', 'Senegal': '塞内加尔',
                'Singapore': '新加坡', 'S. Geo. and S. Sandw. Is.': '南乔治亚岛和南桑威奇群岛', 'Saint Helena': '圣赫勒拿',
                'Solomon Is.': '所罗门群岛', 'Sierra Leone': '塞拉利昂', 'El Salvador': '萨尔瓦多',
                'St. Pierre and Miquelon': '圣皮埃尔和密克隆', 'São Tomé and Principe': '圣多美和普林西比', 'Suriname': '苏里南',
                'Slovakia': '斯洛伐克', 'Slovenia': '斯洛文尼亚', 'Sweden': '瑞典', 'Swaziland': '斯威士兰', 'Seychelles': '塞舌尔',
                'Syria': '叙利亚', 'Turks and Caicos Is.': '特克斯和凯科斯群岛', 'Chad': '乍得', 'Togo': '多哥', 'Thailand': '泰国',
                'Tajikistan': '塔吉克斯坦', 'Turkmenistan': '土库曼斯坦', 'Timor-Leste': '东帝汶', 'Tonga': '汤加',
                'Trinidad and Tobago': '特立尼达和多巴哥', 'Tunisia': '突尼斯', 'Turkey': '土耳其', 'Tanzania': '坦桑尼亚',
                'Uganda': '乌干达', 'Ukraine': '乌克兰', 'Uruguay': '乌拉圭', 'United States': '美国', 'Uzbekistan': '乌兹别克斯坦',
                'St. Vin. and Gren.': '圣文森特和格林纳丁斯', 'Venezuela': '委内瑞拉', 'U.S. Virgin Is.': '美属维尔京群岛', 'Vietnam': '越南',
                'Vanuatu': '瓦努阿图', 'Samoa': '萨摩亚', 'Yemen': '也门', 'South Africa': '南非', 'Zambia': '赞比亚',
                'Zimbabwe': '津巴布韦', 'Somalia': '索马里', "Anguilla": "安圭拉", 'Dominica': '多米尼克','Gibraltar': '直布罗陀',
                'Guyana': '圭亚那','Saint Kitts and Nevis': '圣基茨和尼维斯','Monaco': '摩纳哥','Maldives': '马尔代夫','San Marino': '圣马力诺',
                'Vatican City': '梵蒂冈','British Virgin Islands': '英属维尔京群岛'}


# In[529]:


name_df = pd.DataFrame(name_dict,index=[0]).T
name_df.columns = ['中文']
name_df.reset_index(inplace=True)
name_df.rename(columns={'index':'英文'}, inplace=True)


# In[530]:


world_data_t = pd.merge(world_data,
                        name_df,
                        left_on="country",
                        right_on="中文",
                        how="inner")

world_data_t


# 世界各国现有确诊人数地图

# In[531]:


m2 = Map()
m2.add("", [
    list(z)
    for z in zip(list(world_data_t["英文"]), list(world_data_t["nowConfirm"]))
],
       maptype="world",
       is_map_symbol_show=False)
m2.set_global_opts(title_opts=opts.TitleOpts(title="COVID-19世界各国现有确诊人数地图"),
                   visualmap_opts=opts.VisualMapOpts(is_piecewise=True,
                                                     pieces=[{
                                                         "min": 20000,
                                                         "label": '>20000',
                                                         "color": "#893448"
                                                     }, {
                                                         "min": 10000,
                                                         "max": 19999,
                                                         "label": '10000-19999',
                                                         "color": "#ff585e"
                                                     }, {
                                                         "min": 5000,
                                                         "max": 9999,
                                                         "label": '5000-9999',
                                                         "color": "#fb8146"
                                                     }, {
                                                         "min": 1001,
                                                         "max": 4999,
                                                         "label": '1001-4999',
                                                         "color": "#ffA500"
                                                     }, {
                                                         "min": 100,
                                                         "max": 1000,
                                                         "label": '100-1000',
                                                         "color": "#ffb248"
                                                     }, {
                                                         "min": 0,
                                                         "max": 99,
                                                         "label": '0-99',
                                                         "color": "#fff2d1"
                                                     }]))
"""取消显示国家名称"""
m2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
m2.render('world.html')


# ## 疫情方寸间

# ### 国内疫情方寸间

# In[532]:


import matplotlib.pyplot as plt
import matplotlib.patches as patches
get_ipython().run_line_magic('matplotlib', 'inline')


# 单独取出中国疫情数据

# In[533]:


China_data = world_data.loc[world_data['country'] == "中国"]  # 单独取出中国疫情数据
China_data.reset_index(drop=True, inplace=True)  # 使索引从0开始递增
China_data


# 提取China_data的累计确诊、累计治愈与累计死亡数据

# In[534]:


# 提取China_data的累计确诊、累计治愈与累计死亡数据
# data.at[n,'name']代表根据行索引和列名，获取对应元素的值
w_confirm = China_data.at[0, 'confirm']
w_heal = China_data.at[0, 'heal']
w_dead = China_data.at[0, 'dead']


# 国内疫情方寸间

# In[535]:


fig1 = plt.figure()

ax1 = fig1.add_subplot(111, aspect='equal', facecolor='#fafaf0')
ax1.set_xlim(-w_confirm / 2, w_confirm / 2)
ax1.set_ylim(-w_confirm / 2, w_confirm / 2)
ax1.spines['top'].set_color('none')
ax1.spines['right'].set_color('none')
ax1.spines['bottom'].set_position(('data', 0))
ax1.spines['left'].set_position(('data', 0))
ax1.set_xticks([])
ax1.set_yticks([])

p0 = patches.Rectangle((-w_confirm / 2, -w_confirm / 2),
                       width=w_confirm,
                       height=w_confirm,
                       facecolor='#29648c',
                       label='confirm')
p1 = patches.Rectangle((-w_heal / 2, -w_heal / 2),
                       width=w_heal,
                       height=w_heal,
                       facecolor='#69c864',
                       label='heal')
p2 = patches.Rectangle((-w_dead / 2, -w_dead / 2),
                       width=w_dead,
                       height=w_dead,
                       facecolor='#000000',
                       label='dead')

plt.gca().add_patch(p0)
plt.gca().add_patch(p1)
plt.gca().add_patch(p2)
plt.title('COVID-19 Square - China', fontdict={'size': 20})
plt.legend(loc='best')
plt.show()


# 国内各省疫情方寸间

# 重新排序数据

# In[536]:


china_data.sort_values("confirm", ascending=False, inplace=True)
china_data.reset_index(drop=True, inplace=True)
china_data


# In[537]:


plt.rcParams['font.sans-serif'] = [u'SimHei']
plt.rcParams['axes.unicode_minus'] = False
fig1 = plt.figure(figsize=(25, 25))
for a in range(25):

    c_confirm = china_data.at[a, 'confirm']
    c_heal = china_data.at[a, 'heal']
    c_dead = china_data.at[a, 'dead']
    ax1 = fig1.add_subplot(25 / 5,
                           5,
                           a + 1,
                           aspect='equal',
                           facecolor='#fafaf0')
    ax1.set_xlim(-w_confirm / 2, w_confirm / 2)
    ax1.set_ylim(-w_confirm / 2, w_confirm / 2)

    ax1.spines['top'].set_color('none')
    ax1.spines['right'].set_color('none')
    ax1.spines['bottom'].set_position(('data', 0))
    ax1.spines['left'].set_position(('data', 0))
    ax1.set_xticks([])
    ax1.set_yticks([])
    p0 = patches.Rectangle((-w_confirm / 2, -w_confirm / 2),
                           width=w_confirm,
                           height=w_confirm,
                           alpha=1,
                           facecolor='#29648c',
                           label='confirm')
    p1 = patches.Rectangle((-w_heal / 2, -w_heal / 2),
                           width=w_heal,
                           height=w_heal,
                           alpha=1,
                           facecolor='#69c864',
                           label='heal')
    p2 = patches.Rectangle((-w_dead / 2, -w_dead / 2),
                           width=w_dead,
                           height=w_dead,
                           alpha=1,
                           facecolor='black',
                           label='dead')
    plt.gca().add_patch(p0)
    plt.gca().add_patch(p1)
    plt.gca().add_patch(p2)


    plt.title(china_data.at[a, 'province'], fontdict={'size': 20})


    plt.legend(loc='best')
plt.show()


# ### 国际疫情方寸间

# 重新排序数据

# In[538]:


world_data_t.sort_values("confirm", ascending=False, inplace=True)
world_data_t.reset_index(drop=True, inplace=True)
world_data_t


# 国际各国疫情方寸间

# In[539]:


plt.rcParams['font.sans-serif'] = [u'SimHei']
plt.rcParams['axes.unicode_minus'] = False
fig1 = plt.figure(figsize=(25, 25))
for a in range(20):

    w_confirm = world_data.at[a, 'confirm']
    w_heal = world_data.at[a, 'heal']
    w_dead = world_data.at[a, 'dead']
    ax1 = fig1.add_subplot(20 / 4,
                           4,
                           a + 1,
                           aspect='equal',
                           facecolor='#fafaf0')
    ax1.set_xlim(-w_confirm / 2, w_confirm / 2)
    ax1.set_ylim(-w_confirm / 2, w_confirm / 2)

    ax1.spines['top'].set_color('none')
    ax1.spines['right'].set_color('none')
    ax1.spines['bottom'].set_position(('data', 0))
    ax1.spines['left'].set_position(('data', 0))
    ax1.set_xticks([])
    ax1.set_yticks([])
    p0 = patches.Rectangle((-w_confirm / 2, -w_confirm / 2),
                           width=w_confirm,
                           height=w_confirm,
                           alpha=1,
                           facecolor='#29648c',
                           label='confirm')
    p1 = patches.Rectangle((-w_heal / 2, -w_heal / 2),
                           width=w_heal,
                           height=w_heal,
                           alpha=1,
                           facecolor='#69c864',
                           label='heal')
    p2 = patches.Rectangle((-w_dead / 2, -w_dead / 2),
                           width=w_dead,
                           height=w_dead,
                           alpha=1,
                           facecolor='black',
                           label='dead')
    plt.gca().add_patch(p0)
    plt.gca().add_patch(p1)
    plt.gca().add_patch(p2)


    plt.title(world_data_t.at[a, '英文'], fontdict={'size': 20})


    plt.legend(loc='best')
plt.show()


# ## 疫情死亡率分析

# ### 国内各省疫情死亡率分析

# In[540]:


china_data['deadRate'] = [0.0 for _ in range(len(china_data))]
china_data['healRate'] = [0.0 for _ in range(len(china_data))]

for i in range(len(china_data)):
    china_data['deadRate'][i] = china_data['dead'][i] / china_data['confirm'][i]
    china_data['healRate'][i] = china_data['heal'][i] / china_data['confirm'][i]

# 查看治愈率小于1.00且死亡率大于0.00的省份
china_data = china_data[china_data['healRate']<=1]
china_data = china_data[china_data['deadRate']>0.00]
china_data.sort_values("healRate", ascending=False, inplace=True)
china_data


# In[541]:


from pyecharts.charts import Bar

print(china_data)
attr, value = list(china_data['province']), list(china_data['healRate'])
value = [format(i, '.2f') for i in value]
print(attr, '\n', value)
bar = Bar(init_opts=opts.InitOpts(width="900px", height="400px"))
bar.add_xaxis(attr)
bar.add_yaxis("中国", value)
bar.set_global_opts(title_opts=opts.TitleOpts(title="中国各省 COVID-19 死亡率"),
                   xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)))

bar.load_javascript();


# In[542]:


# 保存html文件
bar.render('中国各省 COVID-19 死亡率.html')


# In[543]:


bar.render_notebook()


# ### 国际各国疫情死亡率分析

# In[544]:


world_data['deadRate'] = [0.0 for _ in range(len(world_data))]
world_data['healRate'] = [0.0 for _ in range(len(world_data))]

for i in range(len(world_data)):
    world_data['deadRate'][i] = world_data['dead'][i] / world_data['confirm'][i]
    world_data['healRate'][i] = world_data['heal'][i] / world_data['confirm'][i]

# 查看治愈率小于1.00且死亡率大于0.00的国家
world_data = world_data[world_data['healRate']<0.90]
world_data = world_data[world_data['deadRate']>0.00]
world_data.sort_values("deadRate", ascending=False, inplace=True)


# In[545]:


world_data


# In[546]:


from pyecharts.charts import Bar
attr, value = list(world_data['country']), list(world_data['deadRate'])
value = [format(i, '.2f') for i in value]
print(attr, '\n', value)
bar = Bar(init_opts=opts.InitOpts(width="3500px", height="800px"))
bar.add_xaxis(attr)
bar.add_yaxis("世界", value)
bar.set_global_opts(title_opts=opts.TitleOpts(title="世界各国 COVID-19 死亡率"),
                   xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=90)),
                   yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)))

bar.load_javascript();


# In[547]:


bar.render('世界COVID-19 People Dead Rate.html')


# ## 制作疫情词云

# In[548]:


import pandas as pd
import numpy as np
from wordcloud import WordCloud
from matplotlib import colors
from PIL import Image


# ### 中国疫情词云图

# In[549]:


def wordcloud_china():
    data = {i:j for i,j in zip(china_data['province'], china_data['confirm'])}
    
    word_cloud = WordCloud(
        font_path='C:/Windows/Fonts/msyhbd.ttc',
        background_color='white',
        width=1000,
        height=600)
    word_cloud.generate_from_frequencies(data)
    word_cloud.to_file('中国疫情词云图.png')
wordcloud_china()


# ### 国际疫情词云图

# In[550]:


def wordcloud_world():
    data = {i:j for i,j in zip(world_data['country'], china_data['confirm'])}
    
    word_cloud = WordCloud(
        font_path='C:/Windows/Fonts/msyhbd.ttc',
        background_color='white',
        width=1000,
        height=600)
    word_cloud.generate_from_frequencies(data)
    word_cloud.to_file('国际疫情词云图.png')
wordcloud_world()





