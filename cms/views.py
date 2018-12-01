from django.shortcuts import render
from .forms import select_manga
import numpy as np

import sys
sys.path.append("/Users/skai/PycharmProjects/recoman/cms")

import boklog_content_v2,title_cleansing

def recoman_top(request):
    """recoman_top"""
    username = 'testuser'

    return render(request,'cms/recoman_top.html',{'username':username})

def recoman_search(request):
    """recoman_search"""
    form = select_manga()

    # ページ到達時点でjsonデータ読み込み、データ化
    # ページ到達に関わらないアプローチに変えたい
    # boklog_content_v2.load_log('dummy')

    return render(request,
                    'cms/recoman_search.html',
                    {'form': form})

def recoman_searchresult(request):
    """recoman_searchsult"""

    #受け取ったPOSTデータ
    form = select_manga(data=request.POST)

    username = form['username'].value()

    lovetitlel=[
        [username, form['manga1'].value(),form['evaluat1'].value()],
        [username, form['manga2'].value(),form['evaluat2'].value()],
        [username, form['manga3'].value(),form['evaluat3'].value()],
        [username, form['manga4'].value(),form['evaluat4'].value()],
        [username, form['manga5'].value(),form['evaluat5'].value()]
    ]

    #データ追加
    #選択データDB格納

    df_Alllog = boklog_content_v2.target_add(lovetitlel)

    # タイトル情報からシリーズ情報を加工
    # ユーザーシリーズデータの加工
    df_Alllog['series'] = title_cleansing.series_ext(df_Alllog['title'])

    # ログをグループ化して集計
    df_logcust = df_Alllog.groupby(['booklogUserId', 'series'], as_index=False).agg({'reviewScore': [np.size, np.max, np.min, np.mean]})
    df_logcust.columns = ['booklogUserId', 'series', 'rv_num', 'rv_max', 'rv_min', 'rv_mean']

    # マスタデータピボット化
    # データは別保存でうまいことできなかなー
    # （通常）ピボット化
    df_pivot = df_logcust.pivot(index='booklogUserId', columns='series', values='rv_max').fillna(0)
    df_pivot = df_pivot.reset_index(drop=False)

    #評価
    rank=boklog_content_v2.recomend(username,20,df_pivot)

    rankl=[]
    num=20
    cnt=0
    for i,j in rank:
        if j>0:
            if cnt <num:
                rankl.append([df_pivot.iloc[0:0,i+1:i+2].columns.values[0],',',round(j,3)])
                cnt+=1
        else:
            continue


    return render(request,
                'cms/recoman_searchresult.html',
                {'rankl': rankl})



def recoman_history(request):
    """recoman_history"""
    return render(request,'cms/recoman_history.html')

