import json
import sys
import pandas as pd

sys.path.append("/Users/skai/PycharmProjects/recoman_api/cms")

import numpy as np
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import title_cleansing
import boklog_content_v2
import urllib.parse


def render_json_response(request, data, status=None):
    """response を JSON で返却"""
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    callback = request.GET.get('callback')
    if not callback:
        callback = request.POST.get('callback')  # POSTでJSONPの場合
    if callback:
        json_str = "%s(%s)" % (callback, json_str)
        response = HttpResponse(json_str, content_type='application/javascript; charset=UTF-8', status=status)
    else:
        response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
    return response


# @csrf_exempt
# def debug(request):
#     data = request.POST
#     values = json.loads(request.body)
#     # print(values["name"])
#     # print(values["series"])
#
#     lovetitlel=[]
#
#     for i in values["series"]:
#         lovetitlel.append([values["name"],i,values["series"][i]])
#
#     print(lovetitlel)
#
#     return render_json_response(request, lovetitlel)


@csrf_exempt
def analyze(request):
    """analyze"""
    # 受け取ったPOSTデータ
    # 受け取り後にdecodeかけてjsonをparse
    parsed = urllib.parse.unquote(request.body.decode('utf-8'))
    values = json.loads(parsed)

    lovetitles = []

    for i in values["series"]:
        lovetitles.append([values["name"], i, values["series"][i]])

    # データ追加
    # 選択データDB格納

    username = lovetitles[0][0]

    try:
        # df_Alllog = boklog_content_v2.target_add(lovetitles)
        # タイトル情報からシリーズ情報を加工
        # ユーザーシリーズデータの加工

        # df_Alllog['series'] = title_cleansing.series_ext(df_Alllog['title'])

        # ログをグループ化して集計
        # df_logcust = df_Alllog.groupby(['booklogUserId', 'series'], as_index=False).agg(
        #     {'reviewScore': [np.size, np.max, np.min, np.mean]})
        # df_logcust.columns = ['booklogUserId', 'series', 'rv_num', 'rv_max', 'rv_min', 'rv_mean']

        # マスタデータピボット化
        # df_pivot = df_logcust.pivot(index='booklogUserId', columns='series', values='rv_max').fillna(0)
        # df_pivot = df_pivot.reset_index(drop=False)

        df_pivot = pd.read_csv('./cms/booklog_recopivot.csv', index_col=0, encoding='utf-8')

        # 入力データが既存ログで一致したものをrequestとして投げる方針
        requestl = []
        for lovetitle in lovetitles:
            for series in df_pivot.columns.tolist():
                if lovetitle[1] == series:
                    requestl.append([lovetitle[0], series, lovetitle[2]])

        ##pivotへ追加する
        columl = []
        datel = []

        for num in range(len(requestl)):
            columl.append(requestl[num][1])
            datel.append(requestl[num][2])

        datel = list(map(int, datel))
        datel.insert(0, requestl[0][0])
        columl.insert(0, 'booklogUserId')

        df_request = pd.DataFrame(data=[datel], columns=columl)

        print('df_request', df_request.dtypes)

        # columnの順番を変更せずにセットできる
        df_pivot = df_pivot.append(df_request)[df_pivot.columns.tolist()]
        df_pivot.fillna(0, inplace=True)
        df_pivot.reset_index(drop=True, inplace=True)

        # 評価

        rank = boklog_content_v2.recomend(username, 20, df_pivot)

        rankl = []
        num = 20
        cnt = 0
        for i, j in rank:
            if j > 0:
                if cnt < num:
                    rankl.append([df_pivot.iloc[0:0, i + 1:i + 2].columns.values[0], round(j, 3)])
                    cnt += 1
            else:
                continue

        rank_dic = dict(rankl)

        if len(rank_dic) == 0:
            rank_dic = '該当者なし'

        return render_json_response(request, rank_dic)

    except:
        return render_json_response(request, "なんらかのエラーが発生しました")
