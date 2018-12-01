import unicodedata,re

def series_ext(titlel):
    """
    タイトル情報から、シリーズ情報を抽出
    スペース、数字の続き以前の文字列をタイトルとする
    """
    title_repl = []
    for i in titlel:
        txt = i

        # nkf対応
        txt = unicodedata.normalize("NFKC", txt)

        # 先頭文字が”（”の場合への対処
        if txt.find('(') >= 0:
            if re.search('\(', txt).start() == 0:
                txt = re.sub('\(', '_', txt)
        else:
            None

        txt = txt.replace('(', ' ')
        txt = txt.replace(')', ' ')
        txt = txt.replace('（', ' ')
        txt = txt.replace('）', ' ')
        txt = re.sub(r'\s+[0-9].*', '', txt)

        txt = re.sub(r'\s+第+[0-9].*', '', txt)
        txt = re.sub(r'\s+ vol.+[0-9].*', '', txt)
        txt = re.sub(r'\s+上.*', '', txt)
        txt = re.sub(r'\s+中.*', '', txt)
        txt = re.sub(r'\s+I.*', '', txt)
        txt = re.sub(r'\s+Ⅱ.*', '', txt)
        txt = re.sub(r'\s+Ⅲ.*', '', txt)

        # ジャンプコミックス
        txt = re.sub(r'[0-9].\s.*', '', txt)

        # 上位層向けの個別対応
        txt = re.sub(r'\sうみまちダイアリー', '', txt)

        title_repl.append(txt)
    return title_repl