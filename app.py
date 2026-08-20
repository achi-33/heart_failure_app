import streamlit as st
import sqlite3
from datetime import timedelta
import pandas as pd

if "page" not in st.session_state:
    st.session_state.page = 1

st.title("心不全 体調管理アプリ🫀")

st.write("""
このアプリは、心不全患者の体調管理をサポートするためのものです。
日々の体調や症状を記録することで、より良い治療や生活の改善に役立てることができます。
""" )

#日付
from datetime import datetime

today = datetime.now().date()
st.write(f"今日の日付📆：{today}")

#体重の入力
st.write("今日の体重を入力してください")
wt = st.number_input("体重（kg）",
                     min_value=0.0,max_value=200.0,value=0.0,
                     step=0.1,format="%.1f")

#血圧の入力
st.write("今日の血圧を入力してください")
bp_input = st.text_input("血圧（例：120/80）", "120/80")
#入力を分割
try:
    systolic_str, diastolic_str = bp_input.split("/")
    systolic = int(systolic_str)
    diastolic = int(diastolic_str)
except ValueError:
    st.error("血圧は『120/80』のように入力してください。")

#脈拍の入力
st.write("今日の脈拍を入力してください")
hr = st.number_input("脈拍（回/分）",
                     min_value=0,max_value=200,value=0,
                     step=1,format="%d")

#息苦しさの入力
st.write("今日の息苦しさの程度を入力してください")
breathing = st.slider("息苦しさの程度（0:なし、5:中程度、10:非常に強い）", 0, 10, 0)

#むくみの入力
st.write("今日のむくみの程度を入力してください")
swelling = st.selectbox("むくみの程度", ["なし", "少しある", "強い"], index=0)

#服薬状況
st.write("今日の服薬状況を入力してください")
medication = st.selectbox("服薬状況", ["飲み忘れなし","一部飲み忘れあり" ,"飲み忘れあり"], index=0)

#ボタン表示
if st.button("1️⃣ データを保存"):

#接続
    conn = sqlite3.connect('health_data.db')

#テーブルの作成
    conn.execute("""CREATE TABLE IF NOT EXISTS health_records(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    wt REAL NOT NULL,
    systolic REAL NOT NULL,
    diastolic REAL NOT NULL,
    hr REAL NOT NULL,
    breathing INTEGER NOT NULL,
    swelling TEXT NOT NULL,
    medication TEXT NOT NULL
    )""")

#日付の取得
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")

#テーブルへ入力
    conn.execute(
    """
    INSERT INTO health_records (date, wt, systolic, diastolic, hr, breathing, swelling, medication)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (today, wt, systolic, diastolic, hr, breathing, swelling, medication)
    )

#終了
    conn.commit()
    conn.close()

    st.success("データを保存しました！")

#改ページし昨日の数値と比較
if st.button("2️⃣ 昨日のデータと比較🔍"):
    st.session_state.page = 2

    from datetime import timedelta
    today = datetime.today()
    yesterday = today - timedelta(days=1)

    today_str = today.strftime("%Y-%m-%d")
    yesterday_str = yesterday.strftime("%Y-%m-%d")

#データベースから昨日のデータを取得
    conn = sqlite3.connect('health_data.db')

    import pandas as pd

    df_yesterday = pd.read_sql_query("""
    SELECT wt, systolic, diastolic, hr, breathing, swelling, medication 
    FROM health_records   
    WHERE date = ?        
    ORDER BY id DESC      
    LIMIT 1               
    """, conn, params=(yesterday_str,))

#データベースから今日のデータを取得
    df_today = pd.read_sql_query("""
    SELECT wt, systolic, diastolic, hr, breathing, swelling, medication 
    FROM health_records
    WHERE date = ?
    ORDER BY id DESC
    LIMIT 1
    """, conn, params=(today_str,))

    conn.close()

#データの取り出し
    if not df_yesterday.empty and not df_today.empty: 
    #昨日のデータが空じゃなくて、今日のデータも空じゃないなら処理を続ける
        wt_yesterday = df_yesterday.iloc[0]['wt']
        systolic_yesterday = df_yesterday.iloc[0]['systolic']
        diastolic_yesterday = df_yesterday.iloc[0]['diastolic']
        hr_yesterday = df_yesterday.iloc[0]['hr']
        breathing_yesterday = df_yesterday.iloc[0]['breathing']
        swelling_yesterday = df_yesterday.iloc[0]['swelling']
        medication_yesterday = df_yesterday.iloc[0]['medication']

        wt_today = df_today.iloc[0]['wt']
        systolic_today = df_today.iloc[0]['systolic']
        diastolic_today = df_today.iloc[0]['diastolic']
        hr_today = df_today.iloc[0]['hr']
        breathing_today = df_today.iloc[0]['breathing']
        swelling_today = df_today.iloc[0]['swelling']
        medication_today = df_today.iloc[0]['medication']

#比較結果の表示
    if df_yesterday.empty and df_today.empty:
        st.error("⚠️昨日と今日のデータが見つかりませんでした。記録を追加してください。")
    elif df_yesterday.empty:
        st.warning("⚠️昨日のデータがありません。昨日の記録を追加すると比較できます。")
    elif df_today.empty:
        st.warning("⚠️今日のデータがありません。今日の記録を追加してください。")
    else:
        st.success("✅昨日と今日のデータを比較します。")

#体重の比較
        st.write(f"昨日の体重: {wt_yesterday} kg, 今日の体重: {wt_today} kg")
        wt_diff = wt_today - wt_yesterday
        if wt_diff > 1:
            st.error(f"⚠️体重が {wt_diff:.1f} kg 増加しています。注意してください。")
        elif wt_diff > 0:
            st.warning("⚠️体重がわずかに増加しています。")
        elif wt_diff == 0:
            st.info("体重の変化はありません。")
        else:
            st.info(f"体重が {abs(wt_diff):.1f} kg 減少しています。")

#血圧の比較
        st.write(f"昨日の血圧: {systolic_yesterday}/{diastolic_yesterday} mmHg", 
             f"今日の血圧: {systolic_today}/{diastolic_today} mmHg")
        #収縮期血圧の比較
        sbp_diff = systolic_today - systolic_yesterday
        if sbp_diff > 0:
            st.warning(f"収縮期血圧が昨日より高いです。")
        elif sbp_diff < 0:
            st.info(f"収縮期血圧が昨日より低いです。")
        else:
            st.info("収縮期血圧の変化はありません。")
        #拡張期血圧の比較
        dbp_diff = diastolic_today - diastolic_yesterday
        if dbp_diff > 0:
            st.warning(f"拡張期血圧が昨日より高いです。")
        elif dbp_diff < 0:
            st.info(f"拡張期血圧が昨日より低いです。")
        else:
            st.info("拡張期血圧の変化はありません。")

#脈拍の比較
        st.write(f"昨日の脈拍: {hr_yesterday} 回/分, 今日の脈拍: {hr_today} 回/分")
        hr_diff = hr_yesterday - hr_today
        if hr_diff > 0:
             st.warning(f"脈拍が昨日より高いです。")
        elif hr_diff < 0:
            st.warning(f"脈拍が昨日より低いです。")
        else:
            st.info("脈拍の変化はありません。")

#息苦しさの比較
        st.write(f"昨日の息苦しさ: {breathing_yesterday}, 今日の息苦しさ: {breathing_today}")
        if breathing_today >= breathing_yesterday:
            st.error(f"⚠️昨日より息苦しさが強くなっています。注意してください。")
        elif breathing_today < breathing_yesterday:
            st.info(f"昨日より息苦しさが改善しました。")
        else:
            st.info("息苦しさの変化はありません。")

#むくみの比較
        st.write(f"昨日のむくみ: {swelling_yesterday}, 今日のむくみ: {swelling_today}")
        if swelling_yesterday in ["少しある" ,"なし"] and swelling_today == "強い":
            st.error(f"⚠️昨日よりむくみが強くなっています。注意してください。")
        elif swelling_yesterday =="強い" and swelling_today in ["なし","少しある"]:
            st.info(f"昨日よりむくみが改善しました。")
        else:
            st.info("むくみの変化はありません。")

#服薬状況の比較
        st.write(f"昨日の服薬状況: {medication_yesterday}, 今日の服薬状況: {medication_today}")
        if medication_yesterday in ["一部飲み忘れあり" ,"飲み忘れあり"] or medication_today in ["一部飲み忘れあり" ,"飲み忘れあり"] :
            st.error(f"⚠️薬の飲み忘れがあります。注意してください。")
        else:
            st.info("問題なく内服できています😊")

#体重、血圧、脈拍の変化をグラフで表示
if st.button("📈 過去1週間の体重・血圧・脈拍の変化をグラフで表示"):

    today = datetime.today()
    start_day = today - timedelta(days=6)

    today_str = today.strftime("%Y-%m-%d")
    start_date_str = start_day.strftime("%Y-%m-%d")

#過去1週間のデータを取得
    conn = sqlite3.connect('health_data.db')

    df_week = pd.read_sql_query("""
            SELECT date, wt, systolic, diastolic, hr
            FROM health_records   
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC            
            """, conn, params=(start_date_str,today_str))

    conn.close()

#グラフ作成
    #日付（文字列）をdateに変換
    df_week["date"] = pd.to_datetime(df_week["date"]).dt.strftime("%m月%d日")
    #dateをインデックスする：X軸に使う
    df_week.set_index("date", inplace=True)

    st.write("📍過去1週間の体重")
    st.line_chart(df_week["wt"])

    st.write("📍過去1週間の血圧")
    st.line_chart(df_week[["systolic", "diastolic"]])

    st.write("📍過去1週間の脈拍")
    st.line_chart(df_week["hr"])

    st.info("👨🏼‍⚕️変化が激しい場合は医師に相談しましょう！")
