import sqlite3
DB_NAME = "game_data.db"

def get_connection():
    """获取数据库连接（和database.py保持一致）"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def parse_card_records(username):
    """
    从数据库解析用户抽卡记录
    返回：五星间隔列表、四星间隔列表、五星总数、四星总数、总抽数
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 查询该用户所有抽卡记录（按时间排序）
    cursor.execute("""
        SELECT card_star FROM gacha_history 
        WHERE username = ? 
        ORDER BY draw_time ASC
    """, (username,))
    records = cursor.fetchall()
    conn.close()
    
    if not records:
        return [], [], 0, 0, 0
    
    # 提取星级列表
    star_list = [r["card_star"] for r in records]
    total = len(star_list)
    
    # 计算五星/四星间隔
    five_star_intervals = []  # 五星间隔列表
    four_star_intervals = []  # 四星间隔列表
    last_5_idx = -1
    last_4_idx = -1
    
    for idx, star in enumerate(star_list):
        if star == 5:
            if last_5_idx != -1:
                five_star_intervals.append(idx - last_5_idx)
            last_5_idx = idx
        elif star == 4:
            if last_4_idx != -1:
                four_star_intervals.append(idx - last_4_idx)
            last_4_idx = idx
    
    # 统计五星/四星总数
    cnt5 = star_list.count(5)
    cnt4 = star_list.count(4)
    
    return five_star_intervals, four_star_intervals, cnt5, cnt4, total

def judge_eu_non(iv5, iv4, cnt5, cnt4, total):
    """
    判断欧非等级，返回：等级、统计字典
    """
    stats = {
        "总抽数": total,
        "五星数量": cnt5,
        "四星数量": cnt4,
        "五星真实概率(%)": (cnt5/total)*100 if total > 0 else 0,
        "四星真实概率(%)": (cnt4/total)*100 if total > 0 else 0,
        "五星间隔列表": iv5 if iv5 else ["无"],
        "四星间隔列表": iv4 if iv4 else ["无"],
        "五星平均间隔": sum(iv5)/len(iv5) if iv5 else 0,
        "四星平均间隔": sum(iv4)/len(iv4) if iv4 else 0
    }
    
    # 真实概率 = 数量 / 总抽数
    rate5 = (cnt5 / total) * 100 if total > 0 else 0
    rate4 = (cnt4 / total) * 100 if total > 0 else 0

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
    
    return grade, stats