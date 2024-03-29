#알수없음
from ast import keyword
# from asyncio import FastChildWatcher
from atexit import register
from distutils.util import rfc822_escape
from glob import glob

#DB모듈
from sqlite3 import connect
from tkinter.ttk import Progressbar
from django import get_version
import pymysql
import sqlite3
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import create_engine
from bs4 import BeautifulSoup

# from test import fetcher
# pyrcc5 test.qrc -o ./test_rc.py
import test_rc

#시스템모듈
import sys
import os
import time
import datetime
import json

#UI모듈
from PyQt5.QtGui import *
from PyQt5 import uic
# from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QDialog, QMainWindow, QApplication, QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5 import QtGui
# from PyQt5 import QtCore, QtGui, QtWidgets
import qdarktheme
from PyQt5.QtCore import Qt, QDate, QCoreApplication, QThread, QTimer, pyqtSignal, QObject, pyqtSlot
# from PyQt5.QtCore import *
#pip install pyqtdarktheme

#부가기능
import webbrowser
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import re, uuid #MAC
import pickle
import csv
import gc
import random

#데이터분석
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings(action='ignore')
# from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, KFold, cross_val_score

#Misc
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import scale, MinMaxScaler

#자연어
import collections
from collections import Counter
from math import gamma

#폰트

#UI파일 연결
UI_Login = uic.loadUiType("Login.ui")[0]
UI_Register = uic.loadUiType("Register.ui")[0]
UI_Find = uic.loadUiType("Find.ui")[0]
UI_Analysis = uic.loadUiType("Analysis Interface.ui")[0]
UI_Keyword = uic.loadUiType("Keyword.ui")[0]
UI_Recommend = uic.loadUiType("Recommend.ui")[0]
UI_Free = uic.loadUiType("Free.ui")[0]

#쓰레드
class Thread1(QThread):
    # user_signal = pyqtSignal()
    #시그널
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    #검색 로직
    def run(self):
        # global start_time
        global time_bool
        global worker_cnt_f
        global item_list
        global item_result
        global item_result_view
        global df
        global check_searching
        global mariadb
        global remain_date
        global remain_count
        
        time_bool = True

        with ThreadPoolExecutor(max_workers=worker_cnt_f) as executor:
            thread_list = []
            for keyword in keyword_list:
                thread_list.append(executor.submit(self.searching, keyword))
            for execution in concurrent.futures.as_completed(thread_list):
                execution.result()
        #비어있으면 종료

        #check DB에서 회원정보 조회
        try:
            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = "SELECT * FROM check_login WHERE mac=%s;"
                cur_user.execute(sql, mac_address)
                check_id = cur_user.fetchall()
                last_date = check_id[0][7]
                last_count = check_id[0][8]
            except:
                con_user.close()

                pass
            finally:
                con_user.commit()
                con_user.close()

            #잔여 일수 체크
            r_now = datetime.datetime.now()
            r_now = r_now.date()
            r_now = ['%04d' % r_now.year, '%02d' % r_now.month,'%02d' % r_now.day]
            r_now = ''.join(r_now)

            if int(last_date) == int(r_now):
                remain_date = last_date
                remain_count = remain_count
            else:
                remain_date = r_now
                remain_count = 25000

            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = f"UPDATE check_login SET last_date='{remain_date}' WHERE id='{db_id}';"
                cur_user.execute(sql)
                sql = f"UPDATE check_login SET last_count='{remain_count}' WHERE id='{db_id}';"
                cur_user.execute(sql)
            except:
                con_user.close()
                pass
            finally:
                con_user.commit()
                con_user.close()
        except:
            pass

        if len(item_list) == 0:
            self.parent.textEdit_box.append("검색된 상품이 없습니다. 다시 시도해주세요.")
            self.parent.pushButton.setEnabled(False)
            time_bool = False
            return

        try:
            #데이터프레임 순위 정렬 및 결측치 제거
            df = pd.DataFrame.from_dict(data=item_list)
            
            #에러잡기
            # writer = pd.ExcelWriter('에러잡기.xlsx', engine = 'xlsxwriter')
            # df.to_excel(writer, index=False, sheet_name = '최종본') 
            # writer.save()

            df.columns = ['No','대분류','중분류','소분류','세분류','카테고리','순위','판매유형','제조국가','상품가격','등록일자','구매_7일','구매','리뷰','찜','문의','평점','스토어명','등급','상품명','상품명_L','옵션','옵션_L','태그','태그_L','URL']
            df = df.drop([0], axis = 0)
            try:
                df = df.loc[df.순위 != '없음']
                print(1)
                df = df.astype({'구매_7일':'str','구매':'str','리뷰':'str','찜':'str','문의':'str'})
                df = df[~(df['구매_7일'].str.contains('수집실패',na=False,case=False)) & ~(df['구매'].str.contains('수집실패',na=False,case=False)) & ~(df['리뷰'].str.contains('수집실패',na=False,case=False)) & ~(df['찜'].str.contains('수집실패',na=False,case=False)) & ~(df['문의'].str.contains('수집실패',na=False,case=False))]
                print(2)
                df = df.astype({'No':'int'})
                df = df.astype({'순위':'int'})
                df.sort_values(by=["No","순위"], ascending=[True,True], inplace=True)
                df.reset_index(drop=True, inplace=True)
                df.loc[df['찜'] == 'None', '찜'] = 0
                df.loc[df['평점'] == 'None', '평점'] = 0
                # df = df.astype({'구매_7일':'int','구매':'int','리뷰':'int','찜':'int','문의':'int'})
                print(3)
                df[['등록일자', '카테고리']].dropna()
                df = df.astype({'판매유형':'str'})
                df = df.astype({'상품가격':'int'})
                df = df.astype({'등록일자':'int'})
                df = df.astype({'구매_7일':'int'})
                df = df.astype({'구매':'int'})
                df = df.astype({'리뷰':'int'})
                df = df.astype({'찜':'int'})
                df = df.astype({'문의':'int'})
                df = df.astype({'카테고리':'int'})
                df = df.astype({'상품명_L':'int'})
                df = df.astype({'옵션_L':'int'})
                df = df.astype({'태그_L':'int'})
            except:
                pass
            try:
                print(4)            #국가/등급/판매유형 변경
                df.loc[df['제조국가'].str.contains('중국|china|CHINA|CN'),'제조국가']='중국'
                df.loc[df['제조국가'].str.contains('미국|멕시코|캐나다|CANADA'),'제조국가']='미국'
                df.loc[df['제조국가'].str.contains('일본|JAPAN|japan'),'제조국가']='일본'
                df.loc[df['제조국가'].str.contains('태국|대만|뉴질랜드'),'제조국가']='기타'
                df.loc[df['제조국가'].str.contains('폴란드|프랑스|유럽|EU|영국|스페인|이탈리아|네덜란드|노르웨이|덴마크|독일}그리스|러시아|스위스'),'제조국가']='유럽'
                df.loc[df['제조국가'].str.contains('국산|국내산|대한민국'),'제조국가']='국내'
                df.loc[~df['제조국가'].str.contains('중국|미국|일본|유럽|국내'),'제조국가']='기타'
                print(5)
                df.loc[df['등급'].str.contains('M44001'),'등급']='플래티넘'
                df.loc[df['등급'].str.contains('M44002'),'등급']='프리미엄'
                df.loc[df['등급'].str.contains('M44003'),'등급']='빅파워'
                df.loc[df['등급'].str.contains('M44004'),'등급']='파워'
                df.loc[df['등급'].str.contains('M44005'),'등급']='새싹'
                df.loc[df['등급'].str.contains('M44006'),'등급']='씨앗'
                df.loc[df['판매유형'].str.contains('0'),'판매유형']='국내'
                df.loc[df['판매유형'].str.contains('1'),'판매유형']='해외'
                print(6)
                #Item Log DB에 회원정보 저장
                m_now = datetime.datetime.now()
                m_now = m_now.date()
                m_noww = ['%04d' % m_now.year, '%02d' % m_now.month,'%02d' % m_now.day]
                m_noww = ''.join(m_noww)
                m_pre = m_now - datetime.timedelta(days=7)
                m_pre = ['%04d' % m_pre.year, '%02d' % m_pre.month,'%02d' % m_pre.day]
                m_pre = ''.join(m_pre)
                # print(m_pre)
            except:
                pass
            try:
                mariadb = df.loc[((df.구매 > 0)| (df.문의 > 0)) & (df.등록일자 > int(m_pre))]
                mariadb.insert(0,'검색일자',m_noww)
                print(7)
                #Item Log DB에 회원정보 저장
                db_connection_str = 'mysql+pymysql://young_write:0000@3.39.22.73/trend'
                db_connection = create_engine(db_connection_str)
                conn = db_connection.connect()
                mariadb.to_sql(name='item_log', con=db_connection, if_exists='append',index=False)
            except:
                pass
            print(8)
            item_result = df
            try:
                #제조국가
                if set_start['전체국가'] == True:
                    df = df.loc[df.제조국가 != '']
                else:
                    if set_start['국내'] == False:
                        df = df.loc[df.제조국가 != '국내']
                    if set_start['중국'] == False:
                        df = df.loc[df.제조국가 != '중국']
                    if set_start['미국'] == False:
                        df = df.loc[df.제조국가 != '미국']
                    if set_start['일본'] == False:
                        df = df.loc[df.제조국가 != '일본']
                    if set_start['유럽'] == False:
                        df = df.loc[df.제조국가 != '유럽']
                    if set_start['기타'] == False:
                        df = df.loc[df.제조국가 != '기타']
                print(9)
                #상품가격
                if set_start['전체가격'] == True:
                    df = df.loc[df.상품가격 != '']
                else:
                    df = df.loc[df.상품가격 >= int(set_start['최저가격'])]
                    df = df.loc[df.상품가격 <= int(set_start['최고가격'])]
                #등록일자
                print(10)
                if set_start['전체기간'] == True:
                    df = df.loc[df.등록일자 != '']
                else:
                    date_min = [str(set_start['시작일자'][0]),str('%02d' % set_start['시작일자'][1]),str('%02d' % set_start['시작일자'][2])]
                    date_min = ''.join(date_min)
                    date_max = [str(set_start['종료일자'][0]),str('%02d' % set_start['종료일자'][1]),str('%02d' % set_start['종료일자'][2])]
                    date_max = ''.join(date_max)
                    df = df.loc[df.등록일자 >= int(date_min)]
                    df = df.loc[df.등록일자 <= int(date_max)]
                #구매7일
                if set_start['구매7일'] == True:
                    df = df.loc[df.구매_7일 != '']
                else:
                    df = df.loc[df.구매_7일 >= int(set_start['구매7일_min'])]
                    df = df.loc[df.구매_7일 <= int(set_start['구매7일_max'])]
                #구매
                if set_start['구매'] == True:
                    df = df.loc[df.구매 != '']
                else:
                    df = df.loc[df.구매 >= int(set_start['구매_min'])]
                    df = df.loc[df.구매 <= int(set_start['구매_max'])]
                #리뷰
                if set_start['리뷰'] == True:
                    df = df.loc[df.리뷰 != '']
                else:
                    df = df.loc[df.리뷰 >= int(set_start['리뷰_min'])]
                    df = df.loc[df.리뷰 <= int(set_start['리뷰_max'])]
                #찜
                if set_start['찜'] == True:
                    df = df.loc[df.찜 != '']
                else:
                    df = df.loc[df.찜 >= int(set_start['찜_min'])]
                    df = df.loc[df.찜 <= int(set_start['찜_max'])]
                #문의
                if set_start['문의'] == True:
                    df = df.loc[df.문의 != '']
                else:
                    df = df.loc[df.문의 >= int(set_start['문의_min'])]
                    df = df.loc[df.문의 <= int(set_start['문의_max'])]
                #몰등급
                if set_start['전체등급'] == True:
                    df = df.loc[df.등급 != '']
                else:
                    if set_start['플래티넘'] == False:
                        df = df.loc[df.등급 != '플래티넘']
                    if set_start['프리미엄'] == False:
                        df = df.loc[df.등급 != '프리미엄']
                    if set_start['빅파워'] == False:
                        df = df.loc[df.등급 != '빅파워']
                    if set_start['파워'] == False:
                        df = df.loc[df.등급 != '파워']
                    if set_start['새싹'] == False:
                        df = df.loc[df.등급 != '새싹']
                        df = df.loc[df.등급 != '씨앗']
            except:
                pass
            item_result_view = df
            #리스트 테이블 채우기        
            print(11)

        except:
            #데이터 오류 찾기
            print("전처리 실패")
            writer = pd.ExcelWriter('전처리 실패.xlsx', engine = 'xlsxwriter')
            df.to_excel(writer, index=False, sheet_name = '오류원인') 
            writer.save()
            self.parent.textEdit_box.append("데이터 오류로 검색이 실패하였습니다.\n현재 데이터를 머슭상품 폴더 안에 엑셀 파일로 저장하였으니 확인해주세요.")
            check_searching = True
            time_bool = False   
            self.parent.pushButton.setEnabled(False)
            print(12)
            return

        try:
            self.parent.progressBar.setValue(100)
            time.sleep(0.1)
            self.parent.textEdit_box.append("검색 소요 시간 : %s초" % int(time.time() - start_time))
            time.sleep(0.1)
            self.parent.textEdit_box.append("검색이 완료되었습니다.")
            time.sleep(0.1)
            self.parent.textEdit_box.append("검색 결과 업데이트 버튼을 클릭하여 검색된 상품을 확인해주세요.")
            time.sleep(0.1)
            self.parent.textEdit_box.append("아래 테이블에는 100개까지만 확인 가능하며, 엑셀 다운로드로 전체 데이터를 확인할 수 있습니다.")
            time.sleep(0.1)
            check_searching = True

            #중지버튼 비활성화
            self.parent.pushButton.setEnabled(False)

            # self.parent.table_result()
        except:
            time_bool = False   

        time_bool = False   
        #시그널
        # self.user_signal.emit()
        # self.parent.user_signal.emit()
    
    def searching(self, keyword):
        global category_num
        global page_num
        global item_list
        global remain_count

        category_num += 1
        category_num_f = category_num
        
        headers = {
            'authority': 'search.shopping.naver.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            # Requests sorts cookies= alphabetically
            # 'cookie': 'NNB=HOU6WFGU3LTGC; AD_SHP_BID=29; ASID=70a87a600000017e8af3e5ac00000062; NaverSuggestUse=use%26unuse; autocomplete=use; nx_ssl=2; _ga=GA1.2.51846183.1642520968; _gid=GA1.2.1517975898.1660920372; _ga_7VKFYR6RV1=GS1.1.1660920372.9.1.1660920636.60.0.0; BMR=s=1660921306789&r=https%3A%2F%2Fm.blog.naver.com%2FPostView.naver%3FisHttpsRedirect%3Dtrue%26blogId%3Drjs5730%26logNo%3D220950201726&r2=https%3A%2F%2Fwww.google.com%2F; _naver_usersession_=GGcKQxpyjRbtRLuN+cSn+w==; sus_val=lay6iY1I3rmp3hI07geHdKcc; nid_inf=1588157468; NID_AUT=tmkhLZVFmC0EgAQX3k7l+AxioZqOYlvJiH44qtLrVQCkTtbE7kh9KEQe34YAK1m4; NID_SES=AAABth/zSphmohq1L8eBCpj89T2FZHIjaOqjb3OmBAGRntwgpIrEfNutxFzlgqQ3NllfoUDW2vUBb8BrzlRxoWNEoY8HV1paR/Q93o8tNwEBDanFSvFwC4MP97cIqLC+GhAt0fBAjvVhVdPlRiD1OV3r61bdepkbvBVoCkjjRE50TAtBrBgDrhmjxMDhbLDIBL8hdaS06uIDK4yTXuUIrBu6iy5UHjbteZO6hU3EJUUwnVOqkBGZFrZrFx51wpU0bU1WM8/gro+rh3BS9P3w79fo1rPH+TvgZH9k/yPhxmRyPPNnQ4I7S0DxibhfnLSdATjlFdLJAzVwv/gWedbVMBSA+a8jsCOY2CS0Yps/WjxcXtJ9qZ8qDOzXDgDil7WmfHeUNWTBBSX4+qfDjDxj3Eu82gfVGlfiBhTwl2tmbkB8AT7BAcYwi+dxo60PFBZTMsM5TWEU5De4mkTBwai/QijIMdrAg+niWTGfe+VQmEBfhKJf70aOWSAK3aE4EF01+vpZfSqZZrYXjjBEtXNyc2hgpdtNsRD6F3ih+WuyzY0JvJ5+7/7UL1DsUOboal7APZ9igIvnnob13r6AKBpe7JDYID8=; NID_JKL=fE5kQGqQDIvOTf0WVZu9UrBCjJaUip0Y2lNH1EPn3cU=; page_uid=hwsb1sp0J1ZssUMSLpZssssstWG-326295; spage_uid=hwsb1sp0J1ZssUMSLpZssssstWG-326295',
            'logic': 'PART',
            'referer': 'https://search.shopping.naver.com/search/category/100002989?agency=true&catId=50003265&frm=NVSHCHK&npayType=2&origQuery&pagingIndex=1&pagingSize=40&productSet=checkout&query&sort=rel&timestamp=&viewType=list',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        }

        cookiess = {
            'NNB': 'HOU6WFGU3LTGC',
            'AD_SHP_BID': '29',
            'ASID': '70a87a600000017e8af3e5ac00000062',
            'NaverSuggestUse': 'use%26unuse',
            'autocomplete': 'use',
            '_ga': 'GA1.2.51846183.1642520968',
            '_ga_7VKFYR6RV1': 'GS1.1.1661101481.12.0.1661101481.60.0.0',
            'nx_ssl': '2',
            'nid_inf': '1560874613',
            'NID_JKL': 'wiEb2ohQZi/BMBqAekak3ecyMl6ZqLSx7ztIrq2+pIA=',
            'CBI_SES': 'I3zlBiuU9ywTN+BkqyVaeLfd2zQNvnRbyHA3FflWjiubpkrLEDJZ65J12hu2aWySYT3ZtHnjaTSLi+aI8zOHgTf7w4ulPUBrxMMIrtihZ1RPj5JHxcsNAKNc8LSkAXzBSOGcNj7RVyJJV7jw5BBo44SaaBTOZuVJpetYAQuNrr9J0evFrALuRh8vmoGPrmlPrSM5G3tmATvbY6VhAfRnB1Twz9NoZ4SuLtJl3SwrMMcnvgGRpuu8RxiTYCgiDrVYUNA/TztneSJEvXqK8rbiY71kw43Jd8aYi6Z3iL9jF7RxZsUyEwZwn2IyQyo32O6IR7uk6MhsfXomcBU0EhQA3IJhGbohysaBEKvqrmhxeHhPO7hXzJr8E6ltwVA+uaGpKq1UTWeMcGJAC77HKjWRj6LTGE/GGX8vSVMF+w0xxTRp8421nMRpaye8lTHzPCX0DAcV5e7LXEeFjttCMySWGg==',
            'CBI_CHK': '"r5V0mf9uRUZHZ/vmLGy3ez7f4/k4aqWXL5o03eN68frU64OUHq3UOf2FsdzamoCMJEOvKgU/6s4Xqol9RmtQqkfwtbDREsF4quRwdxn0vpl5Qa3/CW1KLPfbW5kX0n02ugBfAevdAyxdMOit1sn37AdE3NJk9usprt/iLDI7Pdk="',
            'BMR': 's=1663506479043&r=https%3A%2F%2Fm.blog.naver.com%2FPostView.naver%3FisHttpsRedirect%3Dtrue%26blogId%3Dohgnus56%26logNo%3D221517674547&r2=https%3A%2F%2Fwww.google.com%2F',
            'page_uid': 'hyNkAwprvTossO5YBjKssssstQo-142175',
            'spage_uid': 'hyNkAwprvTossO5YBjKssssstQo-142175',
            'sus_val': 'I41keoZlRAiDTeFWkGrWgy00',
        }

        headerss = {
            'authority': 'search.shopping.naver.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            # Requests sorts cookies= alphabetically
            # 'cookie': 'NNB=HOU6WFGU3LTGC; AD_SHP_BID=29; ASID=70a87a600000017e8af3e5ac00000062; NaverSuggestUse=use%26unuse; autocomplete=use; _ga=GA1.2.51846183.1642520968; _ga_7VKFYR6RV1=GS1.1.1661101481.12.0.1661101481.60.0.0; nx_ssl=2; nid_inf=1560874613; NID_JKL=wiEb2ohQZi/BMBqAekak3ecyMl6ZqLSx7ztIrq2+pIA=; CBI_SES=I3zlBiuU9ywTN+BkqyVaeLfd2zQNvnRbyHA3FflWjiubpkrLEDJZ65J12hu2aWySYT3ZtHnjaTSLi+aI8zOHgTf7w4ulPUBrxMMIrtihZ1RPj5JHxcsNAKNc8LSkAXzBSOGcNj7RVyJJV7jw5BBo44SaaBTOZuVJpetYAQuNrr9J0evFrALuRh8vmoGPrmlPrSM5G3tmATvbY6VhAfRnB1Twz9NoZ4SuLtJl3SwrMMcnvgGRpuu8RxiTYCgiDrVYUNA/TztneSJEvXqK8rbiY71kw43Jd8aYi6Z3iL9jF7RxZsUyEwZwn2IyQyo32O6IR7uk6MhsfXomcBU0EhQA3IJhGbohysaBEKvqrmhxeHhPO7hXzJr8E6ltwVA+uaGpKq1UTWeMcGJAC77HKjWRj6LTGE/GGX8vSVMF+w0xxTRp8421nMRpaye8lTHzPCX0DAcV5e7LXEeFjttCMySWGg==; CBI_CHK="r5V0mf9uRUZHZ/vmLGy3ez7f4/k4aqWXL5o03eN68frU64OUHq3UOf2FsdzamoCMJEOvKgU/6s4Xqol9RmtQqkfwtbDREsF4quRwdxn0vpl5Qa3/CW1KLPfbW5kX0n02ugBfAevdAyxdMOit1sn37AdE3NJk9usprt/iLDI7Pdk="; BMR=s=1663506479043&r=https%3A%2F%2Fm.blog.naver.com%2FPostView.naver%3FisHttpsRedirect%3Dtrue%26blogId%3Dohgnus56%26logNo%3D221517674547&r2=https%3A%2F%2Fwww.google.com%2F; page_uid=hyNkAwprvTossO5YBjKssssstQo-142175; spage_uid=hyNkAwprvTossO5YBjKssssstQo-142175; sus_val=I41keoZlRAiDTeFWkGrWgy00',
            'logic': 'PART',
            'referer': 'https://search.shopping.naver.com/search/category/100000402?agency=true&catId=50000790%2050000666&frm=NVSHCHK&npayType=2&origQuery&pagingIndex=1&pagingSize=80&productSet=checkout&query&sort=rel&timestamp=&viewType=list',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        }

        #판매유형 선택
        if set_start['전체유형'] == True:
            agency = ''
            exagency = ''
        elif set_start['국내상품'] == True:
            agency = ''
            exagency = 'true'        
        elif set_start['해외직구'] == True:
            agency = 'true'
            exagency = ''

        #페이지별로 검색    
        for page in range(int(set_start['수집_min']), int(set_start['수집_max'])+1):
            if stop_bool == True:
                # print(str(keyword) + ' 카테고리, ' + str(page) + ' 페이지')
                page_num += 1
                remain_count -= 1

                params = {
                    'sort': 'rel',
                    'pagingIndex': page,
                    'pagingSize': '80',
                    'viewType': 'list',
                    'productSet': 'checkout',
                    'catId': keyword,
                    'spec': '',
                    'agency': agency,
                    'deliveryFee': '',
                    'deliveryTypeValue': '',
                    'frm': 'NVSHCHK',
                    'iq': '',
                    'eq': '',
                    'xq': '',
                    'exagency': exagency,
                    'npayType': '2'
                }

                try:
                    itemlist = requests.get('https://search.shopping.naver.com/api/search/category/'+keyword, params=params, headers=headers).json()
                except:
                    # print("requsets 불가 오류")
                    time.sleep(1)
                    break
                total = str(itemlist['shoppingResult']['total'])
                
                rank = '없음'

                try:
                    for i in itemlist['shoppingResult']['products']:
                        # time.sleep(0.1)
                        if stop_bool == True:
                            category1Name = '없음'
                            category2Name = '없음'
                            category3Name = '없음'
                            category4Name = '없음'
                            detail_purchase = "0"
                            # detail_purchase = "수집실패"
                            # cumulationSaleCount = "수집실패"
                            commentCount = "수집실패"
                            viewAttributes = "수집실패"
                            sellerTags = ""
                            rank = '없음'
                            mallProductUrl = "수집실패"

                            try:
                                mallPcUrl = str(i['mallPcUrl'])
                                smart = str('https://smart')
                                if mallPcUrl[0:13] == smart:
                                    title = str(i['productTitle'])
                                    mallProductId = i['mallProductId']
                                    mallName = i['mallName']
                                    rank = i['rank']
                                    # rank_set = i['rank']
                                    purchaseCnt = int(i['purchaseCnt'])
                                    reviewCount = i['reviewCount']
                                    openDate = int(i['openDate'])
                                    keepCnt = i['keepCnt']
                                    smart = str('https://smart')
                                    overseaTp = i['overseaTp']
                                    mallProductUrl = i['mallProductId']
                                    mallProductUrl = i['mallProdMblUrl']
                                    mallProductUrl = i['mallProductUrl']
                                    scoreInfo = i['scoreInfo']
                                    characterValue = i['characterValue']
                                    manuTag = i['manuTag']
                                    mallName = i['mallName']
                                    mobilePrice = i['mobilePrice']
                                    category1Name = i['category1Name']
                                    category2Name = i['category2Name']
                                    category3Name = i['category3Name']
                                    category4Name = i['category4Name']
                                    chnlSeq = i['chnlSeq']
                                    
                                    openDate = (i['openDate'])
                                    openDate = openDate[0:8]

                                    regDate = openDate

                                    detail_item = requests.get('https://smartstore.naver.com/i/v1/stores/'+chnlSeq+'/products/'+mallProductId, cookies=cookiess, headers=headerss).json()
                                    #수집 불가 에러 방지 목적의 타임슬립
                                    # time.sleep(0.1)
                                    try:
                                        for t in detail_item['sellerTags']:
                                            sellerTag = t['text']
                                            sellerTags += sellerTag + ','
                                            manuTag = sellerTags[:-1]
                                    except:
                                        pass
                                    
                                    try:
                                        #7일간 구매수 크롤링
                                        headersss = {
                                            'authority': 'm.smartstore.naver.com',
                                            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                                            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                                            'cache-control': 'max-age=0',
                                            # 'cookie': 'NA_CO=ct%3Dlfgv52w8%7Cci%3D8e43e521f69d2364cb1cc27b79fe5f498f51ced7%7Ctr%3Dslsl%7Chk%3D252d1ce025c4137da085e68ccd75914143842b49%7Ctrx%3Dundefined; wcs_bt=s_12579650cc372:1679319830; NNB=IUOPSJJ34MIWI; ASID=af75d55900000186e5eab73f0000005e; nx_ssl=2; nid_inf=1191992439; NID_AUT=qu70717cXCLPY2bPn22m1eOSccs53kQunE4BcQBY8mhIwxhVf6muDXbZJF2bgCiK; NID_JKL=3+NN6sYgR/6BwnSbzldz4Ot/2m738T871YQnD0Cc4Rs=; NID_SES=AAABzGj/5AU8YD4zrfRvaqsHwSizvGAIuZWdYTE/ZHO7wvRMmoEiLYtz1RWYQgRPTKVNugecUH+4ZyohKPwHI0e+nqciQFhtrToRckagcbMWi2Ap/sdtxllbqScksFeZ+I6jO1WhJiMEehZjVCJ8A7z7Kb2yb+691VGPlwWJnuXIcn9EQGSTqnpHjXlzAwo0tgWRkh/kyS0xtIMJ+fBY4k1nsWAhqCf0F35ByaJTUPrub34b2raiLI64lC21b6g63xPPKxa/6Bwz35ZgFsTA8HwBex1w3tSjXB+7z1HA3ikqMpFSCc1XtkNiGQO5HHx+E1ADQJrRKr5GewmzgDPlPceYLtJzDS7ncZJm9kbdDEO+kejQZvYgucJV/osDC6bYTqgb+WAh8KoniORC/J8FgbbnGW36eDnpEyKyxDXB8//sJJlZQDjM67YWgIT+ynRfR5qlmLCQWByVNrUOGp6r2VMcxvoCc0wAjjajsrn7CNHtvVCvk0uR2UbrsDQJqye8PQYZkYYIY8ek+Q2seqVhwa/dFiqdcq3UAMvKDUNZbWYnAM5j1ZCRQU3wMqnWy7uYcxompze0+fohz9yKwA8rCgoKe9/JEoZGCzuOoLdfRDswxt6a; page_uid=itmmJlp0J1ZssPA34H4ssssssP8-256121',
                                            'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
                                            'sec-ch-ua-mobile': '?1',
                                            'sec-ch-ua-platform': '"Android"',
                                            'sec-fetch-dest': 'document',
                                            'sec-fetch-mode': 'navigate',
                                            'sec-fetch-site': 'same-site',
                                            'sec-fetch-user': '?1',
                                            'upgrade-insecure-requests': '1',
                                            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
                                        }

                                        seven_detail = requests.get(
                                            'https://smartstore.naver.com/main/products/'+mallProductId,
                                            # params=params,
                                            # cookies=cookies,
                                            headers=headersss,
                                        )

                                        soup = BeautifulSoup(seven_detail.text, 'html.parser') 
                                        # print(soup)

                                        a = soup.select('em._1vZLzdf7am strong')
                                        # print(a)
                                        numbers = re.findall(r'\d+', str(a))
                                        numbers = list(map(int, numbers))
                                        numbers = sum(numbers)

                                        if purchaseCnt < numbers:
                                            detail_purchase = 0
                                        else:
                                            detail_purchase = numbers

                                    except:
                                        detail_purchase = 0
                                        pass

                                    # detail_purchase = detail_item['saleAmount']['recentSaleCount']
                                    commentCount = detail_item['commentCount']
                                    viewAttributes = detail_item['viewAttributes']['원산지']
                                    # regDate = detail_item['regDate']
                                    # regDate = regDate[0:10]
                                    # regDate = re.sub('-','',regDate)

                                    itemup = [
                                    str(category_num_f),
                                    str(category1Name),
                                    str(category2Name),
                                    str(category3Name),
                                    str(category4Name),
                                    str(keyword),
                                    str(rank),
                                    str(overseaTp),
                                    str(viewAttributes),
                                    str(mobilePrice),
                                    str(regDate),
                                    str(detail_purchase),
                                    str(purchaseCnt),
                                    str(reviewCount),
                                    str(keepCnt),
                                    str(commentCount),
                                    str(scoreInfo),
                                    str(mallName),
                                    str(i['mallInfoCache']['mallGrade']),
                                    str(title),
                                    str(len(title)),
                                    str(characterValue),
                                    str(len(characterValue)),
                                    str(manuTag),
                                    str(len(manuTag)),
                                    str(mallProductUrl)
                                    ]

                                    # print(itemup)
                                    item_list.append(itemup)
                                else:
                                    pass
                                
                            except:
                                # print(str(keyword) + '의 ' + str(page) + '페이지, ' + str(rank) + "순위에서 상품수집 에러")
                                pass
                        else:
                            return
                            # break
                except:
                    # print(str(keyword) + '의 ' + str(page) + '페이지에서 에러')
                    break

            else:
                return
                # break
        else:
            return

    def stop(self):
        global stop_bool
        stop_bool = False
        # self.quit()
        # self.wait(1000)

#쓰레드2
class Thread2(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    #필터링 로직
    def run(self):
        global start_time
        global time_bool_filtering
        global df
        global df_filter
        global stop_bool
        global check_filtering
        time_bool_filtering = True
        try:
            if stop_bool == True:
                #금지어 데이터프레임
                df_filter = df.loc[df['상품명'].str.contains(filter_list)]
                # print(df_filter)
                #필터링 데이터프레임
                df = df.loc[~df['상품명'].str.contains(filter_list)]
                # print(df)
                time_bool_filtering = False   
            else:
                time_bool_filtering = False
                return
        except:
            self.parent.textEdit_box.append("데이터 오류로 검색이 실패하였습니다. 다시 시도해주세요.")
            time_bool_filtering = False
        time.sleep(0.1)
        #필터링 에러 방지
        
        try:
            time.sleep(0.1)
            self.parent.progressBar.setValue(100)
            time.sleep(0.1)
            self.parent.textEdit_box.append("금지어 필터링 소요 시간 : %s초" % int(time.time() - start_time))
            time.sleep(0.1)
            self.parent.textEdit_box.append("금지어 필터링이 완료되었습니다.")
            time.sleep(0.1)
            #중지버튼 비활성화
            self.parent.pushButton.setEnabled(False)
            time.sleep(0.1)

            # self.parent.table_result_filtering()
        except:
            check_filtering = True
            
        check_filtering = True

#쓰레드3
class Thread3(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    #카테고리 로직
    def run(self):
        global start_time
        global time_bool_category
        global item_category
        global stop_bool
        global item_result
        global category_all
        global category_cnt
        global check_category
        time_bool_category = True
        try:
            if stop_bool == True:
                ai_date = datetime.datetime.now()
                ai_date = ai_date.date()
                ai_date_n = ['%04d' % ai_date.year, '%02d' % ai_date.month,'%02d' % ai_date.day]
                ai_date_n = ''.join(ai_date_n)
                # print(ai_date_n)
                ai_date = ai_date - datetime.timedelta(days=30)
                ai_date = ['%04d' % ai_date.year, '%02d' % ai_date.month,'%02d' % ai_date.day]
                ai_date_p = ''.join(ai_date)
                # print(ai_date_p)
                print(1)
                #카테고리추천
                # item_result = pd.read_excel('./aaa.xlsx', engine='openpyxl')
                #중복카테고리 다 제거한 데이터프레임 생성
                item_category = item_result.drop_duplicates(['카테고리'], ignore_index=True)
                item_category = item_category[['No','대분류','중분류','소분류','세분류','카테고리']]
                item_category.insert(6,'구매상품수_1개월','-')
                item_category.insert(7,'등록상품수_1개월','-')
                item_category.insert(8,'구매/등록','-')
                item_category.insert(9,'경쟁강도_AI','-')
                item_category.insert(10,'상품명 키워드 추천','-')
                item_category.insert(11,'태그명 키워드 추천','-')
                # print(item_category)
                print(2)

                #원핫인코딩
                item_result.loc[item_result['구매'] < 1, '구매'] = 0
                item_result.loc[item_result['구매'] != 0, '구매'] = 1
                item_result.loc[item_result['찜'] == 0, '찜'] = 0
                item_result.loc[item_result['찜'] != 0, '찜'] = 1
                item_result.loc[item_result['문의'] == 0, '문의'] = 0
                item_result.loc[item_result['문의'] != 0, '문의'] = 1
                item_result.loc[item_result['옵션_L'] == '', '옵션_L'] = 0
                item_result.loc[item_result['옵션_L'] != '', '옵션_L'] = 1
                item_result.loc[item_result['태그_L'] == '', '태그_L'] = 0
                item_result.loc[item_result['태그_L'] != '', '태그_L'] = 1
                item_result = item_result[['카테고리','순위','등록일자','구매','찜','문의','상품명','옵션_L','태그','태그_L']]
                item_result = item_result.astype({'카테고리':'int','순위':'int','등록일자':'int','구매':'int','찜':'int','문의':'int','옵션_L':'int','태그_L':'int'})
                # print(item_result)
                print(3)

                #테스트 데이터프레임 생성
                item_predict = pd.DataFrame({'순위':[1000],
                                            '등록일자':[ai_date_n],
                                            '구매':[0],
                                            '찜':[0],
                                            '문의':[0],
                                            '옵션_L':[0],
                                            '태그_L':[0]})
                # print(item_predict)
                ac_category = list(item_category['카테고리'])
                category_all = len(ac_category)
                print(4)
########################################################1,2,3,4 없애기 테스트용도#######################
                for idx, category in enumerate(ac_category):
                    if stop_bool == True:
                        category_cnt += 1
                        try:
                            ac_category = (item_result.카테고리 == category)
                            ac_date = (item_result.등록일자 > int(ai_date_p))
                            ac_df = item_result.loc[ac_category & ac_date, ['순위', '등록일자', '구매', '찜', '문의', '옵션_L', '태그_L']]
                            ac_pur = sum(list(ac_df['구매']))
                            ac_app = len(list(ac_df['구매']))

                            #머신러닝
                            item_predict.loc[0, '등록일자'] = int(ac_df['등록일자'].max())
                            item_predict.loc[0, '순위'] = int(ac_df['순위'].max()/2)

                            x_train = ac_df.drop(['구매'], axis=1)
                            y_train = ac_df['구매']
                            x_test = item_predict.drop(['구매'], axis=1)
                            y_test = item_predict['구매']

                            # scaler = MinMaxScaler()
                            # scaler.fit(x_train)
                            # scaler.fit(x_test)

                            # x_train = scaler.transform(x_train)
                            # x_test = scaler.transform(x_test)

                            # kf = KFold(n_splits=10, random_state=1, shuffle=True)

                            # def rmsle(y_test, y_pred):
                            #     return np.sqrt(mean_squared_error(y_test, y_pred))
                            # def cv_rmse(model, x_train=x_train):
                            #     rmse = np.sqrt(-cross_val_score(model, x_train, y_train, scoings='meg_mean_squared_error', cv=kf))

                            rf = RandomForestRegressor(n_estimators=400,
                                                        max_depth=12,
                                                        min_samples_leaf=8,
                                                        min_samples_split=8,
                                                        random_state=0,
                                                        n_jobs=1)

                            random_forest = rf.fit(x_train, y_train)
                            # ac_result = xgb_model_full_data.predict(x_test)
                            ac_result = '%0.4f' % float(random_forest.predict(x_test))
                            ac_sum = '%0.4f' % float(ac_pur/ac_app)
                        except:
                            ac_pur = '상품부족'
                            ac_app = '-'
                            ac_sum = '-'
                            ac_result = '-'
                        finally:
                            item_category.loc[idx, '구매상품수_1개월'] = ac_pur
                            item_category.loc[idx, '등록상품수_1개월'] = ac_app
                            item_category.loc[idx, '구매/등록'] = ac_sum
                            item_category.loc[idx, '경쟁강도_AI'] = ac_result
                    else:
                        time_bool_category = False
                        return

                # print(item_category)
                time_bool_category = False

            else:
                time_bool_category = False
                return
        except:
            self.parent.textEdit_box.append("데이터 오류로 검색이 실패하였습니다. 다시 시도해주세요.")
            time_bool_category = False
            ("오류발생")

        time.sleep(0.1)

        #필터링 에러 방지
        try:
            time.sleep(0.1)
            self.parent.progressBar.setValue(100)
            time.sleep(0.1)
            self.parent.textEdit_box.append("AI 카테고리 추천 소요 시간 : %s초" % int(time.time() - start_time))
            time.sleep(0.1)
            self.parent.textEdit_box.append("AI 카테고리 추천이 완료되었습니다.")
            #중지버튼 비활성화
            time.sleep(0.1)
            self.parent.pushButton.setEnabled(False)
            time.sleep(0.1)
            # self.parent.table_result_category()
        except:
            check_category = True
            
        check_category = True

#쓰레드4
class Thread4(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    #필터링 로직
    def run(self):
        global start_time
        global time_bool_product
        global item_category
        global stop_bool
        global item_result
        global product_all
        global product_cnt
        global check_product
        time_bool_product = True
        try:
            if stop_bool == True:
                #상품추천
                ai_date = datetime.datetime.now()
                ai_date = ai_date.date()
                ai_date = ai_date - datetime.timedelta(days=90)
                ai_date = ['%04d' % ai_date.year, '%02d' % ai_date.month,'%02d' % ai_date.day]
                ai_date_pp = ''.join(ai_date)
                # print(ai_date_pp)
                ai_category = list(item_category['카테고리'])
                product_all = len(ai_category)
                
                for idx, category in enumerate(ai_category):
                    if stop_bool == True:
                        product_cnt += 1
                        try:
                            item_result = item_result.astype({'등록일자':'int'})
                            ai_category = (item_result.카테고리 == category)
                            ai_date = (item_result.등록일자 > int(ai_date_pp))
                            ai_pur = (item_result.구매 != 0)
                            ai_zzim = (item_result.찜 != 0)
                            ai_con = (item_result.문의 != 0)
                            ai_df = item_result.loc[ai_category & ai_date & (ai_pur | ai_zzim | ai_con), ['상품명', '태그']]
                            # print(ai_df)
                            ai_title = ai_df['상품명'].tolist()
                            ai_title = ' '.join(map(str, ai_title))
                            ai_tag = ai_df['태그']
                            ai_tag = ai_tag.dropna(axis=0)
                            ai_tag = ai_tag.tolist()

                            ai_tag = ' '.join(map(str, ai_tag))
                            ai_title = ai_title.split(' ')
                            ai_tag = ai_tag.split(',')

                            ai_title_list = collections.Counter(ai_title)
                            ai_tag_list = collections.Counter(ai_tag)
                            ai_title_most = ai_title_list.most_common(10)
                            ai_tag_most = ai_tag_list.most_common(10)
                            ai_title_list = {}
                            ai_tag_list = {}
                            for n, c in ai_title_most:
                                ai_title_list[n] = c
                            for n, c in ai_tag_most:
                                ai_tag_list[n] = c
                            ai_title_list = ' '.join(map(str, ai_title_list.keys()))
                            ai_tag_list = ' '.join(map(str, ai_tag_list.keys()))
                        except:
                            ai_title_list = '상품부족'
                            ai_title_most = '-'
                        
                        finally:
                            item_category.loc[idx, '상품명 키워드 추천'] = ai_title_list
                            item_category.loc[idx, '태그명 키워드 추천'] = ai_tag_list
                    else:
                        time_bool_product = False
                        return

                time_bool_product = False

            else:
                time_bool_product = False
                return
        except:
            self.parent.textEdit_box.append("데이터 오류로 검색이 실패하였습니다. 다시 시도해주세요.")
            time_bool_product = False
            ("오류발생")

        time.sleep(0.1)

        try:
            time.sleep(0.1)
            self.parent.progressBar.setValue(100)
            time.sleep(0.1)
            self.parent.textEdit_box.append("AI 상품 추천 소요 시간 : %s초" % int(time.time() - start_time))
            time.sleep(0.1)
            self.parent.textEdit_box.append("AI 상품 추천이 완료되었습니다.")
            time.sleep(0.1)
            #중지버튼 비활성화
            self.parent.pushButton.setEnabled(False)
            time.sleep(0.1)

            # self.parent.table_result_product()
        except:
            check_product = True
            
        check_product = True

#쓰레드5
class Thread5(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    #필터링 로직
    def run(self):
        global df
        global df_filter
        global item_category
        global check_searching
        global check_filtering
        global check_category
        global check_product
        global time_bool_download
        global file_name

        time_bool_download = True
        self.parent.textEdit_box.append("엑셀 다운로드가 시작되었습니다.\n폴더가 열릴 때까지 잠시 기다리신 후 파일을 열어 확인해주세요.")
        writer = pd.ExcelWriter(file_name[0], engine = 'xlsxwriter')
        if check_searching == True:
            try:
                df.to_excel(writer, index=False, sheet_name = '최종본') 
            except:
                pass
        if check_filtering == True:
            try:
                df_filter.to_excel(writer, index=False, sheet_name = '금지어')
            except:
                pass
        if check_category == True:
            try:
                item_category.to_excel(writer, index=False, sheet_name = 'AI 추천')
            except:
                pass
        time.sleep(0.1)
        writer.save()
        time.sleep(0.1)
        os.startfile(os.path.dirname(file_name[0]))
        time.sleep(0.1)
        self.parent.textEdit_box.append("엑셀 다운로드가 완료되었습니다.")
        time_bool_download = False


#로그인 인터페이스
class Window_Login(QDialog, UI_Login):

    #기본 설정
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.get_mac() #mac 확인
        self.get_date() #오늘날짜 확인
        self.get_worker() #worker 확인
        self.make_sqllite() #sqllite 연동
        self.get_news()
        self.initUI()
        self.show()
    
    #실행 설정
    def initUI(self):
        self.setWindowTitle("머슭상품")
        app.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet(qdarktheme.load_stylesheet("light"))

        #로그인 정보 불러오기
        try:
            self.lineEdit_id.setText(save_login[0])
            self.lineEdit_password.setText(save_login[1])
        except:
            pass

        self.tableWidget_news.cellClicked.connect(self.get_news_click)
 
    #공지사항 클릭
    def get_news_click(self):
        row = self.tableWidget_news.currentIndex().row()
        column = self.tableWidget_news.currentIndex().column()
        if column == 1:
            webbrowser.open(url=news_list[row][3])
        else:
            pass
        
    #공지사항 확인
    def get_news(self):
        global news_list
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT * FROM news_list;"
            cur_user.execute(sql)
            news_list = cur_user.fetchall()
        except:
            pass
        finally:
            con_user.commit()
            con_user.close()

        try:
            self.tableWidget_news.setRowCount(len(news_list))
            for i in range(len(news_list)):
                for j in range(2):
                    self.tableWidget_news.setItem(i,j,QTableWidgetItem(news_list[i][j+1]))
            self.tableWidget_news.repaint()
        except:
            pass

    #최신버젼
    def get_version(self):
        msg = QMessageBox() #메시지 알림 박스
        global check_run
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            #프로그램 버젼 확인
            sql = "SELECT * FROM version WHERE name=%s;"
            cur_user.execute(sql, 'V5')
            check_version = cur_user.fetchall()
            check_run = check_version[0][2]
            # print(check_run)
        except:
            msg.setWindowTitle('알림')
            msg.setText('버젼 확인이 실패하였습니다.\n관리자에게 문의하세요.')
            msg.exec_()
        finally:
            con_user.commit()
            con_user.close()

    #분석 화면 이동
    def login_lnterface(self):
        global db_id
        global db_password
        global db_mac
        global db_premium
        global remain_date
        global remain_count

        msg = QMessageBox() #메시지 알림 박스

        login_id = self.lineEdit_id.text()
        login_password = self.lineEdit_password.text()
        login_save_check = self.checkBox_login.isChecked()

        #최신버젼
        self.get_version()
        if check_run != 1:
            msg.setWindowTitle('알림')
            msg.setText('우측 공지사항을 통해 최신 버젼을 다운로드해주세요.')
            msg.exec_()
            return

        #아이디와 비밀번호 입력 여부 확인
        if login_id == '':
            msg.setWindowTitle('알림')
            msg.setText('아이디를 입력해주세요.')
            msg.exec_()
            return
        elif login_password == '':
            msg.setWindowTitle('알림')
            msg.setText('비밀번호를 입력해주세요.')
            msg.exec_()
            return
        else:
            #check DB에서 회원정보 조회
            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                # sql = "SELECT * FROM check_login WHERE mac=%s AND id={login_id};"
                sql = f"SELECT * FROM check_login WHERE mac='{mac_address}' AND id='{login_id}';"
                cur_user.execute(sql)
                # cur_user.execute(sql, mac_address)
                check_id = cur_user.fetchall()
                db_id = check_id[0][1]
                db_password = check_id[0][2]
                db_mac = check_id[0][3]
                db_premium = check_id[0][4]
                last_date = check_id[0][7]
                last_count = check_id[0][8]
            except:
                msg.setWindowTitle('알림')
                msg.setText('신규 회원가입을 진행해주시거나\n회원가입을 진행했던 PC에서 로그인을 시도해주세요.')
                msg.exec_()
                # con_user.commit()
                con_user.close()
                return

            finally:
                con_user.commit()
                con_user.close()

        if login_id != db_id:
            msg.setWindowTitle('알림')
            msg.setText('아이디가 일치하지 않습니다.\n아래의 계정찾기를 통해 ID를 확인해주세요.')
            msg.exec_()
            return
        elif login_password != db_password:
            msg.setWindowTitle('알림')
            msg.setText('비밀번호가 일치하지 않습니다.\n우측 공지사항을 확인하여 비밀번호를 찾아주세요.')
            msg.exec_()
            return
        else:
            #로그인 정보 저장 체크 시 sqlite db에 저장
            if login_save_check == True:
                try: #sqllite 로그인 db 조회
                    connect_sqllite = sqlite3.connect(".\login.db");
                    cursor_sqllite = connect_sqllite.cursor();
                    cursor_sqllite.execute("DELETE FROM LOGIN_TABLE");
                    sql = "INSERT INTO LOGIN_TABLE VALUES(?,?)"
                    cursor_sqllite.execute(sql,(login_id,login_password));
                finally: #DB 저장 후 닫기
                    connect_sqllite.commit();
                    connect_sqllite.close();
            #로그인 정보 저장 체크 안할 시 sqlite db 데이터 삭제    
            elif login_save_check == False:
                try: #sqllite 로그인 db 조회
                    connect_sqllite = sqlite3.connect(".\login.db");
                    cursor_sqllite = connect_sqllite.cursor();
                    cursor_sqllite.execute("DELETE FROM LOGIN_TABLE");
                finally: #DB 저장 후 닫기
                    connect_sqllite.commit();
                    connect_sqllite.close();

            #잔여 일수 체크
            r_now = datetime.datetime.now()
            r_now = r_now.date()
            r_now = ['%04d' % r_now.year, '%02d' % r_now.month,'%02d' % r_now.day]
            r_now = ''.join(r_now)

            if last_date == r_now:
                remain_date = last_date
                remain_count = last_count
            else:
                remain_date = r_now
                remain_count = 25000

            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = f"UPDATE check_login SET last_date='{remain_date}' WHERE id='{db_id}';"
                cur_user.execute(sql)
                sql = f"UPDATE check_login SET last_count='{remain_count}' WHERE id='{db_id}';"
                cur_user.execute(sql)
            except:
                con_user.close()
                return
            finally:
                con_user.commit()
                con_user.close()

            self.main = Window_Analysis()
            self.hide()

    #계정 찾기 화면 이동
    def find_lnterface(self):
        self.main = Window_Find()
        
    #회원가입 화면 이동
    def register_lnterface(self):
        msg = QMessageBox() #메시지 알림 박스
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT * FROM check_login WHERE mac=%s;"
            cur_user.execute(sql, mac_address)
            check_id = cur_user.fetchall()
            check_cnt = check_id[0]
        except:
            self.main = Window_Register()
        try:
            if check_cnt != '':
                msg.setWindowTitle('알림')
                msg.setText('이미 해당 PC에서 가입을 진행하였습니다.\n아래의 계정찾기를 통해 ID를 확인해주세요.')
                msg.exec_()
        except:
            return

    #MAC주소
    def get_mac(self):
        global mac_address
        mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

    #오늘날짜
    def get_date(self):
        global register_date
        global premium_date
        global dt_now
        dt_now = datetime.datetime.now()
        register_date = dt_now.date()
        dt_pre = dt_now + datetime.timedelta(days=7)
        premium_date = dt_pre.date()

    #Worker
    def get_worker(self):
        global worker_cnt
        executor = ThreadPoolExecutor()
        worker_cnt = executor._max_workers

    #sqllite DB생성
    def make_sqllite(self):
        global save_login

        try: #sqllite 로그인 db 조회
            connect_sqllite = sqlite3.connect(".\login.db");
            cursor_sqllite = connect_sqllite.cursor();
            cursor_sqllite.execute("SELECT * FROM LOGIN_TABLE");
            #sqlite 저장된 로그인 정보 불러오기
            save_login = cursor_sqllite.fetchone()

        except: #sqllite 로그인 db 생성
            connect_sqllite = sqlite3.connect(".\login.db");
            cursor_sqllite = connect_sqllite.cursor();
            cursor_sqllite.execute("CREATE TABLE LOGIN_TABLE(id TEXT, password TEXT)");
        finally: #DB 저장 후 닫기
            connect_sqllite.commit();
            connect_sqllite.close();

    #프로그램 종료
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '확인', '이 프로그램을 종료하시겠습니까?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class Window_Register(QDialog, UI_Register):
    global check_id
    global check_password
    check_id = 1 #아이디 체크여부 0이면 Pass, 1이면 Fail
    check_password = 1 #비밀번호 체크여부 0이면 Pass, 1이면 Fail

    #기본 설정
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.show()
    
    #실행 설정
    def initUI(self):
        self.setWindowTitle("머슭상품")
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet(qdarktheme.load_stylesheet("light"))

        #아이디 입력 시 중복확인 활성화
        self.lineEdit_register_id.textChanged.connect(self.check_id_button)
        self.lineEdit_register_pass1.textChanged.connect(self.check_password_button)
        self.lineEdit_register_pass2.textChanged.connect(self.check_password_button)
        self.lineEdit_register_mac.setText(mac_address)

    #중복체크 활성화
    def check_id_button(self):
        self.pushButton_check.setEnabled(True)

    #아이디 중복체크
    def id_same_check(self):
        global register_id
        global check_id
        register_id = self.lineEdit_register_id.text()

        msg = QMessageBox()

        if register_id == '':
            msg.setWindowTitle('알림')
            msg.setText('아이디를 입력해주세요.')
            msg.exec_()
            return

        #DB에서 아이디 조회
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT IF( EXISTS( SELECT * FROM check_login WHERE id=%s), 1, 0);"
            cur_user.execute(sql, register_id)
            check_id = cur_user.fetchall()
            check_id = check_id[0][0]
        finally:
            con_user.commit()
            con_user.close()

        # print(check_id)

        if check_id == 1:
            msg.setWindowTitle('알림')
            msg.setText('이미 존재하는 아이디입니다.')
            msg.exec_()

        elif check_id == 0:
            msg.setWindowTitle('알림')
            msg.setText('사용 가능한 아이디입니다.')
            msg.exec_()
            self.pushButton_check.setEnabled(False)

    #비밀번호 일치 확인
    def check_password_button(self):
        global check_password
        global register_pass1
        global register_pass2

        register_pass1 = self.lineEdit_register_pass1.text()
        register_pass2 = self.lineEdit_register_pass2.text()

        if register_pass1 == '':
            self.label_password_check.setText("")
        elif register_pass2 == '':
            self.label_password_check.setText("")
        elif register_pass1 != '' and register_pass2 != '':
            if register_pass1 == register_pass2:
                self.label_password_check.setText("비밀번호가 일치합니다.")
                self.label_password_check.setStyleSheet("Color : blue")
                check_password = 0
            elif register_pass1 != register_pass2:
                self.label_password_check.setText("비밀번호가 일치하지 않습니다.")
                self.label_password_check.setStyleSheet("Color : red")
                check_password = 1

    #회원가입 버튼 클릭
    def complete_register(self):
        global register_name
        global register_phone
        global register_email
        global register_check

        register_id = self.lineEdit_register_id.text()
        register_pass1 = self.lineEdit_register_pass1.text()
        register_pass2 = self.lineEdit_register_pass2.text()
        register_name = self.lineEdit_register_name.text()
        register_phone = self.lineEdit_register_phone.text()
        register_email = self.lineEdit_register_email.text()
        register_check = self.checkBox_personal.isChecked()

        msg = QMessageBox()

        if register_id == '':
            msg.setWindowTitle('알림')
            msg.setText('아이디를 입력해주세요.')
            msg.exec_()
            return
        elif check_id == 1:
            msg.setWindowTitle('알림')
            msg.setText('아이디 중복확인을 클릭해주세요.')
            msg.exec_()
            return
        elif register_pass1 == '':
            msg.setWindowTitle('알림')
            msg.setText('비밀번호를 입력해주세요.')
            msg.exec_()
            return
        elif register_pass2 == '':
            msg.setWindowTitle('알림')
            msg.setText('비밀번호를 다시 입력해주세요.')
            msg.exec_()
            return
        elif check_password == 1:
            msg.setWindowTitle('알림')
            msg.setText('비밀번호를 다시 확인해주세요.')
            msg.exec_()
            return
        elif register_name == '':
            msg.setWindowTitle('알림')
            msg.setText('성함을 입력해주세요.')
            msg.exec_()
            return
        if register_phone == '':
            msg.setWindowTitle('알림')
            msg.setText('연락처를 입력해주세요.')
            msg.exec_()
            return
        else:
            phone_regex = re.compile("^(01)\d{1}-\d{3,4}-\d{4}$")
            phone_validation = phone_regex.search(register_phone.replace(" ",""))
            if phone_validation:
                pass
            else:
                msg.setWindowTitle('알림')
                msg.setText('연락처를 정확히 입력해주세요.'+'\n'+'ex)010-0000-0000')
                msg.exec_()
                return
        if register_email == '':
            msg.setWindowTitle('알림')
            msg.setText('이메일을 입력해주세요.')
            msg.exec_()
            return
        else:
            email = re.compile("([A-Za-z]+[A-Za-z0-9]+@[A-Za-z]+\.[A-Za-z]+)")
            email_validation = email.search(register_email.replace(" ",""))
            if email_validation:
                pass
            else:
                msg.setWindowTitle('알림')
                msg.setText('이메일을 정확히 입력해주세요.'+'\n'+'ex)abcdefg@naver.com')
                msg.exec_()
                return
        if register_check == False:
            msg.setWindowTitle('알림')
            msg.setText('이용약관과 개인정보 취급방침에 동의해주세요.')
            msg.exec_()
        else:
            reply = QMessageBox.question(self, '확인', '회원가입을 진행하시겠습니까?',
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                #User DB에 회원정보
                try:
                    con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                    cur_user = con_user.cursor()
                    sql = f"INSERT INTO youngmusk_login (id, password, mac, premium, name, phone, email, register) VALUES ('{register_id}','{register_pass2}','{mac_address}','{premium_date}','{register_name}','{register_phone}','{register_email}','{register_date}');"
                    cur_user.execute(sql)
                except:
                    msg.setWindowTitle('알림')
                    msg.setText('회원가입이 실패하였습니다.\n관리자에게 문의하세요.')
                    msg.exec_()
                    # con_user.commit()
                    con_user.close()
                    return
                finally:
                    con_user.commit()
                    con_user.close()

                #Check DB에 회원정보 저장
                try:
                    con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                    cur_user = con_user.cursor()
                    sql = f"INSERT INTO check_login (id, password, mac, premium, review, recommend) VALUES ('{register_id}','{register_pass2}','{mac_address}','{premium_date}',0,0);"
                    cur_user.execute(sql)
                except:
                    msg.setWindowTitle('알림')
                    msg.setText('회원가입이 실패하였습니다.\n관리자에게 문의하세요.')
                    msg.exec_()
                    # con_user.commit()
                    con_user.close()
                    return
                finally:
                    con_user.commit()
                    con_user.close()
                    #창 닫고 완료 알림창 띄우기
                    self.close()
                    msg.setWindowTitle('알림')
                    msg.setText('회원가입이 완료되었습니다.')
                    msg.exec_()                
            else:
                return

class Window_Find(QDialog, UI_Find):
    
    #기본 설정
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.show()
    
    #실행 설정
    def initUI(self):
        self.setWindowTitle("머슭상품")
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet(qdarktheme.load_stylesheet("light"))

        #MAC주소 불러오기
        self.lineEdit_find_mac.setText(mac_address)

        #check db에서 아이디 불러오기
        global db_id
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT * FROM check_login WHERE mac=%s;"
            cur_user.execute(sql, mac_address)
            check_id = cur_user.fetchall()
            db_id = check_id[0][1]
            self.lineEdit_find_id.setText(db_id)
        except:
            pass
        finally:
            con_user.commit()
            con_user.close()

class Window_Analysis(QMainWindow, UI_Analysis):
  
    #기본 설정
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.show()

        global category_count
        global category_num

        global category_cnt
        global category_all
        global product_cnt
        global product_all

        global time_bool
        global time_bool_filtering
        global time_bool_category
        global time_bool_product
        global time_bool_download

        global check_searching
        global check_filtering
        global check_category
        global check_product

        check_searching = False
        check_filtering = False
        check_category = False
        check_product = False

        category_num = 0
        category_count = 0
        category_cnt = 0
        category_all = 0
        product_cnt = 0
        product_all = 0

        time_bool = False
        time_bool_filtering = False
        time_bool_category = False
        time_bool_product = False
        time_bool_download = False

        self.timer = QTimer(self)                   # timer 변수에 QTimer 할당
        self.timer.start(2000)                     # 10000msec(10sec) 마다 반복
        self.timer.timeout.connect(self.listbox_searching)    # start time out시 연결할 함수
    
    #실행 설정
    def initUI(self):
        global premium_days
        global remain_count

        self.setWindowTitle("머슭상품")
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet(qdarktheme.load_stylesheet("light"))
        # dt_now = datetime.datetime.now()
        # keyword_date = dt_now.date()
        #MAC주소 불러오기
        self.label_mac.setText("MAC : "+ mac_address)
        #아이디 불러오기
        self.label_id.setText("ID : "+ db_id)
        #잔여 검색수 불러오기
        self.label_count.setText("잔여 검색수 : "+ str(remain_count))
        #불러오기
        premium_days = db_premium - register_date
        premium_days = premium_days.days
        if premium_days < 0:
            premium_days = 0
        self.label_premium.setText("프리미엄 잔여일수 : "+ str(premium_days))

        #시그널
        # worker= Thread1(self)
        # worker.user_signal.connect(self.user_slot)

        #카테고리 불러오기
        self.import_category()
        self.comboBox_level_1.activated[str].connect(self.level_1)
        self.comboBox_level_2.activated[str].connect(self.level_2)
        self.comboBox_level_3.activated[str].connect(self.level_3)
        #옵션 기본값 설정
        self.option_standard_setting()
        #제조국가 체크 상태 변동 시
        self.checkBox_country_all.stateChanged.connect(self.country_all)
        #몰등급 체크 상태 변동 시
        self.checkBox_level_all.stateChanged.connect(self.level_all)
        #상품가격 체크 상태 변동 시
        self.checkBox_price_all.stateChanged.connect(self.price_all)
        self.spinBox_price_min.valueChanged.connect(self.price_changed)
        self.spinBox_price_max.valueChanged.connect(self.price_changed)
        #등록일자 체크 상태 변동 시
        self.checkBox_date_all.stateChanged.connect(self.date_all)
        self.dateEdit_min.dateChanged.connect(self.date_changed)
        self.dateEdit_max.dateChanged.connect(self.date_changed)
        #구매7일 체크 상태 변동 시
        self.checkBox_pur3_all.stateChanged.connect(self.pur3_all)
        self.spinBox_pur3_min.valueChanged.connect(self.pur3_changed)
        self.spinBox_pur3_max.valueChanged.connect(self.pur3_changed)
        #구매 체크 상태 변동 시
        self.checkBox_pur_all.stateChanged.connect(self.pur_all)
        self.spinBox_pur_min.valueChanged.connect(self.pur_changed)
        self.spinBox_pur_max.valueChanged.connect(self.pur_changed)
        #리뷰 체크 상태 변동 시
        self.checkBox_review_all.stateChanged.connect(self.review_all)
        self.spinBox_review_min.valueChanged.connect(self.review_changed)
        self.spinBox_review_max.valueChanged.connect(self.review_changed)
        #찜 체크 상태 변동 시
        self.checkBox_zzim_all.stateChanged.connect(self.zzim_all)
        self.spinBox_zzim_min.valueChanged.connect(self.zzim_changed)
        self.spinBox_zzim_max.valueChanged.connect(self.zzim_changed)
        #문의 체크 상태 변동 시
        self.checkBox_con_all.stateChanged.connect(self.con_all)
        self.spinBox_con_min.valueChanged.connect(self.con_changed)
        self.spinBox_con_max.valueChanged.connect(self.con_changed)
        #수집 체크 상태 변동 시
        self.checkBox_page_all.stateChanged.connect(self.page_all)
        self.spinBox_page_min.valueChanged.connect(self.page_changed)
        self.spinBox_page_max.valueChanged.connect(self.page_changed)
        
        #중지버튼 비활성화
        self.pushButton.setEnabled(False)

        dt_now = datetime.datetime.now()

        #모듈 로그 DB 입력
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','로그인','{dt_now}');"
            cur_user.execute(sql)
        except:
            pass
        finally:
            con_user.commit()
            con_user.close()

    #옵션 기본값
    def option_standard_setting(self):
        #판매유형 전체
        self.radioButton_type_all.setChecked(True)
        #제조국가 전체
        self.checkBox_country_korea.setEnabled(False)
        self.checkBox_country_china.setEnabled(False)
        self.checkBox_country_usa.setEnabled(False)
        self.checkBox_country_japan.setEnabled(False)
        self.checkBox_country_europe.setEnabled(False)
        self.checkBox_country_etc.setEnabled(False)
        #몰등급 전체
        self.checkBox_level_pla.setEnabled(False)
        self.checkBox_level_pre.setEnabled(False)
        self.checkBox_level_big.setEnabled(False)
        self.checkBox_level_pow.setEnabled(False)
        self.checkBox_level_new.setEnabled(False)
        #상품가격 전체
        self.spinBox_price_min.setEnabled(False)
        self.spinBox_price_max.setEnabled(False)
        #등록일자 전체
        self.dateEdit_max.setDate(QDate.currentDate())
        self.dateEdit_max.setMaximumDate(QDate.currentDate())
        self.dateEdit_min.setEnabled(False)
        self.dateEdit_max.setEnabled(False)
        #구매7일 전체
        self.spinBox_pur3_min.setEnabled(False)
        self.spinBox_pur3_max.setEnabled(False)
        #구매 전체
        self.spinBox_pur_min.setEnabled(False)
        self.spinBox_pur_max.setEnabled(False)
        #리뷰 전체
        self.spinBox_review_min.setEnabled(False)
        self.spinBox_review_max.setEnabled(False)
        #찜 전체
        self.spinBox_zzim_min.setEnabled(False)
        self.spinBox_zzim_max.setEnabled(False)
        #문의 전체
        self.spinBox_con_min.setEnabled(False)
        self.spinBox_con_max.setEnabled(False)
        #수집 전체
        self.spinBox_page_min.setEnabled(False)
        self.spinBox_page_max.setEnabled(False)

    #기본값 설정
    def standard_setting(self):
        self.textEdit_box.append("검색 설정을 기본값으로 복원하였습니다.")
        #카테고리
        self.comboBox_level_1.setCurrentText('전체')
        self.level_1()
        #판매유형
        self.radioButton_type_all.toggle()
        #제조국가
        if self.checkBox_country_all.isChecked() == True:
            pass
        else:
            self.checkBox_country_all.toggle()
        #상품가격
        if self.checkBox_price_all.isChecked() == True:
            pass
        else:
            self.checkBox_price_all.toggle()
        self.spinBox_price_min.setValue(0)
        self.spinBox_price_max.setValue(1000000)
        #등록일자
        if self.checkBox_date_all.isChecked() == True:
            pass
        else:
            self.checkBox_date_all.toggle()
        self.dateEdit_min.setDate(QDate(2000,1,1))
        self.dateEdit_max.setDate(QDate.currentDate())
        #구매7일
        if self.checkBox_pur3_all.isChecked() == True:
            pass
        else:
            self.checkBox_pur3_all.toggle()
        self.spinBox_pur3_min.setValue(0)
        self.spinBox_pur3_max.setValue(1000)            
        #구매
        if self.checkBox_pur_all.isChecked() == True:
            pass
        else:
            self.checkBox_pur_all.toggle()
        self.spinBox_pur_min.setValue(0)
        self.spinBox_pur_max.setValue(1000) 
        #리뷰
        if self.checkBox_review_all.isChecked() == True:
            pass
        else:
            self.checkBox_review_all.toggle()
        self.spinBox_review_min.setValue(0)
        self.spinBox_review_max.setValue(1000) 
        #찜
        if self.checkBox_zzim_all.isChecked() == True:
            pass
        else:
            self.checkBox_zzim_all.toggle()
        self.spinBox_zzim_min.setValue(0)
        self.spinBox_zzim_max.setValue(1000) 
        #문의
        if self.checkBox_con_all.isChecked() == True:
            pass
        else:
            self.checkBox_con_all.toggle()
        self.spinBox_con_min.setValue(0)
        self.spinBox_con_max.setValue(1000)
        #수집
        if self.checkBox_page_all.isChecked() == True:
            pass
        else:
            self.checkBox_page_all.toggle()
        self.spinBox_page_min.setValue(1)
        self.spinBox_page_max.setValue(100) 
        #몰등급
        if self.checkBox_level_all.isChecked() == True:
            pass
        else:
            self.checkBox_level_all.toggle()

    #설정값 내보내기
    def setting_export(self):
        file_name = QFileDialog.getSaveFileName(self, self.tr("Save Data files"), "./", self.tr("PICKLE 문서 (*.pickle)"))

        #설정값 summary
        setting_export = {
            '대분류':self.comboBox_level_1.currentText(),
            '중분류':self.comboBox_level_2.currentText(),
            '소분류':self.comboBox_level_3.currentText(),
            '세분류':self.comboBox_level_4.currentText(),
            '전체유형':self.radioButton_type_all.isChecked(),
            '국내상품':self.radioButton_type_korea.isChecked(),
            '해외직구':self.radioButton_type_oversea.isChecked(),
            '전체국가':self.checkBox_country_all.isChecked(),
            '국내':self.checkBox_country_korea.isChecked(),
            '중국':self.checkBox_country_china.isChecked(),
            '미국':self.checkBox_country_usa.isChecked(),
            '일본':self.checkBox_country_japan.isChecked(),
            '유럽':self.checkBox_country_europe.isChecked(),
            '기타':self.checkBox_country_etc.isChecked(),
            '전체가격':self.checkBox_price_all.isChecked(),
            '최저가격':self.spinBox_price_min.value(),
            '최고가격':self.spinBox_price_max.value(),
            '전체기간':self.checkBox_date_all.isChecked(),
            '시작일자':[self.dateEdit_min.date().year(),self.dateEdit_min.date().month(),self.dateEdit_min.date().day()],
            '종료일자':[self.dateEdit_max.date().year(),self.dateEdit_max.date().month(),self.dateEdit_max.date().day()],
            '구매7일':self.checkBox_pur3_all.isChecked(),
            '구매7일_min':self.spinBox_pur3_min.value(),
            '구매7일_max':self.spinBox_pur3_max.value(),            
            '구매':self.checkBox_pur_all.isChecked(),
            '구매_min':self.spinBox_pur_min.value(),
            '구매_max':self.spinBox_pur_max.value(),
            '리뷰':self.checkBox_review_all.isChecked(),
            '리뷰_min':self.spinBox_review_min.value(),
            '리뷰_max':self.spinBox_review_max.value(),
            '찜':self.checkBox_zzim_all.isChecked(),
            '찜_min':self.spinBox_zzim_min.value(),
            '찜_max':self.spinBox_zzim_max.value(),
            '문의':self.checkBox_con_all.isChecked(),
            '문의_min':self.spinBox_con_min.value(),
            '문의_max':self.spinBox_con_max.value(),
            '전체등급':self.checkBox_level_all.isChecked(),
            '플래티넘':self.checkBox_level_pla.isChecked(),
            '프리미엄':self.checkBox_level_pre.isChecked(),
            '빅파워':self.checkBox_level_big.isChecked(),
            '파워':self.checkBox_level_pow.isChecked(),
            '새싹':self.checkBox_level_new.isChecked(),
            '수집':self.checkBox_page_all.isChecked(),
            '수집_min':self.spinBox_page_min.value(),
            '수집_max':self.spinBox_page_max.value()
            }

        #PICKLE 파일로 내보내기
        try:
            with open(file_name[0],'wb') as fw:
                pickle.dump(setting_export, fw)
                self.textEdit_box.append("현재 설정된 값을 성공적으로 저장하였습니다.")
        except:
            pass

    #설정값 불러오기
    def setting_import(self):
        file_name = QFileDialog.getOpenFileName(self, self.tr("Open Data files"), "./", self.tr("PICKLE 문서 (*.pickle)"))
        try:
            with open(file_name[0], 'rb') as fr:
                set = pickle.load(fr)
            # print(set)
        except:
            return
        
        #설정값 세팅
        #카테고리 세팅
        self.comboBox_level_1.setCurrentText(set['대분류'])
        self.level_1()
        self.comboBox_level_2.setCurrentText(set['중분류'])
        self.level_2()
        self.comboBox_level_3.setCurrentText(set['소분류'])
        self.level_3()
        self.comboBox_level_4.setCurrentText(set['세분류'])
        #판매유형 세팅
        if set['전체유형'] == True:
            self.radioButton_type_all.setChecked(True)
        elif set['국내상품'] == True:
            self.radioButton_type_korea.setChecked(True)
        elif set['해외직구'] == True:
            self.radioButton_type_oversea.setChecked(True)
        #제조국가 세팅
        if set['전체국가'] == True:
            if self.checkBox_country_all.isChecked() == True:
                pass
            else:
                self.checkBox_country_all.toggle()            
        else:
            if self.checkBox_country_all.isChecked() == True:
                self.checkBox_country_all.toggle()  
            if set['국내'] != self.checkBox_country_korea.isChecked():
                self.checkBox_country_korea.toggle()            
            if set['중국'] != self.checkBox_country_china.isChecked():
                self.checkBox_country_china.toggle()    
            if set['미국'] != self.checkBox_country_usa.isChecked():
                self.checkBox_country_usa.toggle()    
            if set['일본'] != self.checkBox_country_japan.isChecked():
                self.checkBox_country_japan.toggle()    
            if set['유럽'] != self.checkBox_country_europe.isChecked():
                self.checkBox_country_europe.toggle()
            if set['기타'] != self.checkBox_country_etc.isChecked():
                self.checkBox_country_etc.toggle()
        #상품가격 세팅
        if set['전체가격'] == True:
            if self.checkBox_price_all.isChecked() == True:
                pass
            else:
                self.checkBox_price_all.toggle()
        else:
            if self.checkBox_price_all.isChecked() == True:
                self.checkBox_price_all.toggle()  
        self.spinBox_price_min.setValue(0)
        self.spinBox_price_max.setValue(999999999)
        self.spinBox_price_min.setValue(set['최저가격'])
        self.spinBox_price_max.setValue(set['최고가격'])
        #등록일자 세팅
        if set['전체기간'] == True:
            if self.checkBox_date_all.isChecked() == True:
                pass
            else:
                self.checkBox_date_all.toggle()
        else:
            if self.checkBox_date_all.isChecked() == True:
                self.checkBox_date_all.toggle()  
        self.dateEdit_min.setDate(QDate(1800,1,1))
        self.dateEdit_max.setDate(QDate.currentDate())
        self.dateEdit_min.setDate(QDate(set['시작일자'][0],set['시작일자'][1],set['시작일자'][2]))
        self.dateEdit_max.setDate(QDate(set['종료일자'][0],set['종료일자'][1],set['종료일자'][2]))
        #구매7일 세팅
        if set['구매7일'] == True:
            if self.checkBox_pur3_all.isChecked() == True:
                pass
            else:
                self.checkBox_pur3_all.toggle()
        else:
            if self.checkBox_pur3_all.isChecked() == True:
                self.checkBox_pur3_all.toggle()  
        self.spinBox_pur3_min.setValue(0)
        self.spinBox_pur3_max.setValue(99999)
        self.spinBox_pur3_min.setValue(set['구매7일_min'])
        self.spinBox_pur3_max.setValue(set['구매7일_max'])        
        #구매 세팅
        if set['구매'] == True:
            if self.checkBox_pur_all.isChecked() == True:
                pass
            else:
                self.checkBox_pur_all.toggle()
        else:
            if self.checkBox_pur_all.isChecked() == True:
                self.checkBox_pur_all.toggle()  
        self.spinBox_pur3_min.setValue(0)
        self.spinBox_pur3_max.setValue(99999)
        self.spinBox_pur3_min.setValue(set['구매_min'])
        self.spinBox_pur3_max.setValue(set['구매_max'])        
        #리뷰 세팅
        if set['리뷰'] == True:
            if self.checkBox_review_all.isChecked() == True:
                pass
            else:
                self.checkBox_review_all.toggle()
        else:
            if self.checkBox_review_all.isChecked() == True:
                self.checkBox_review_all.toggle()  
        self.spinBox_review_min.setValue(0)
        self.spinBox_review_max.setValue(99999)
        self.spinBox_review_min.setValue(set['리뷰_min'])
        self.spinBox_review_max.setValue(set['리뷰_max'])                       
        #찜 세팅
        if set['찜'] == True:
            if self.checkBox_zzim_all.isChecked() == True:
                pass
            else:
                self.checkBox_zzim_all.toggle()
        else:
            if self.checkBox_zzim_all.isChecked() == True:
                self.checkBox_zzim_all.toggle()  
        self.spinBox_zzim_min.setValue(0)
        self.spinBox_zzim_max.setValue(99999)
        self.spinBox_zzim_min.setValue(set['찜_min'])
        self.spinBox_zzim_max.setValue(set['찜_max'])      
        #문의 세팅
        if set['문의'] == True:
            if self.checkBox_con_all.isChecked() == True:
                pass
            else:
                self.checkBox_con_all.toggle()
        else:
            if self.checkBox_con_all.isChecked() == True:
                self.checkBox_con_all.toggle()  
        self.spinBox_con_min.setValue(0)
        self.spinBox_con_max.setValue(99999)
        self.spinBox_con_min.setValue(set['문의_min'])
        self.spinBox_con_max.setValue(set['문의_max'])
        #수집 세팅
        if set['수집'] == True:
            if self.checkBox_page_all.isChecked() == True:
                pass
            else:
                self.checkBox_page_all.toggle()
        else:
            if self.checkBox_page_all.isChecked() == True:
                self.checkBox_page_all.toggle()  
        self.spinBox_page_min.setValue(0)
        self.spinBox_page_max.setValue(100)
        self.spinBox_page_min.setValue(set['수집_min'])
        self.spinBox_page_max.setValue(set['수집_max'])
        #몰등급 세팅
        if set['전체등급'] == True:
            if self.checkBox_level_all.isChecked() == True:
                pass
            else:
                self.checkBox_level_all.toggle()            
        else:
            if self.checkBox_level_all.isChecked() == True:
                self.checkBox_level_all.toggle()  
            if set['플래티넘'] != self.checkBox_level_pla.isChecked():
                self.checkBox_level_pla.toggle()            
            if set['프리미엄'] != self.checkBox_level_pre.isChecked():
                self.checkBox_level_pre.toggle()    
            if set['빅파워'] != self.checkBox_level_big.isChecked():
                self.checkBox_level_big.toggle()    
            if set['파워'] != self.checkBox_level_pow.isChecked():
                self.checkBox_level_pow.toggle()    
            if set['새싹'] != self.checkBox_level_new.isChecked():
                self.checkBox_level_new.toggle()
        self.textEdit_box.append("저장된 설정값을 성공적으로 적용하였습니다.")

    #등록일자 변경
    def date_changed(self):
        self.dateEdit_min.setMaximumDate(self.dateEdit_max.date())
        self.dateEdit_max.setMinimumDate(self.dateEdit_min.date())

    #상품가격 변경
    def price_changed(self):
        self.spinBox_price_min.setMaximum(self.spinBox_price_max.value())
        self.spinBox_price_max.setMinimum(self.spinBox_price_min.value())
    #구매7일 변경
    def pur3_changed(self):
        self.spinBox_pur3_min.setMaximum(self.spinBox_pur3_max.value())
        self.spinBox_pur3_max.setMinimum(self.spinBox_pur3_min.value())
    #구매 변경
    def pur_changed(self):
        self.spinBox_pur_min.setMaximum(self.spinBox_pur_max.value())
        self.spinBox_pur_max.setMinimum(self.spinBox_pur_min.value())
    #리뷰 변경
    def review_changed(self):
        self.spinBox_review_min.setMaximum(self.spinBox_review_max.value())
        self.spinBox_review_max.setMinimum(self.spinBox_review_min.value())
    #찜 변경
    def zzim_changed(self):
        self.spinBox_zzim_min.setMaximum(self.spinBox_zzim_max.value())
        self.spinBox_zzim_max.setMinimum(self.spinBox_zzim_min.value())
    #문의 변경
    def con_changed(self):
        self.spinBox_con_min.setMaximum(self.spinBox_con_max.value())
        self.spinBox_con_max.setMinimum(self.spinBox_con_min.value())
    #수집 변경
    def page_changed(self):
        self.spinBox_page_min.setMaximum(self.spinBox_page_max.value())
        self.spinBox_page_max.setMinimum(self.spinBox_page_min.value())

    #수집 체크 로직 구현
    def page_all(self, state):
        if state == 0:
            self.spinBox_page_min.setEnabled(True)
            self.spinBox_page_max.setEnabled(True)
        else:
            self.spinBox_page_min.setEnabled(False)
            self.spinBox_page_max.setEnabled(False)

    #문의 체크 로직 구현
    def con_all(self, state):
        if state == 0:
            self.spinBox_con_min.setEnabled(True)
            self.spinBox_con_max.setEnabled(True)
        else:
            self.spinBox_con_min.setEnabled(False)
            self.spinBox_con_max.setEnabled(False)

    #찜 체크 로직 구현
    def zzim_all(self, state):
        if state == 0:
            self.spinBox_zzim_min.setEnabled(True)
            self.spinBox_zzim_max.setEnabled(True)
        else:
            self.spinBox_zzim_min.setEnabled(False)
            self.spinBox_zzim_max.setEnabled(False)

    #리뷰 체크 로직 구현
    def review_all(self, state):
        if state == 0:
            self.spinBox_review_min.setEnabled(True)
            self.spinBox_review_max.setEnabled(True)
        else:
            self.spinBox_review_min.setEnabled(False)
            self.spinBox_review_max.setEnabled(False)

    #구매 체크 로직 구현
    def pur_all(self, state):
        if state == 0:
            self.spinBox_pur_min.setEnabled(True)
            self.spinBox_pur_max.setEnabled(True)
        else:
            self.spinBox_pur_min.setEnabled(False)
            self.spinBox_pur_max.setEnabled(False)

    #구매7일 체크 로직 구현
    def pur3_all(self, state):
        if state == 0:
            self.spinBox_pur3_min.setEnabled(True)
            self.spinBox_pur3_max.setEnabled(True)
        else:
            self.spinBox_pur3_min.setEnabled(False)
            self.spinBox_pur3_max.setEnabled(False)

    #등록일자 체크 로직 구현
    def date_all(self, state):
        if state == 0:
            self.dateEdit_min.setEnabled(True)
            self.dateEdit_max.setEnabled(True)
        else:
            self.dateEdit_min.setEnabled(False)
            self.dateEdit_max.setEnabled(False)

    #상품가격 체크 로직 구현
    def price_all(self, state):
        if state == 0:
            self.spinBox_price_min.setEnabled(True)
            self.spinBox_price_max.setEnabled(True)
        else:
            self.spinBox_price_min.setEnabled(False)
            self.spinBox_price_max.setEnabled(False)

    #제조국가 체크 로직 구현
    def country_all(self, state):
        global country_korea_cnt
        global country_china_cnt
        global country_usa_cnt
        global country_japan_cnt
        global country_europe_cnt
        global country_etc_cnt

        country_korea_cnt = self.checkBox_country_korea.isChecked()
        country_china_cnt = self.checkBox_country_china.isChecked()
        country_usa_cnt = self.checkBox_country_usa.isChecked()
        country_japan_cnt = self.checkBox_country_japan.isChecked()
        country_europe_cnt = self.checkBox_country_europe.isChecked()
        country_etc_cnt = self.checkBox_country_etc.isChecked()

        if state == 0:
            self.checkBox_country_korea.setEnabled(True)
            self.checkBox_country_china.setEnabled(True)
            self.checkBox_country_usa.setEnabled(True)
            self.checkBox_country_japan.setEnabled(True)
            self.checkBox_country_europe.setEnabled(True)
            self.checkBox_country_etc.setEnabled(True)
            if country_korea_cnt == False:
                self.checkBox_country_korea.toggle()
            if country_china_cnt == False:
                self.checkBox_country_china.toggle()
            if country_usa_cnt == False:
                self.checkBox_country_usa.toggle()
            if country_japan_cnt == False:
                self.checkBox_country_japan.toggle()
            if country_europe_cnt == False:
                self.checkBox_country_europe.toggle()
            if country_etc_cnt == False:
                self.checkBox_country_etc.toggle()
        else:
            self.checkBox_country_korea.setEnabled(False)
            self.checkBox_country_china.setEnabled(False)
            self.checkBox_country_usa.setEnabled(False)
            self.checkBox_country_japan.setEnabled(False)
            self.checkBox_country_europe.setEnabled(False)
            self.checkBox_country_etc.setEnabled(False)
            if country_korea_cnt == True:
                self.checkBox_country_korea.toggle()
            if country_china_cnt == True:
                self.checkBox_country_china.toggle()
            if country_usa_cnt == True:
                self.checkBox_country_usa.toggle()
            if country_japan_cnt == True:
                self.checkBox_country_japan.toggle()
            if country_europe_cnt == True:
                self.checkBox_country_europe.toggle()
            if country_etc_cnt == True:
                self.checkBox_country_etc.toggle()
    #몰등급 체크 로직 구현
    def level_all(self, state):
        global level_pla_cnt
        global level_pre_cnt
        global level_big_cnt
        global level_pow_cnt
        global level_new_cnt

        level_pla_cnt = self.checkBox_level_pla.isChecked()
        level_pre_cnt = self.checkBox_level_pre.isChecked()
        level_big_cnt = self.checkBox_level_big.isChecked()
        level_pow_cnt = self.checkBox_level_pow.isChecked()
        level_new_cnt = self.checkBox_level_new.isChecked()

        if state == 0:
            self.checkBox_level_pla.setEnabled(True)
            self.checkBox_level_pre.setEnabled(True)
            self.checkBox_level_big.setEnabled(True)
            self.checkBox_level_pow.setEnabled(True)
            self.checkBox_level_new.setEnabled(True)
            if level_pla_cnt == False:
                self.checkBox_level_pla.toggle()
            if level_pre_cnt == False:
                self.checkBox_level_pre.toggle()
            if level_big_cnt == False:
                self.checkBox_level_big.toggle()
            if level_pow_cnt == False:
                self.checkBox_level_pow.toggle()
            if level_new_cnt == False:
                self.checkBox_level_new.toggle()
        else:
            self.checkBox_level_pla.setEnabled(False)
            self.checkBox_level_pre.setEnabled(False)
            self.checkBox_level_big.setEnabled(False)
            self.checkBox_level_pow.setEnabled(False)
            self.checkBox_level_new.setEnabled(False)
            if level_pla_cnt == True:
                self.checkBox_level_pla.toggle()
            if level_pre_cnt == True:
                self.checkBox_level_pre.toggle()
            if level_big_cnt == True:
                self.checkBox_level_big.toggle()
            if level_pow_cnt == True:
                self.checkBox_level_pow.toggle()
            if level_new_cnt == True:
                self.checkBox_level_new.toggle()

    #카테고리 불러오기
    def import_category(self):
        global df_category
        # df_category = pd.read_csv('./category.csv', encoding='cp949')
        df_category = pd.read_csv('./category.csv')
        df_category = df_category.astype(str)

        category_level_1 = df_category['대분류'].unique()

        #카테고리 기본값 세팅
        self.comboBox_level_1.addItem('전체')
        self.comboBox_level_2.addItem('전체')
        self.comboBox_level_3.addItem('전체')
        self.comboBox_level_4.addItem('전체')
        for level_1_elm in category_level_1:
            self.comboBox_level_1.addItem(level_1_elm)

    #카테고리
    def level_1(self):
        level_1_keyword = self.comboBox_level_1.currentText()
        category_level_2 = df_category[df_category['대분류'] == level_1_keyword]['중분류'].unique()

        self.comboBox_level_2.clear()
        self.comboBox_level_3.clear()
        self.comboBox_level_4.clear()
        self.comboBox_level_2.addItem('전체')
        self.comboBox_level_3.addItem('전체')
        self.comboBox_level_4.addItem('전체')

        for level_2_elm in category_level_2:
            self.comboBox_level_2.addItem(level_2_elm)

    def level_2(self):
        level_1_keyword = self.comboBox_level_1.currentText()
        level_2_keyword = self.comboBox_level_2.currentText()
        category_level_3 = df_category[df_category['대분류'] == level_1_keyword][df_category['중분류'] == level_2_keyword]['소분류'].unique()

        self.comboBox_level_3.clear()
        self.comboBox_level_4.clear()
        self.comboBox_level_3.addItem('전체')
        self.comboBox_level_4.addItem('전체')

        for level_3_elm in category_level_3:
            if level_3_elm == 'nan':
                pass
            else:
                self.comboBox_level_3.addItem(level_3_elm)

    def level_3(self):
        level_1_keyword = self.comboBox_level_1.currentText()
        level_2_keyword = self.comboBox_level_2.currentText()
        level_3_keyword = self.comboBox_level_3.currentText()
        category_level_4 = df_category[df_category['대분류'] == level_1_keyword][df_category['중분류'] == level_2_keyword][df_category['소분류'] == level_3_keyword]['세분류'].unique()

        self.comboBox_level_4.clear()
        self.comboBox_level_4.addItem('전체')

        for level_4_elm in category_level_4:
            if level_4_elm == 'nan':
                pass
            else:
                self.comboBox_level_4.addItem(level_4_elm)

    def free_interface(self):
        msg = QMessageBox() #메시지 알림 박스

        #이벤트 진행여부
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            #프로그램 버젼 확인
            sql = "SELECT * FROM version WHERE name=%s;"
            cur_user.execute(sql, 'V5')
            check_version = cur_user.fetchall()
            check_review = check_version[0][4]
        except:
            msg.setWindowTitle('알림')
            msg.setText('버젼 확인이 실패하였습니다.\n관리자에게 문의하세요.')
            msg.exec_()
        finally:
            con_user.commit()
            con_user.close()

        if check_review != '1':
            msg.setWindowTitle('알림')
            msg.setText('리뷰 이벤트가 종료되었습니다.\n다시 진행할 경우 공지사항에 업데이트됩니다.')
            msg.exec_()
            return

        dt_now = datetime.datetime.now()

        #모듈 로그 DB 입력
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','블로그 후기','{dt_now}');"
            cur_user.execute(sql)
        except:
            pass
        finally:
            con_user.commit()
            con_user.close()

        self.main = Window_Free()

    def recommend_interface(self):
        dt_now = datetime.datetime.now()

        #모듈 로그 DB 입력
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','추천인 입력','{dt_now}');"
            cur_user.execute(sql)
        except:
            pass
        finally:
            con_user.commit()
            con_user.close()
        self.main = Window_Recommend()

    def keyword_interface(self):
        self.main = Window_Keyword()

    def logout_interface(self):
        
        msg = QMessageBox() #메시지 알림 박스

        reply = QMessageBox.question(self, '확인', '로그아웃을 진행하시겠습니까?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            dt_now = datetime.datetime.now()

            #모듈 로그 DB 입력
            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','로그아웃','{dt_now}');"
                cur_user.execute(sql)
            except:
                pass
            finally:
                con_user.commit()
                con_user.close()

            thread = Thread1(self)
            thread.stop()
            self.main = Window_Login()
            self.hide()  
            self.main.exec()
        else:
            pass
    
    def premium_link(self):
        msg = QMessageBox()
        dt_now = datetime.datetime.now()

        #모듈 로그 DB 입력
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','멤버쉽 안내','{dt_now}');"
            cur_user.execute(sql)
        except:
            pass
        finally:
            con_user.commit()
            con_user.close()

        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT * FROM web_link WHERE button=%s;"
            cur_user.execute(sql, '멤버쉽 결제')
            free_seven = cur_user.fetchall()
            webbrowser.open(free_seven[0][2])
        except:
            msg.setWindowTitle('알림')
            msg.setText('홈페이지 접속에 실패하였습니다.\n관리자에게 문의하세요.')
            return

    def contact_link(self):
        dt_now = datetime.datetime.now()

        #모듈 로그 DB 입력
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','문의하기','{dt_now}');"
            cur_user.execute(sql)
        except:
            pass
        finally:
            con_user.commit()
            con_user.close()

        msg = QMessageBox()
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT * FROM web_link WHERE button=%s;"
            cur_user.execute(sql, '문의하기')
            free_seven = cur_user.fetchall()
            webbrowser.open(free_seven[0][2])
        except:
            msg.setWindowTitle('알림')
            msg.setText('홈페이지 접속에 실패하였습니다.\n관리자에게 문의하세요.')
            return
        
    #프로그램 종료
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', '이 프로그램을 종료하시겠습니까?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            dt_now = datetime.datetime.now()

            #모듈 로그 DB 입력
            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','프로그램 종료','{dt_now}');"
                cur_user.execute(sql)
            except:
                pass
            finally:
                con_user.commit()
                con_user.close()

            thread = Thread1(self)
            thread.stop()
            event.accept()
            app.exec_()
        else:
            event.ignore()

    #검색 설정
    def start_setting(self):
        global set_start

        #검색설정 summary
        set_start = {
            '대분류':self.comboBox_level_1.currentText(),
            '중분류':self.comboBox_level_2.currentText(),
            '소분류':self.comboBox_level_3.currentText(),
            '세분류':self.comboBox_level_4.currentText(),
            '전체유형':self.radioButton_type_all.isChecked(),
            '국내상품':self.radioButton_type_korea.isChecked(),
            '해외직구':self.radioButton_type_oversea.isChecked(),
            '전체국가':self.checkBox_country_all.isChecked(),
            '국내':self.checkBox_country_korea.isChecked(),
            '중국':self.checkBox_country_china.isChecked(),
            '미국':self.checkBox_country_usa.isChecked(),
            '일본':self.checkBox_country_japan.isChecked(),
            '유럽':self.checkBox_country_europe.isChecked(),
            '기타':self.checkBox_country_etc.isChecked(),
            '전체가격':self.checkBox_price_all.isChecked(),
            '최저가격':self.spinBox_price_min.value(),
            '최고가격':self.spinBox_price_max.value(),
            '전체기간':self.checkBox_date_all.isChecked(),
            '시작일자':[self.dateEdit_min.date().year(),self.dateEdit_min.date().month(),self.dateEdit_min.date().day()],
            '종료일자':[self.dateEdit_max.date().year(),self.dateEdit_max.date().month(),self.dateEdit_max.date().day()],
            '구매7일':self.checkBox_pur3_all.isChecked(),
            '구매7일_min':self.spinBox_pur3_min.value(),
            '구매7일_max':self.spinBox_pur3_max.value(),            
            '구매':self.checkBox_pur_all.isChecked(),
            '구매_min':self.spinBox_pur_min.value(),
            '구매_max':self.spinBox_pur_max.value(),
            '리뷰':self.checkBox_review_all.isChecked(),
            '리뷰_min':self.spinBox_review_min.value(),
            '리뷰_max':self.spinBox_review_max.value(),
            '찜':self.checkBox_zzim_all.isChecked(),
            '찜_min':self.spinBox_zzim_min.value(),
            '찜_max':self.spinBox_zzim_max.value(),
            '문의':self.checkBox_con_all.isChecked(),
            '문의_min':self.spinBox_con_min.value(),
            '문의_max':self.spinBox_con_max.value(),
            '전체등급':self.checkBox_level_all.isChecked(),
            '플래티넘':self.checkBox_level_pla.isChecked(),
            '프리미엄':self.checkBox_level_pre.isChecked(),
            '빅파워':self.checkBox_level_big.isChecked(),
            '파워':self.checkBox_level_pow.isChecked(),
            '새싹':self.checkBox_level_new.isChecked(),
            '수집':self.checkBox_page_all.isChecked(),
            '수집_min':self.spinBox_page_min.value(),
            '수집_max':self.spinBox_page_max.value()
            }
        self.textEdit_box.append("검색 설정값 적용을 완료하였습니다.")
        
    #AI 상품 추천 시작
    def start_product(self):
        global stop_bool
        global start_time
        global product_cnt
        global product_all
        global check_searching
        global check_category
        global check_product
        global dt_now

        msg = QMessageBox()

        # 진행중일때 리턴
        if time_bool != False:
            msg.setWindowTitle('알림')
            msg.setText('검색 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_filtering != False:
            msg.setWindowTitle('알림')
            msg.setText('필터링 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_category != False:
            msg.setWindowTitle('알림')
            msg.setText('카테고리 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_product != False:
            msg.setWindowTitle('알림')
            msg.setText('상품 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_download != False:
            msg.setWindowTitle('알림')
            msg.setText('엑셀 다운로드 작업이 진행중입니다.')
            msg.exec_()
            return

        if check_searching != True:
            msg.setWindowTitle('알림')
            msg.setText('검색을 진행한 후 다시 시도해주세요.')
            msg.exec_()
            return    

        if check_category != True:
            msg.setWindowTitle('알림')
            msg.setText('AI기반 카테고리 추천을 먼저 진행해주세요.')
            msg.exec_()
            return    

        if check_product == True:
            msg.setWindowTitle('알림')
            msg.setText('이미 상품 분석 작업이 완료되었습니다.\n엑셀 다운로드를 진행해주세요.')
            msg.exec_()
            return    

        #AI 카테고리 추천 진행 확인
        reply = QMessageBox.question(self, '확인', f'AI 상품 추천을 진행하시겠습니까?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            check_product = False

            dt_now = datetime.datetime.now()

            #모듈 로그 DB 입력
            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','AI상품','{dt_now}');"
                cur_user.execute(sql)
            except:
                msg.setWindowTitle('알림')
                msg.setText('서버 이상으로 작동이 불가합니다.\n관리자에게 문의하세요.')
                msg.exec_()
                pass
            finally:
                con_user.commit()
                con_user.close()


            #시작 시간
            start_time = time.time()

            #중지버튼 활성화
            self.pushButton.setEnabled(True)

            stop_bool = True

            product_cnt = 0
            product_all = 0
            self.textEdit_box.append("AI 상품 추천이 시작되었습니다.")
            self.progressBar.setValue(0)

            #멀티쓰레드 가동
            thread = Thread4(self)
            thread.start()


    #AI 카테고리 추천 시작
    def start_category(self):
        global stop_bool
        global start_time
        global category_cnt
        global category_all
        global check_searching
        global check_category
        global dt_now
        msg = QMessageBox()

        # 진행중일때 리턴
        if time_bool != False:
            msg.setWindowTitle('알림')
            msg.setText('검색 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_filtering != False:
            msg.setWindowTitle('알림')
            msg.setText('필터링 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_category != False:
            msg.setWindowTitle('알림')
            msg.setText('카테고리 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_product != False:
            msg.setWindowTitle('알림')
            msg.setText('상품 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_download != False:
            msg.setWindowTitle('알림')
            msg.setText('엑셀 다운로드 작업이 진행중입니다.')
            msg.exec_()
            return

        if check_searching != True:
            msg.setWindowTitle('알림')
            msg.setText('검색을 진행한 후 다시 시도해주세요.')
            msg.exec_()
            return    

        if check_category == True:
            msg.setWindowTitle('알림')
            msg.setText('이미 카테고리 분석 작업이 완료되었습니다.\n다음 작업을 시도해주세요.')
            msg.exec_()
            return    

        #AI 카테고리 추천 진행 확인
        reply = QMessageBox.question(self, '확인', f'AI 카테고리 추천을 진행하시겠습니까?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            check_category = False

            dt_now = datetime.datetime.now()

            #모듈 로그 DB 입력
            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','AI카테고리','{dt_now}');"
                cur_user.execute(sql)
            except:
                msg.setWindowTitle('알림')
                msg.setText('서버 이상으로 작동이 불가합니다.\n관리자에게 문의하세요.')
                msg.exec_()
                pass
            finally:
                con_user.commit()
                con_user.close()

            
            #시작 시간
            start_time = time.time()

            #중지버튼 활성화
            self.pushButton.setEnabled(True)

            stop_bool = True

            category_cnt = 0
            category_all = 0
            self.textEdit_box.append("AI 카테고리 추천이 시작되었습니다.")
            self.progressBar.setValue(0)

            #멀티쓰레드 가동
            thread = Thread3(self)
            thread.start()

    #금지어 필터링 시작
    def start_filtering(self):
        global filter_list
        global stop_bool
        global start_time
        global check_filtering
        global check_searching
        global dt_now
        msg = QMessageBox()

        # 진행중일때 리턴
        if time_bool != False:
            msg.setWindowTitle('알림')
            msg.setText('검색 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_filtering != False:
            msg.setWindowTitle('알림')
            msg.setText('필터링 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_category != False:
            msg.setWindowTitle('알림')
            msg.setText('카테고리 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_product != False:
            msg.setWindowTitle('알림')
            msg.setText('상품 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_download != False:
            msg.setWindowTitle('알림')
            msg.setText('엑셀 다운로드 작업이 진행중입니다.')
            msg.exec_()
            return

        if check_searching != True:
            msg.setWindowTitle('알림')
            msg.setText('검색을 진행한 후 다시 시도해주세요.')
            msg.exec_()
            return

        if check_filtering == True:
            msg.setWindowTitle('알림')
            msg.setText('이미 금지어 필터링 작업이 완료되었습니다.\n다음 작업을 시도해주세요.')
            msg.exec_()
            return    

        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT * FROM filtering_keyword WHERE version=%s;"
            cur_user.execute(sql, 'V1')
            filter_db = cur_user.fetchall()
            filter_list = filter_db[0][2]
        except:
            msg.setWindowTitle('알림')
            msg.setText('서버 접속에 실패하였습니다.\n관리자에게 문의하세요.')
            msg.exec_()
            return

        #필터링 진행 확인
        reply = QMessageBox.question(self, '확인', f'금지어 필터링을 진행하시겠습니까?\n(필터링된 내역도 엑셀 시트에서 볼 수 있습니다.)',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            check_filtering = False

            dt_now = datetime.datetime.now()

            #필터링 로그 DB 입력
            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','금지어','{dt_now}');"
                cur_user.execute(sql)
            except:
                msg.setWindowTitle('알림')
                msg.setText('서버 이상으로 필터링이 불가합니다.\n관리자에게 문의하세요.')
                msg.exec_()
                pass
            finally:
                con_user.commit()
                con_user.close()

            #시작 시간
            start_time = time.time()

            #중지버튼 활성화
            self.pushButton.setEnabled(True)

            stop_bool = True

            self.textEdit_box.append("금지어 필터링이 시작되었습니다.")
            self.progressBar.setValue(0)

            #멀티쓰레드 가동
            thread = Thread2(self)
            thread.start()

    #검색 시작
    def start_searching(self):
        global set_start
        global keyword_list
        global item_list
        global category_num
        global page_num
        global category_count
        global category_data
        global start_time
        global worker_cnt_f
        global stop_bool
        global check_searching
        global check_filtering
        global check_category
        global check_product
        global remain_count
        global dt_now

        msg = QMessageBox()

        # 진행중일때 리턴
        if time_bool != False:
            msg.setWindowTitle('알림')
            msg.setText('검색 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_filtering != False:
            msg.setWindowTitle('알림')
            msg.setText('필터링 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_category != False:
            msg.setWindowTitle('알림')
            msg.setText('카테고리 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_product != False:
            msg.setWindowTitle('알림')
            msg.setText('상품 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_download != False:
            msg.setWindowTitle('알림')
            msg.setText('엑셀 다운로드 작업이 진행중입니다.')
            msg.exec_()
            return

        if premium_days == 0:
            msg.setWindowTitle('알림')
            msg.setText('프리미엄 기간이 종료되었습니다.\n블로그 후기를 작성해서 멤버쉽을 연장해보세요!')
            msg.exec_()
            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = "SELECT * FROM web_link WHERE button=%s;"
                cur_user.execute(sql, '하루남음')
                free_seven = cur_user.fetchall()
                webbrowser.open(free_seven[0][2])
                return
            except:
                msg.setWindowTitle('알림')
                msg.setText('홈페이지 접속에 실패하였습니다.\n관리자에게 문의하세요.')
                msg.exec_()
                return

        if premium_days == 1:
            msg.setWindowTitle('알림')
            msg.setText('프리미엄 기간이 1일 남았습니다.\n미리 멤버쉽을 연장하시는걸 추천드려요!')
            msg.exec_()

        if remain_count < 100:
            msg.setWindowTitle('알림')
            msg.setText('API 호출 제한 수에 도달하여 작업이 불가합니다.\n0시에 검색수가 리셋됩니다.')
            msg.exec_()
            return

        check_searching = False
        check_filtering = False
        check_category = False
        check_product = False
            
        #데이터프레임 형성
        item_list = [['No','대분류','중분류','소분류','세분류','카테고리','순위','판매유형','제조국가','상품가격','등록일자','구매_7일','구매','리뷰','찜','문의','평점','스토어명','등급','상품명','상품명_L','옵션','옵션_L','태그','태그_L','URL']]

        #테이블 리셋    
        self.tableWidget.clear()
        self.tableWidget.setHorizontalHeaderLabels(['No','대분류','중분류','소분류','세분류','카테고리','순위','판매유형','제조국가','상품가격','등록일자','구매_7일','구매','리뷰','찜','문의','평점','스토어명','등급','상품명','상품명_L','옵션','옵션_L','태그','태그_L','URL'])
        category_num = 0
        page_num = 0

        self.progressBar.setValue(0)

        #시작 전 설정값 불러오기
        self.start_setting()
        #검색할 키워드 리스트 불러오기
        category_data = pd.read_csv('./category.csv')
        category_data = category_data.astype(str)
        if set_start['대분류'] == '전체':
            keyword_list = list(category_data['카테고리번호'])
        elif set_start['중분류'] == '전체':
            keyword_list = list(category_data[category_data['대분류'] == set_start['대분류']]['카테고리번호'])
        elif set_start['소분류'] == '전체':  
            keyword_list = list(category_data[category_data['대분류'] == set_start['대분류']][category_data['중분류'] == set_start['중분류']]['카테고리번호'])
        elif set_start['세분류'] == '전체':  
            keyword_list = list(category_data[category_data['대분류'] == set_start['대분류']][category_data['중분류'] == set_start['중분류']][category_data['소분류'] == set_start['소분류']]['카테고리번호'])
        else:
            keyword_list = list(category_data[category_data['대분류'] == set_start['대분류']][category_data['중분류'] == set_start['중분류']][category_data['소분류'] == set_start['소분류']][category_data['세분류'] == set_start['세분류']]['카테고리번호'])
        category_count = len(keyword_list)
        if set_start['수집'] == True:
            set_start['수집_max'] = 100
            set_start['수집_min'] = 1
        remain_pre = category_count*(set_start['수집_max']-set_start['수집_min']+1)
        self.textEdit_box.append(f"총 {category_count}개 카테고리에서 {remain_pre}의 페이지가 선택되었습니다.")
        # print(category_count)

        # 호출 제한 방지 429
        if remain_count < remain_pre :
            msg.setWindowTitle('알림')
            self.textEdit_box.append(f"검색 페이지가 잔여 검색수보다 낮도록 설정해주세요.")
            msg.setText('설정한 카테고리와 수집 페이지가 너무 많습니다.\n잔여 검색수 이하로 재설정해주세요.')
            msg.exec_()
            return

        #예상 검색 시간(로직 : 카테고리 개수, 페이지 개수 * 시간 / worker개수)
        #성능 조회 후 실행                    
        if category_count < worker_cnt:
            worker_cnt_f = category_count
        else:
            worker_cnt_f = int(worker_cnt)

        #max_worker 제한 하기(요청 제한 방지)
        if worker_cnt_f > 10:
            worker_cnt_f = 10

        if set_start['수집'] == True:
            set_start['수집_max'] = 100
            set_start['수집_min'] = 1

        estimated_time = int((category_count * (set_start['수집_max']-set_start['수집_min']+1) * 18 / worker_cnt_f) / 60)
        if estimated_time == 0:
            estimated_time = 1
        #설정값을 텍스트로 변환(DB 저장 목적)
        set_start_db = json.dumps(set_start, ensure_ascii=False)
        keyword_list_db = json.dumps(keyword_list, ensure_ascii=False)

        self.textEdit_box.append("검색 설정값 확인이 완료되었습니다.")

        #검색 진행 확인
        reply = QMessageBox.question(self, '확인', f'예상 검색 시간은 최대 {estimated_time}분 입니다.\n진행하시겠습니까?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            #검색 로그 DB 입력

            #check DB에서 회원정보 조회
            try:
                try:
                    con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
                    cur_user = con_user.cursor()
                    sql = "SELECT * FROM check_login WHERE mac=%s;"
                    cur_user.execute(sql, mac_address)
                    check_id = cur_user.fetchall()
                    last_date = check_id[0][7]
                    # last_count = check_id[0][8]
                except:
                    con_user.close()

                    pass
                finally:
                    con_user.commit()
                    con_user.close()

                #잔여 일수 체크
                r_now = datetime.datetime.now()
                r_now = r_now.date()
                r_now = ['%04d' % r_now.year, '%02d' % r_now.month,'%02d' % r_now.day]
                r_now = ''.join(r_now)

                if int(last_date) == int(r_now):
                    remain_date = last_date
                    remain_count = remain_count
                else:
                    remain_date = r_now
                    remain_count = 25000

                try:
                    con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                    cur_user = con_user.cursor()
                    sql = f"UPDATE check_login SET last_date='{remain_date}' WHERE id='{db_id}';"
                    cur_user.execute(sql)
                    sql = f"UPDATE check_login SET last_count='{remain_count}' WHERE id='{db_id}';"
                    cur_user.execute(sql)
                except:
                    con_user.close()
                    pass
                finally:
                    con_user.commit()
                    con_user.close()
            except:
                pass

            dt_now = datetime.datetime.now()

            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                # print(db_id,estimated_time,premium_days,worker_cnt,keyword_list_db,set_start,dt_now)
                sql = f"INSERT INTO searching_log (id, estimated_time, premium, worker, keyword_list, setting, today) VALUES ('{db_id}','{estimated_time}','{premium_days}','{worker_cnt}','{keyword_list_db}','{set_start_db}','{dt_now}');"
                cur_user.execute(sql)
            except:
                msg.setWindowTitle('알림')
                msg.setText('서버 이상으로 검색이 불가합니다.\n관리자에게 문의하세요.')
                msg.exec_()
                pass
            finally:
                con_user.commit()
                con_user.close()

            #모듈 로그 DB 입력
            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','검색 시작','{dt_now}');"
                cur_user.execute(sql)
            except:
                msg.setWindowTitle('알림')
                msg.setText('서버 이상으로 작동이 불가합니다.\n관리자에게 문의하세요.')
                msg.exec_()
                pass
            finally:
                con_user.commit()
                con_user.close()

            #시작 시간
            start_time = time.time()
            self.textEdit_box.append("검색이 시작되었습니다.")

            #중지버튼 활성화
            self.pushButton.setEnabled(True)

            stop_bool = True

            #멀티쓰레드 가동
            thread = Thread1(self)
            thread.start()


    #리스트 박스 검색중
    def listbox_searching(self):
        # self.tableWidget.repaint()
        global remain_count
        #잔여 검색수 불러오기
        self.label_count.setText("잔여 검색수 : "+ str(remain_count))

        try:
            if time_bool == True:
                try:
                    page_cnt = category_count*(int(set_start['수집_max'])-int(set_start['수집_min'])+1)
                    self.textEdit_box.append(f"검색 진행중 - [ 카테고리 : {category_num}/{category_count} ] [ 페이지 : {page_num}/{page_cnt} ] [ 총 {len(item_list)}개 검색완료 ]")
                    self.progressBar.setValue(int(page_num/(category_count*(int(set_start['수집_max'])-int(set_start['수집_min'])+1))*99))
                except:
                    pass
            elif time_bool_filtering == True:
                try:
                    self.textEdit_box.append(f"필터링 진행중")
                except:
                    pass
            elif time_bool_category == True:
                try:
                    self.textEdit_box.append(f"카테고리 분석중 - [ 카테고리 : {category_cnt}/{category_all}]")
                    self.progressBar.setValue(int(category_cnt/category_all)*99)
                except:
                    pass
            elif time_bool_product == True:
                try:
                    self.textEdit_box.append(f"상품 분석중 - [ 카테고리 : {product_cnt}/{product_all}]")
                    self.progressBar.setValue(int(product_cnt/product_all)*99)
                except:
                    pass
            elif time_bool_download == True:
                try:
                    self.textEdit_box.append(f"엑셀 다운로드 중 - 잠시만 기다려주세요.")
                except:
                    pass
            else:
                pass
        except:
            print("테이블 리셋 실패")
            pass
                    
    #검색 중지
    def stop_searching(self):
        global stop_bool
        global time_bool
        global dt_now
        msg = QMessageBox()
        

        reply = QMessageBox.question(self, '확인', f'검색을 중지하시겠습니까?\n검색 중지 후 잠시 기다린 후에 다음 작업을 진행해주세요.)',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            #중지버튼 비활성화

            dt_now = datetime.datetime.now()

            #모듈 로그 DB 입력
            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','검색 중지','{dt_now}');"
                cur_user.execute(sql)
            except:
                pass
            finally:
                con_user.commit()
                con_user.close()

            try:
                if premium_days == 0:
                    msg.setWindowTitle('알림')
                    msg.setText('프리미엄 기간이 종료되었습니다.\n블로그 후기를 작성해서 멤버쉽을 연장해보세요!')
                    msg.exec_()
                    return
                stop_bool = False
                time_bool = False

                self.pushButton.setEnabled(False)
                self.textEdit_box.append("검색이 중지되었습니다.")

            except:
                return


    #박스 리셋
    def reset_box(self):
        self.textEdit_box.clear()

    #구독하기
    def youtube(self):
        dt_now = datetime.datetime.now()

        #모듈 로그 DB 입력
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','사용방법','{dt_now}');"
            cur_user.execute(sql)
        except:
            pass
        finally:
            con_user.commit()
            con_user.close()

        msg = QMessageBox()
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT * FROM web_link WHERE button=%s;"
            cur_user.execute(sql, '구독하기')
            free_seven = cur_user.fetchall()
            webbrowser.open(free_seven[0][2])
        except:
            msg.setWindowTitle('알림')
            msg.setText('홈페이지 접속에 실패하였습니다.\n관리자에게 문의하세요.')
            msg.exec_()
            return

    #엑셀 다운로드
    def excel_download(self):
        #멀티쓰레드 가동
        global df
        global df_filter
        global item_category
        global check_searching
        global check_filtering
        global check_category
        global check_product
        global file_name
        global dt_now

        msg = QMessageBox()

        # 진행중일때 리턴
        if time_bool != False:
            msg.setWindowTitle('알림')
            msg.setText('검색 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_filtering != False:
            msg.setWindowTitle('알림')
            msg.setText('필터링 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_category != False:
            msg.setWindowTitle('알림')
            msg.setText('카테고리 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_product != False:
            msg.setWindowTitle('알림')
            msg.setText('상품 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_download != False:
            msg.setWindowTitle('알림')
            msg.setText('엑셀 다운로드 작업이 진행중입니다.')
            msg.exec_()
            return

        if check_searching != True:
            msg.setWindowTitle('알림')
            msg.setText('검색을 진행한 후 다시 시도해주세요.')
            msg.exec_()
            return    

        file_name = ''
        #EXCEL 파일로 저장하기
        try:
            file_name = QFileDialog.getSaveFileName(self, self.tr("검색결과"), "./", self.tr("엑셀 파일 (*.xlsx)"))
            #모듈 로그 DB 입력

            dt_now = datetime.datetime.now()

            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','엑셀 다운로드','{dt_now}');"
                cur_user.execute(sql)
            except:
                pass
            finally:
                con_user.commit()
                con_user.close()
            
            # print(file_name[0])
            if 'xlsx' in file_name[0]:
                thread = Thread5(self)
                thread.start()

        except:
            pass

    def table_update(self):
        global item_result_view

        msg = QMessageBox()

        # 진행중일때 리턴
        if time_bool != False:
            msg.setWindowTitle('알림')
            msg.setText('검색 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_filtering != False:
            msg.setWindowTitle('알림')
            msg.setText('필터링 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_category != False:
            msg.setWindowTitle('알림')
            msg.setText('카테고리 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_product != False:
            msg.setWindowTitle('알림')
            msg.setText('상품 분석 작업이 진행중입니다.')
            msg.exec_()
            return
        if time_bool_download != False:
            msg.setWindowTitle('알림')
            msg.setText('엑셀 다운로드 작업이 진행중입니다.')
            msg.exec_()
            return

        try:
            a = len(item_result_view)
        except:
            msg.setWindowTitle('알림')
            msg.setText('검색 버튼을 누른 후 다시 시도해주세요.')
            msg.exec_()
            return            

        if len(item_result_view) == 0:
            msg.setWindowTitle('알림')
            msg.setText('상품 검색 시 오류가 발생하였습니다.\n검색 버튼을 눌러 다시 시도해주세요.')
            msg.exec_()
            return

        try:
            self.tableWidget.setColumnCount(len(item_result_view.columns))

            #인덱스는 최대 100까지 허용
            if len(item_result_view.index) > 100:
                row_cnt = 100
            else:
                row_cnt = len(item_result_view.index)

            self.tableWidget.setRowCount(row_cnt)

            for i in range(0, 35):
                self.tableWidget.setColumnWidth(i, int(self.width()*1/20))

            for i in range(row_cnt):
                for j in range(len(item_result_view.columns)):
                    self.tableWidget.setItem(i,j,QTableWidgetItem(str(item_result_view.iloc[i, j])))
        except:
            pass

    def table_result(self):
        time.sleep(0.1)
        # self.tableWidget.repaint()
        self.progressBar.setValue(100)
        self.textEdit_box.append("검색 소요 시간 : %s초" % int(time.time() - start_time))
        self.textEdit_box.append("검색이 완료되었습니다.")
        self.textEdit_box.append("검색 결과 업데이트 버튼을 클릭하여 검색된 상품을 확인해주세요.")
        self.textEdit_box.append("아래 테이블에는 100개까지만 확인 가능하며, 엑셀 다운로드로 전체 데이터를 확인할 수 있습니다..")

        #중지버튼 비활성화
        self.pushButton.setEnabled(False)

    # @pyqtSlot()
    #시그널
    # def user_slot(self):
    #     print("2222")

    def table_result_filtering(self):
        time.sleep(0.1)
        try:
            self.progressBar.setValue(100)
            self.textEdit_box.append("금지어 필터링 소요 시간 : %s초" % int(time.time() - start_time))
            self.textEdit_box.append("금지어 필터링이 완료되었습니다.")
            #중지버튼 비활성화
            self.pushButton.setEnabled(False)
        except:
            msg = QMessageBox()
            msg.setWindowTitle('알림')
            msg.setText('작업이 완료되었습니다.')
            msg.exec_()
        finally:
            self.pushButton.setEnabled(False)

        
    def table_result_category(self):
        time.sleep(0.1)
        try:
            self.progressBar.setValue(100)
            self.textEdit_box.append("AI 카테고리 추천 소요 시간 : %s초" % int(time.time() - start_time))
            self.textEdit_box.append("AI 카테고리 추천이 완료되었습니다.")
            #중지버튼 비활성화
            self.pushButton.setEnabled(False)
        except:
            msg = QMessageBox()
            msg.setWindowTitle('알림')
            msg.setText('작업이 완료되었습니다.')
            msg.exec_()
        finally:
            self.pushButton.setEnabled(False)        
    def table_result_product(self):
        time.sleep(0.1)
        try:
            self.progressBar.setValue(100)
            self.textEdit_box.append("AI 상품 추천 소요 시간 : %s초" % int(time.time() - start_time))
            self.textEdit_box.append("AI 상품 추천이 완료되었습니다.")
            #중지버튼 비활성화
            self.pushButton.setEnabled(False)
        except:
            msg = QMessageBox()
            msg.setWindowTitle('알림')
            msg.setText('작업이 완료되었습니다.')
            msg.exec_()
        finally:
            self.pushButton.setEnabled(False)  

class Window_Keyword(QDialog, UI_Keyword):
    
    #기본 설정
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.show()
    
    #실행 설정
    def initUI(self):
        self.setWindowTitle("머슭상품")
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet(qdarktheme.load_stylesheet("light"))

    def complete_interface(self):
        msg = QMessageBox()
        #리스트 박스 내용
        keyword_content = self.textEdit_keyword.toPlainText()
        dt_now = datetime.datetime.now()
        keyword_date = dt_now.date()

        #DB에 금지어 등록
        reply = QMessageBox.question(self, '확인', '금지어 등록 제안을 진행하시겠습니까?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            if keyword_content == '':
                msg.setWindowTitle('알림')
                msg.setText('등록을 원하시는 키워드를 입력하신 후 다시 시도해주세요.')
                msg.exec_()
            else:
                #모듈 로그 DB 입력
                try:
                    con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                    cur_user = con_user.cursor()
                    sql = f"INSERT INTO module_log (id, button, date) VALUES ('{db_id}','금지어 등록','{dt_now}');"
                    cur_user.execute(sql)
                except:
                    pass
                finally:
                    con_user.commit()
                    con_user.close()
                try:
                    con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                    cur_user = con_user.cursor()
                    sql = f"INSERT INTO keyword_list (id, keyword, date) VALUES ('{db_id}','{keyword_content}','{keyword_date}');"
                    cur_user.execute(sql)
                    msg.setWindowTitle('알림')
                    msg.setText('금지어 등록이 완료되었습니다.\n적용은 2~3일의 검토를 거친 후 반영됩니다.')
                    msg.exec_()
                except:
                    msg.setWindowTitle('알림')
                    msg.setText('금지어 등록이 실패하였습니다.\n관리자에게 문의하세요.')
                    msg.exec_()
                finally:
                    con_user.commit()
                    con_user.close()

class Window_Free(QDialog, UI_Free):
    #기본 설정
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.show()
    
    #실행 설정
    def initUI(self):
        self.setWindowTitle("머슭상품")
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet(qdarktheme.load_stylesheet("light"))

    def complete_interface(self):
        maria = 0
        msg = QMessageBox()
        review_cnt = 0
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT * FROM check_login WHERE id=%s;"
            cur_user.execute(sql, db_id)
            review_sen = cur_user.fetchall()
            review_cnt = review_sen[0][5]
        except:
            msg.setWindowTitle('알림')
            msg.setText('버젼 확인에 실패하였습니다.\n관리자에게 문의하세요.')
            msg.exec_()
            return

        if review_cnt > 10:
            msg.setWindowTitle('알림')
            msg.setText('10회 이상 프리미엄 체험권을 받으셨기에 이용이 불가합니다.')
            msg.exec_()
            return

        review_link = self.lineEdit.text()
        dt_now = datetime.datetime.now()
        review_date = dt_now.date()
        if review_link == '':
            msg.setWindowTitle('알림')
            msg.setText('작성하신 블로그 본문 링크를 입력해주세요.')
            msg.exec_()
            return
        
        if review_link != '':
            reply = QMessageBox.question(self, '확인', '블로그 후기 입력을 진행하시겠습니까?\n임의의 링크를 입력할 시 프로그램 권한이 삭제됩니다.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                #블로그 후기 작성 DB에 링크 저장
                try:
                    con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                    cur_user = con_user.cursor()
                    sql = f"INSERT INTO review_list (id, link, give, date) VALUES ('{db_id}','{review_link}','1','{review_date}');"
                    cur_user.execute(sql)
                    maria = 1
                except:
                    msg.setWindowTitle('알림')
                    msg.setText('링크 입력에 실패하였습니다.\n관리자에게 문의하세요.')
                    msg.exec_()
                finally:
                    con_user.commit()
                    con_user.close()

                    if maria == 1:
                        try:
                            con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                            cur_user = con_user.cursor()
                            #프로그램 버젼 확인
                            sql = "UPDATE check_login SET review=review+1 WHERE id=%s;"
                            cur_user.execute(sql, db_id)

                            msg.setWindowTitle('알림')
                            msg.setText('후기 링크 입력이 성공적으로 처리되었습니다.')
                            msg.exec_()
                        except:
                            msg.setWindowTitle('알림')
                            msg.setText('후기 링크 입력이 실패하였습니다.')
                            msg.exec_()
                            pass
                        finally:
                            con_user.commit()
                            con_user.close()
        else:
            msg.setWindowTitle('알림')
            msg.setText('전체 주소를 입력해주세요. ex) http:...')
            msg.exec_()

    #3일 무료체험 공지글 확인하기
    def check_free(self):
        msg = QMessageBox()
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT * FROM web_link WHERE button=%s;"
            cur_user.execute(sql, '3일 무료체험')
            free_seven = cur_user.fetchall()
            webbrowser.open(free_seven[0][2])
        except:
            msg.setWindowTitle('알림')
            msg.setText('홈페이지 접속에 실패하였습니다.\n관리자에게 문의하세요.')
            msg.exec_()
            return

class Window_Recommend(QDialog, UI_Recommend):
    
    #기본 설정
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.show()
    
    #실행 설정
    def initUI(self):
        self.setWindowTitle("머슭상품")
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet(qdarktheme.load_stylesheet("light"))

    def complete_interface(self):
        msg = QMessageBox()
        recommend_cnt = 0
        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT * FROM check_login WHERE id=%s;"
            cur_user.execute(sql, db_id)
            recommend_sen = cur_user.fetchall()
            recommend_cnt = recommend_sen[0][6]
        except:
            msg.setWindowTitle('알림')
            msg.setText('버젼 확인에 실패하였습니다.\n관리자에게 문의하세요.')
            msg.exec_()
            return

        if recommend_cnt > 0:
            msg.setWindowTitle('알림')
            msg.setText('이미 추천인 혜택을 사용하셨기에 이용이 불가합니다.')
            msg.exec_()
            return

        recommend_code = self.lineEdit.text()

        if recommend_code == '':
            msg.setWindowTitle('알림')
            msg.setText('추천인 코드를 입력해주세요.')
            msg.exec_()
            return

        try:
            con_user = pymysql.connect(host='3.39.22.73', user='young_read', password='0000', db='trend', charset='utf8')
            cur_user = con_user.cursor()
            sql = "SELECT * FROM recommend WHERE code=%s;"
            cur_user.execute(sql, recommend_code)
            recommend_sen = cur_user.fetchall()
            check_rec_cnt = recommend_sen[0][2]
        except:
            msg.setWindowTitle('알림')
            msg.setText('추천인 코드가 일치하지 않습니다.\n다시 입력해주세요.')
            msg.exec_()
            return
        # print(check_rec_cnt)
        # print(recommend_code)
        if check_rec_cnt == recommend_code:
            try:
                con_user = pymysql.connect(host='3.39.22.73', user='young_write', password='0000', db='trend', charset='utf8')
                cur_user = con_user.cursor()
                #프로그램 버젼 확인
                sql = "UPDATE recommend SET cnt=cnt+1 WHERE code=%s;"
                cur_user.execute(sql, recommend_code)
                sql = "UPDATE check_login SET recommend=recommend+1 WHERE id=%s;"
                cur_user.execute(sql, db_id)
                sql = f"UPDATE check_login SET premium=DATE_ADD(premium, interval 7 DAY) WHERE id='{db_id}';"
                cur_user.execute(sql)
                con_user.commit()
                con_user.close()

                msg.setWindowTitle('알림')
                msg.setText('프리미엄 잔여일수가 7일 연장되었습니다.')
                msg.exec_()
            except:
                msg.setWindowTitle('알림')
                msg.setText('버젼 확인에 실패하였습니다.\n관리자에게 문의주세요.')
                msg.exec_()       
                con_user.close()   
        else:
            msg.setWindowTitle('알림')
            msg.setText('입력한 추천인 코드와 일치하는 코드가 없습니다.')
            msg.exec_()
            return    

if __name__ == "__main__":
    app = QApplication(sys. argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont('KoPubWorld Dotum Bold.ttf')
    fontDB.addApplicationFont('KoPubWorld Dotum Light.ttf')
    fontDB.addApplicationFont('KoPubWorld Dotum Medium.ttf')
    # app.setFont((QFont('KoPubWorld Dotum Medium.ttf')))
    Window = Window_Login()
    app.exec_()