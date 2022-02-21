import datetime
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
import shutil
import sys



plt.rcParams['font.family'] = "MS Mincho"
plt.rcParams["font.size"]=18

#日別の新規感染者データ
confirmed_DF=pd.read_csv("https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv")
#日別の重症者数データ
severe_DF=pd.read_csv("https://covid19.mhlw.go.jp/public/opendata/severe_cases_daily.csv")
#都道府県のset
prefectures=list(confirmed_DF.columns)
prefectures.remove("Date")

def dataProcessing():
    # severe_DF starts 2020/5/9
    global confirmed_DF
    index=0
    for i in range(len(confirmed_DF)):
        if confirmed_DF.Date[i]=="2020/5/9":
            index=i
            break
    confirmed_DF=confirmed_DF.drop(confirmed_DF.index[0:index]).reset_index(drop=True)

def calSevereRate():
    confirms={prefecture:list(confirmed_DF[prefecture]) for prefecture in prefectures}
    severes={prefecture:list(severe_DF[prefecture])for prefecture in prefectures}
    rates={prefecture:[severe/confirm if confirm!=0 else 100 for severe,confirm in zip(severes.get(prefecture),confirms.get(prefecture))]for prefecture in confirms.keys()}

    return confirms,severes,rates

def getDate():
    d=datetime.datetime.now()
    return str(d.year)+"-"+str(d.month)+"-"+str(d.day)

def drawGraph(data,genre,pre,axes):
    genre_jpn=""
    if genre=="severe_rate":
        genre_jpn="重症率"
    elif genre=="confirm":
        genre_jpn="新規感染者数"
    elif genre=="severe":
        genre_jpn="重症者数"

    axes.plot(pd.date_range('2020-05-09 00:00:00', periods=len(data), freq='d'),data)
    # plt.xticks(np.arange(0,len(data),30))
    if genre=="severe_rate":
        axes.set_ylim([0,1])#だいたいは(重症者数)<(新規感染者数)の為
    axes.grid()
    axes.set_title("2020-5-9から"+getDate()+"までの"+genre_jpn+"の推移("+pre+")")
    axes.set_xlabel("日付")
    

def drawAndSaveAllGraphs(c_dict,s_dict,r_dict,output_dirname):
    if os.path.isdir(output_dirname):
        shutil.rmtree(output_dirname)
    
    os.makedirs(output_dirname)

    for p in tqdm(c_dict.keys()):
        # print(p)
        confirm=c_dict.get(p)
        severe=s_dict.get(p)
        rate=r_dict.get(p)
        figure= plt.figure(1, figsize=(20,25))
        ax = figure.add_subplot(311)
        drawGraph(confirm,"confirm",p,ax)
        ax = figure.add_subplot(312)
        drawGraph(severe,"severe",p,ax)
        ax = figure.add_subplot(313)
        drawGraph(rate,"severe_rate",p,ax)
        plt.savefig("images/"+p+".png")
        plt.close()

def main():
    output_dirname="./images"
    dataProcessing()
    confirms,severes,rates=calSevereRate()
    drawAndSaveAllGraphs(confirms,severes,rates,output_dirname)

if __name__ == "__main__":
    main()
