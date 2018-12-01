import json,re
import pandas as pd
import numpy as np

import unicodedata

#from scipy.sparse import csr_matrix
#from sklearn.neighbors import NearestNeighbors

# jsonデータから読み込み
#ページに到達した時点で裏で最新のjsonファイルから構築する

def load_log(json_path):

    json_path = '/Users/skai/python_sample/alu_test_anly/input/booklog_data.json'

    r = open(json_path, 'r')
    alujson = json.load(r)

    alllog = []

    for i in alujson['data']:
        for j in i['reviews']:
            alllog.append([j['booklogUserId'], j['title'], j['reviewScore'], j['authors'][0], j['categoryId']])

    df_Alllog = pd.DataFrame(alllog, columns=['booklogUserId', 'title', 'reviewScore', 'authors', 'categoryId'])

    # 'booklogUserId','title',で重複する行をSoreの高い方を残して削除
    df_Alllog.sort_values(by=['booklogUserId', 'title', 'reviewScore'], ascending=['True', 'True', 'False'],inplace=True)
    df_Alllog.drop_duplicates(keep='first', subset=['booklogUserId', 'title'], inplace=True)

    df_Alllog.to_csv('/Users/skai/PycharmProjects/recoman/cms/load_log.csv')


# データ追加
def target_add(lovetitlel):
    # ユーザー、好きなタイトル

    df_dummy = pd.DataFrame(lovetitlel)
    df_dummy.columns = ['booklogUserId', 'title', 'reviewScore']

    df_dummy['authors'] = ''
    df_dummy['categoryId'] = ''

    # ログデータの読み込み
    df_Alllog = pd.read_csv('/Users/skai/PycharmProjects/recoman/cms/load_log.csv')

    # dummy追加
    df_Alllog = pd.concat([df_Alllog, df_dummy], axis=0)

    df_Alllog['reviewScore'] = df_Alllog['reviewScore'].astype(int)

    return df_Alllog


#########################
# 選択データDB格納
#########################


def similarities_search(scores, target,target_user_index):
    """
    tgユーザーに対して、共通の評価が少ないデータを場合を除外すべく、
    対象データの評価値と全データの評価値を掛け合わせ、
    結果が全て０（同タイトルを評価していない）ではないデータを対象とする
    """
    similarities = []

    for i, score in enumerate(scores):
        indices = np.where(np.array(target) * np.array(score) != 0)[0]

        # 共通評価シリーズが１件以上、tg自身ではないことを判断
        if i == target_user_index or len(indices) < 2:
            continue

        # tgユーザーと、同コンテンツへ評価を行ったユーザーの相関を求める
        similarity = np.corrcoef(target, score)[0, 1]

        # レコメンドなので、負の相関、足きりを下回る相関関係は対象外にする
        if np.isnan(similarity) or similarity < 0.01:
            continue

        similarities.append((i, similarity))

    similarities = sorted(similarities, key=lambda s: s[1], reverse=True)
    return similarities


# 対象ユーザーにレコメンドした際のレートを予測する
# https://ohke.hateblo.jp/entry/2017/09/22/230000

def predict(scores, similarities, target_user_index, target_item_index):
    target = scores[target_user_index]

    # 対象ユーザーの平均評価点
    avg_target = np.mean(target[np.where(target >= 0)])

    numerator = 0.0
    denominator = 0.0
    k = 0

    # 相関関係にある類似ユーザー分繰り返し
    for similar in similarities:

        # 相関係数順の上位より処理開始、５件抽出されたところで終了
        if k > 5 or similar[1] <= 0.0:
            break

        # 類似ユーザーの評価
        score = scores[int(similar[0])]

        if score[target_item_index] >= 0:
            # 対象アイテムに対する類似ユーザーの評価値を加算
            denominator += similar[1]
            # denominator += score[target_item_index]

            # アイテムの評価値＊（類似ユーザーにおけるアイテム評価値の分散）を加算
            numerator += similar[1] * (score[target_item_index] - np.mean(score[np.where(score >= 0)]))
            # numerator += score[target_item_index]   * (score[target_item_index] - np.mean(score[np.where(score >= 0)]))
            k += 1
            # print(avg_target + (numerator / denominator) )

    return avg_target + (numerator / denominator) if denominator > 0 else -1


###targetUserIdを指定してレコメンド情報を提供

def rank_items(scores, similarities, target,target_user_index):
    rankings = []
    # 評価タイトル全て
    for i in range(len(target)):
        # 既に評価済みの場合はスキップ
        if target[i] > 0:
            continue

        rankings.append((i, predict(scores, similarities, target_user_index, i)))

    return sorted(rankings, key=lambda r: r[1], reverse=True)


def recomend(targetUserId,num,df_pivot):
    ##対象ユーザー名からpivotのインデックス設定
    target_user_index = df_pivot[df_pivot['booklogUserId'] == targetUserId].index[0]

    # 全pivotデータの評価値のみリスト
    scores = np.array(df_pivot.iloc[0:, 1:].values.tolist())

    # 対象ユーザーのみの評価値リスト
    target = scores[target_user_index]

    # 類似ユーザーのIDリスト
    global similarities

    similarities = similarities_search(scores, target,target_user_index)

    rank = rank_items(scores, similarities, target,target_user_index)

    return rank
