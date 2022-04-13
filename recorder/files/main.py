# -*- coding: utf-8 -*-

import sys
import warnings

#------------------------------------------------------------------------------
# SYSTEM設定
#
# - バイナリコード出力抑止
# - 実行時警告の出力抑止
#------------------------------------------------------------------------------

sys.dont_write_bytecode = True
warnings.filterwarnings( 'ignore' )


#------------------------------------------------------------------------------
# インポート設定
#------------------------------------------------------------------------------

import time
import json
import traceback
import subprocess
import hashlib
from subprocess import Popen
from multiprocessing import Process
from pathlib import Path
from datetime import datetime as dtm
from datetime import timedelta as tmdlt

import log


g_lg = None

def main():

    global g_lg
    g_lg = log.LOG("log", "logfile")
    g_lg.output("INF", "プロセス起動")

    # 処理情報テーブル
    d_tbl = []

    # プロセス情報テーブル
    p_tbl = []

    #============#
    # 処理ループ #
    #============#
    while True:

        #------------------------#
        # 処理情報テーブルの更新 #
        #------------------------#
        read_config(d_tbl)

        #------------------#
        # 処理起動チェック #
        #------------------#
        n = dtm.now()
        g_lg.output("dbg", "該当情報有無チェック 現時刻=" + str(n))

        for one_rec in d_tbl:

            # 次開始時刻が無いものは処理対象外
            if one_rec['next_start'] is None:
                continue

            # 次開始時刻を過ぎているものは、処理対象
            if one_rec['next_start'].strftime('%Y%m%d_%H%M%S') <= n.strftime('%Y%m%d_%H%M%S'):

                # 処理起動
                record_start(p_tbl,
                        one_rec['title'], one_rec['channel'],
                        one_rec['next_start'], one_rec['order_minute'] + 4)

                # 次開始時刻を更新
                nxt_st = get_next_start(one_rec['order_day'], one_rec['order_time'])
                one_rec['next_start'] = nxt_st

                g_lg.output("INF", "NEXT START=" + str(nxt_st))

#            print(one_rec)

        #----------------------# 
        # プロセス終了チェック #
        #----------------------# 
        for one_p in p_tbl:

            if not one_p.is_alive():
                g_lg.output("INF", "プロセス終了を検知 p=" + str(one_p))

                one_p.join
                p_tbl.remove(one_p)

        time.sleep(10)

    return()


def read_config(d_tbl):

    ## g_lg.output("dbg", "設定ファイル読み込み")

    # 既存テーブルのチェック済みフラグを一度OFFにする
    for one_d in d_tbl:
        one_d['checked'] = False

    # データのファイル一覧を取得
    p = Path("./data")
    l = list(p.glob("rec_*.json"))
    ## g_lg.output("dbg", "ファイル一覧 " + str(l))

    for one_p in l:

        filename = str(one_p)

        with open(filename, "r", encoding="utf-8") as fr:
            jsonstr = fr.read()

        with open(filename, "rb") as fr:
            checksum = hashlib.sha256(fr.read()).hexdigest()

        f_list = [one_d.get('filename') for one_d in d_tbl]
        idx = f_list.index(filename) if filename in f_list else None

        if idx is None:
            # 新規追加
            g_lg.output("INF", "新規追加 " + filename)

            add_rec = {}
            add_rec['filename'] = filename
            d_tbl.append(add_rec)

            idx = len(d_tbl) - 1

        elif d_tbl[idx]['checksum'] != checksum:
            # 更新
            g_lg.output("INF", "更新 " + filename)
            nop()
        else:
            # 更新なし
            ## g_lg.output("dbg", "更新なし " + filename)
            d_tbl[idx]['checked'] = True
            continue

        jsn = json.loads(jsonstr)

        d_tbl[idx]['checksum'] = checksum

        d_tbl[idx]['title'] = jsn['title']
        d_tbl[idx]['channel'] = jsn['channel']

        d_tbl[idx]['order_day'] = jsn['date']
        d_tbl[idx]['order_time'] = jsn['start']
        d_tbl[idx]['order_minute'] = jsn['minute']

        d_tbl[idx]['next_start'] = get_next_start(
                d_tbl[idx]['order_day'], d_tbl[idx]['order_time'])

        d_tbl[idx]['checked'] = True

        g_lg.output("INF", str(d_tbl[idx]))


    chk_list = [one_d.get('checked') for one_d in d_tbl]
    del_list = [i for i, x in enumerate(chk_list) if x == False]

    for idx in reversed(del_list):
        del_d = d_tbl.pop(idx)

        g_lg.output("INF", "削除 " + str(del_d))

    return


def nop():
    return


def get_next_start(order_week, order_hhmm):

    ret_val = None

    n = dtm.now() + tmdlt(seconds = 125)

    if ( (order_week == n.strftime('%a'))
            and (order_hhmm > n.strftime('%H:%M')) ):
        tmp_dtm = dtm(
                n.year, n.month, n.day,
                int(order_hhmm[0:2]), int(order_hhmm[3:5]), 0)
        ret_val = tmp_dtm + tmdlt(minutes = -2)

    else:
        for add_days in range(1, 7 + 8):
            chk_dtm = n + tmdlt(days = add_days)
            if order_week != chk_dtm.strftime('%a'):
                continue
            tmp_dtm = dtm(
                    chk_dtm.year, chk_dtm.month, chk_dtm.day,
                    int(order_hhmm[0:2]), int(order_hhmm[3:5]), 0)
            ret_val = tmp_dtm + tmdlt(minutes = -2)
            break

    return ret_val


def record_start(p_tbl, title, channel, dtm_st, minute):

    p = Process(target=wake_child,
            args=(title, channel, dtm_st, minute,))
    p.daemon = True
    p.start()

    p_tbl.append(p)

    return

def wake_child(title, channel, dtm_st, minute):

    global g_lg;
    g_lg = log.LOG("log", "logfile-" + dtm_st.strftime('%Y%m%d_%H%M%S'))

    filename = channel + "_" + title + "_" + dtm_st.strftime('%Y%m%d_%H%M%S') + ".mp3"
    if channel == "agp":
        filename = channel + "_" + title + "_" + dtm_st.strftime('%Y%m%d_%H%M%S') + ".mp4"
    g_lg.output("dbg", "ファイル名=[" + filename + "]")

    command = "./rec_radiko.sh" \
            + " " + channel \
            + " " + str(minute) \
            + " " + filename
    if channel == "agp":
        command = "./rec_agp.sh" \
                + " " + channel \
                + " " + str(minute) \
                + " " + filename

    g_lg.output("dbg", "コマンド=[" + command + "]")

    result = subprocess.run(command.split())

    g_lg.output("INF", "コマンド実行結果 " + str(result))

    return


if __name__ == '__main__':

    try:
        main()
    except Exception as e:
        if g_lg is not None:
            g_lg.output("ERR", "error " + str(e))
            g_lg.output("ERR", traceback.format_exc())


