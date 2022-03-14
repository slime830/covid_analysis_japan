import argparse
import datetime
import os
import re
import shutil
import sys

import japanize_matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm


def get_data():
    # 日別の新規感染者データ
    confirmed_df = pd.read_csv(
        "https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv"
    )
    # 日別の重症者数データ
    severe_df = pd.read_csv(
        "https://covid19.mhlw.go.jp/public/opendata/severe_cases_daily.csv"
    )
    # 都道府県のset
    prefectures = list(confirmed_df.columns)
    prefectures.remove("Date")

    return confirmed_df, severe_df, prefectures


def data_processing(confirmed_df, severe_df, start_date="2020/5/9"):
    # severe_DF starts 2020/5/9
    assert start_date in list(confirmed_df.Date)
    assert start_date in list(severe_df.Date)

    confirmed_df = confirmed_df[
        confirmed_df.index >= list(confirmed_df.Date).index(start_date)
    ]
    severe_df = severe_df[severe_df.index >= list(severe_df.Date).index(start_date)]

    return confirmed_df, severe_df


def cal_severe_rate(confirmed_df, severe_df, prefectures, error_num=100):
    confirms = {
        prefecture: list(confirmed_df[prefecture]) for prefecture in prefectures
    }
    severes = {prefecture: list(severe_df[prefecture]) for prefecture in prefectures}
    rates = {
        prefecture: [
            severe / confirm if confirm != 0 else error_num
            for severe, confirm in zip(
                severes.get(prefecture), confirms.get(prefecture)
            )
        ]
        for prefecture in confirms.keys()
    }

    return confirms, severes, rates


def get_date():
    d = datetime.datetime.now()
    return str(d.year) + "/" + str(d.month) + "/" + str(d.day)


def plot_data(data, prefecture, genre, axes, start_date):
    axes.plot(
        pd.date_range(
            start_date.replace("/", "-") + " 00:00:00", periods=len(data), freq="d"
        ),
        data,
    )
    if genre == "重症率":
        axes.set_ylim([0, 1])  # だいたいは(重症者数)<(新規感染者数)の為
    axes.grid()
    axes.set_title(
        start_date.replace("/", "-")
        + "から"
        + get_date().replace("/","-")
        + "までの"
        + genre
        + "の推移("
        + prefecture
        + ")",
        fontsize=18,
    )
    axes.set_xlabel("日付", fontsize=18)
    axes.set_ylabel(genre, fontsize=18)


def draw_graph(confirm, severe, rate, prefecture, output_dirname, start_date):
    subplot_num = 311
    figure = plt.figure(1, figsize=(20, 25))
    genres = ["新規感染者数", "重症者数", "重症率"]
    for data, genre in zip([confirm, severe, rate], genres):
        plot_data(data, prefecture, genre, figure.add_subplot(subplot_num), start_date)
        subplot_num += 1

    # plt.savefig(f"{output_dirname}{prefecture}.png")
    plt.savefig(os.path.join(output_dirname, prefecture + ".png"))
    plt.close()


def draw_and_save_all_graphs(
    c_dict, s_dict, r_dict, prefectures, output_dirname, start_date="2020/5/9"
):
    if os.path.isdir(output_dirname):
        shutil.rmtree(output_dirname)

    os.makedirs(output_dirname)

    for prefecture in tqdm(prefectures):
        # print(p)
        confirm = c_dict.get(prefecture)
        severe = s_dict.get(prefecture)
        rate = r_dict.get(prefecture)
        draw_graph(confirm, severe, rate, prefecture, output_dirname, start_date)


def check_date(date_string):
    pattern = r"202\d\/\d+\/\d+"
    mutches = re.findall(pattern, date_string)
    if len(mutches) != 1:
        return False

    return date_string == mutches[0]


def main(args):
    if not check_date(args.start_date):
        print("format violation from start_date")
        sys.exit()

    start_date = args.start_date
    error_num = args.error_num
    output_dirname = args.output

    confirmed_df, severe_df, prefectures = get_data()
    confirmed_df, severe_df = data_processing(confirmed_df, severe_df, start_date)
    confirms, severes, rates = cal_severe_rate(
        confirmed_df, severe_df, prefectures, error_num
    )
    draw_and_save_all_graphs(
        confirms, severes, rates, prefectures, output_dirname, start_date
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, help="出力先のディレクトリ", default="./images/")
    parser.add_argument("--error_num", type=int, help="新規感染者数が0だった時の重症率の値", default=100)
    parser.add_argument("--start_date", type=str, help="描画を開始する日付", default="2020/5/9")
    main(parser.parse_args())
