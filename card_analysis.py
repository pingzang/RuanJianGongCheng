import numpy as np
import re

def parse_card_records(file_path="receive_card.npy"):
    try:
        records = np.load(file_path, allow_pickle=True).tolist()
    except FileNotFoundError:
        print(f"错误：未找到{file_path}文件")
        return [], [], 0, 0

    # 间隔统计（你要的核心：两个五星之间隔了几抽）
    star5_intervals = []
    star4_intervals = []
    
    total_draws = len(records)
    last_5 = 0  # 上一次五星位置
    last_4 = 0  # 上一次四星位置

    for idx, record in enumerate(records):
        current_draw = idx + 1  # 当前是第几抽
        
        # 判断星级（以文件名为准）
        if "star5" in record:
            if last_5 != 0:
                interval = current_draw - last_5
                star5_intervals.append(interval)
            last_5 = current_draw

        if "star4" in record:
            if last_4 != 0:
                interval = current_draw - last_4
                star4_intervals.append(interval)
            last_4 = current_draw

    # 统计总数量
    count5 = sum(1 for r in records if "star5" in r)
    count4 = sum(1 for r in records if "star4" in r)

    return star5_intervals, star4_intervals, count5, count4, total_draws


def judge_eu_non(intervals5, intervals4, count5, count4, total_draws):
    if total_draws == 0:
        return "无数据", {}

    # 真实概率 = 数量 / 总抽数
    rate5 = (count5 / total_draws) * 100 if total_draws > 0 else 0
    rate4 = (count4 / total_draws) * 100 if total_draws > 0 else 0

    # 欧非判定（按真实概率）
    if rate5 >= 12 and rate4 >= 33:
        grade = "大欧皇"
    elif rate5 >= 10 or rate4 >= 30:
        grade = "小欧皇"
    elif 7 <= rate5 < 10 or 25 <= rate4 < 30:
        grade = "普通人"
    elif 4 <= rate5 < 7 or 20 <= rate4 < 25:
        grade = "小非酋"
    else:
        grade = "大非酋"

    # 平均间隔
    avg5 = np.mean(intervals5) if intervals5 else 0
    avg4 = np.mean(intervals4) if intervals4 else 0

    stats = {
        "总抽数": total_draws,
        "五星数量": count5,
        "四星数量": count4,
        "五星真实概率(%)": round(rate5, 2),
        "四星真实概率(%)": round(rate4, 2),
        "五星间隔列表": intervals5,
        "四星间隔列表": intervals4,
        "五星平均间隔": round(avg5, 1) if avg5 !=0 else "无",
        "四星平均间隔": round(avg4, 1) if avg4 !=0 else "无",
        "理论五星概率(%)": 10,
        "理论四星概率(%)": 30,
    }
    return grade, stats