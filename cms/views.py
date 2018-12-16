import json
import sys
import pandas as pd
import pymysql

sys.path.append("/Users/skai/PycharmProjects/recoman_api/cms")

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
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
        # テーブルからデータ取得
        # MySQLに接続、データ抽出
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='',
                                     db='recoman',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        connection.commit()
        cur = connection.cursor()
        cur.execute('select userid,title,evaluate  from user_evaluation')
        rows = cur.fetchall()
        df_logcust = pd.DataFrame(rows)

        # 入力データとテーブル抽出データを結合
        df_lovetitle = pd.DataFrame(lovetitles)
        df_lovetitle.columns = ['userid', 'title', 'evaluate']
        df_logcust = pd.concat([df_logcust, df_lovetitle])
        df_logcust.reset_index(drop=True, inplace=True)
        df_logcust = df_logcust[['userid', 'title', 'evaluate']].fillna(0)
        df_logcust = df_logcust.astype({'evaluate': 'int32'})

        # 重複レコードの削除
        df_logcust.drop_duplicates(keep='first', subset=['userid', 'title'], inplace=True)

        # タイトル正規表現処理で欠落？レコードの削除
        df_logcust = df_logcust[[not (i) for i in df_logcust['title'].isnull().tolist()]]

        # 入力されたシリーズ名が既存ログと一致したもののみを対象に評価する
        # requestl = []
        # for lovetitle in lovetitles:
        #     for series in df_pivot.columns.tolist():
        #         if lovetitle[1] == series:
        #             requestl.append([lovetitle[0], series, lovetitle[2]])

        # マトリクス形式のデータ化を行い、レコメンドデータを作成
        # ピボット化
        df_pivot = df_logcust.pivot(index='userid', columns='title', values='evaluate').fillna(0)
        df_pivot = df_pivot.reset_index(drop=False)

        # 評価
        rank = boklog_content_v2.recomend(username, 10, df_pivot)

        rankl = []
        num = 10
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
