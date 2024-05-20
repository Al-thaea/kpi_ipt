from spyre import server
import pandas as pd
from os import listdir
from datetime import datetime
import urllib.request
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt

def dwn (i, y1, y2):
    url=f'https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={i}&year1={y1}&year2={y2}&type=Mean'
    wp = urllib.request.urlopen(url)
    text = wp.read()

    now = datetime.now()
    date_and_time_time = now.strftime('%d-%m-%Y_%H-%M-%S')
    out = open('data/NOAA_ID'+'_'+str(i)+'_'+date_and_time_time+'.csv','wb') # 'data/' — dir name
    out.write(text)
    out.close()

def csvs_to_frame(dir):
    file_names = listdir(dir)

    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'AreaID']
    dfs = []

    for name in file_names:
        df = pd.read_csv(dir+name, header = 1, names = headers)
        df['AreaID'] = int(name.split("_")[2])

        # data cleaning
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df = df.drop(df.index[-1])
        df.at[0, 'Year'] =  df.at[0, 'Year'][9:]
        df['Year'] = df['Year'].astype(int)

        dfs.append(df)

    frame = pd.concat(dfs).drop_duplicates().reset_index(drop=True)
    return frame

#==================================================

user_input = input("wanna download data? (y/n): ")
if user_input == "y":
   for i in range(1,28): # y 29
       dwn(i, 2000, 2020)

df = csvs_to_frame('data2/')

#==================================================

class WebApp(server.App):
    title = "NOOA vizualization"

    inputs = [{"type": "dropdown",
                "label": "Region",
                "options":  [{"label": "Вінницька", "value": "1"},
                                {"label": "Волинська", "value": "2"},
                                {"label": "Дніпропетровська", "value": "3"},
                                {"label": "Донецька", "value": "4"},
                                {"label": "Житомирська", "value": "5"},
                                {"label": "Закарпатська", "value": "6"},
                                {"label": "Запорізька", "value": "7"},
                                {"label": "Івано-Франківська", "value": "8"},
                                {"label": "Київська", "value": "9"},
                                {"label": "Кіровоградська", "value": "10"},
                                {"label": "Луганська", "value": "11"},
                                {"label": "Львівська", "value": "12"},
                                {"label": "Миколаївська", "value": "13"},
                                {"label": "Одеська", "value": "14"},
                                {"label": "Полтавська", "value": "15"},
                                {"label": "Рівенська", "value": "16"},
                                {"label": "Сумська", "value": "17"},
                                {"label": "Тернопільська", "value": "18"},
                                {"label": "Харківська", "value": "19"},
                                {"label": "Херсонська", "value": "20"},
                                {"label": "Хмельницька", "value": "21"},
                                {"label": "Черкаська", "value": "22"},
                                {"label": "Чернівецька", "value": "23"},
                                {"label": "Чернігівська", "value": "24"},
                                {"label": "Республіка Крим", "value": "25"},
                                {"label": "Севастополь", "value": "26"},
                                {"label": "КиЇв", "value": "27"}],
                 "key": "region",
                "action_id": "update_data"},
            #   dict( type='text',
            #         key='AreaID',
            #         label='Area ID here',
            #         value='5',
            #         action_id='update_data'),  -- у мене не працював дропдаун із виборои регіонів, тому для достовірності вводила вибір вручну по індексам
              dict(type='text',
                    key='week1',
                    label='min week',
                    value='1',
                    action_id='update_data'),
              dict(type='text',
                    key='week2',
                    label='max week',
                    value='52',
                    action_id='update_data'),
              dict(type='text',
                    key='year1',
                    label='min_year',
                    value='2001',
                    action_id='update_data'),
              dict(type='text',
                    key='year2',
                    label='max_year',
                    value='2019',
                    action_id='update_data'),
              {"type":'dropdown',
               "label":'NOAA data dropdown',
               "options": [{"label": "VHI", "value":"VHI"},
                         {"label": "VCI", "value":"VCI"},
                         {"label": "TCI", "value":"TCI"}],
               "key": 'indicator',
               "action_id": "update_data"}]
    
    controls = [{"type" : "hidden",
                 "id" : "update_data"}]

    tabs = ["Table", "Plot"]

    outputs = [{"type":"table",
                 "id":"table_id",
                 "control_id":"update_data",
                 "tab":"Table",
                 "on_page_load":True},
                 {"type":"plot",
                 "id":"plot",
                 "control_id":"update_data",
                 "tab":"Plot"}]
    global df
    def getTable(self, params):
        
        w1 = int(params["week1"])
        w2 = int(params["week2"])
        y1 = int(params["year1"])
        y2 = int(params["year2"])
        # AreaID = int(params["AreaID"])
        region = int(params["region"])
        indicator = params["indicator"]

        result_df = df[[indicator, 'Year', 'Week', 'AreaID']]
        result_df = result_df[(df['AreaID'] == region)]
        result_df = result_df[df['Year'].between(y1, y2)]
        # result_df = result_df[(df["AreaID"]) == AreaID]
        result_df = result_df[(df["Week"]) >= w1]
        result_df = result_df[(df["Week"]) <= w2]
        return result_df


    def getPlot(self, params):
        indicator = params["indicator"]
        # plt_obj = self.getTable(params).plot(x = "Week", y = indicator)
        # fig = plt_obj.get_figure()
        # return fig
        data = self.getTable(params)
        color_palette = sns.color_palette("husl", len(data['Year'].unique()))
        plt_obj = None
        for i, (year, year_data) in enumerate(data.groupby('Year')):
            plt_obj = year_data.plot(x='Week', y=indicator, label=year, color=color_palette[i], ax=plt_obj)
        plt.legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')
        plot = plt_obj.get_figure()
        return plot
        

app = WebApp()
app.launch(port=8800)