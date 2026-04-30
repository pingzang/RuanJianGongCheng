# code:utf-8
import os
import numpy as np
import random as ra
from datetime import datetime

# 祈愿币文件路径（独立管理抽卡资源）
MANA_FILE = 'mana_counter.npy'
# 抽卡计数文件路径（保底计数）
COUNTER_FILE = 'pull_counter.npy'
# 初始祈愿币数量
INIT_MANA = 10


# 初始化文件路径
def init_file():
    picpath = os.path.join(os.getcwd(), 'pic')
    if not os.path.isdir(picpath):
        os.mkdir("pic")
    save_video = os.path.join(os.getcwd(), 'video')
    if not os.path.isdir(save_video):
        os.mkdir("video")
    return picpath, save_video


# 初始化/读取卡池（卡池数量固定，不随抽卡变化）
def read_card_pool():
    picpath, _ = init_file()
    
    # 读取卡池文件（仅存储卡池列表，不关联祈愿币）
    if os.path.isfile('card_pool.npy'):
        card_pool = np.load('card_pool.npy')
        pool_size = len(card_pool)
    else:
        print('初始化新卡池...')
        pool_size, pic_files = list_pic(picpath)
        if pool_size == 0:
            raise ValueError("卡池为空！请在pic文件夹中放入图片文件")
        card_pool = np.array(pic_files)
        np.save('card_pool.npy', card_pool)
    
    # 初始化/读取祈愿币（独立的抽卡资源）
    if os.path.isfile(MANA_FILE):
        mana = int(np.load(MANA_FILE).item())
    else:
        mana = INIT_MANA
        np.save(MANA_FILE, np.array(mana))
    
    return card_pool, pool_size, mana


# 强制更新卡池（仅刷新卡池列表，不影响祈愿币）
def renew_card_pool():
    picpath, _ = init_file()
    if os.path.isfile('card_pool.npy'):
        os.remove('card_pool.npy')
    pool_size, pic_files = list_pic(picpath)
    if pool_size == 0:
        raise ValueError("卡池为空！请在pic文件夹中放入图片文件")
    card_pool = np.array(pic_files)
    np.save('card_pool.npy', card_pool)
    # 祈愿币保持不变
    mana = np.load(MANA_FILE).item() if os.path.isfile(MANA_FILE) else INIT_MANA
    return card_pool, pool_size, mana

def read_num():
    card_pool, pool_size, mana = read_card_pool()
    return card_pool, mana

# 消耗祈愿币（抽卡前检查并扣除）
def consume_mana():
    if not os.path.isfile(MANA_FILE):
        np.save(MANA_FILE, np.array(INIT_MANA))
    
    mana = int(np.load(MANA_FILE).item())
    if mana <= 0:
        return False, 0
    
    # 扣除1个祈愿币
    mana -= 1
    np.save(MANA_FILE, np.array(mana))
    return True, mana


# 获得抽到的卡（带保底机制，卡池数量固定）
def gachi_card_out():
    # 1. 读取卡池和祈愿币
    try:
        card_pool, pool_size, current_mana = read_card_pool()
    except ValueError as e:
        print(e)
        return "", -1
    
    # 2. 检查并消耗祈愿币
    can_pull, new_mana = consume_mana()
    if not can_pull:
        print("错误：祈愿币不足，无法抽卡")
        return "", -1
    
    # 3. 读取保底计数
    if os.path.isfile(COUNTER_FILE):
        pull_counter = int(np.load(COUNTER_FILE).item())
    else:
        pull_counter = 0
    
    # 4. 判断保底（20抽未出金则保底）
    is_guaranteed = (pull_counter >= 19)  # 第20抽保底
    if is_guaranteed:
        star_level = 5
        print(f"保底触发！第{pull_counter + 1}抽必出五星")
    else:
        # 正常概率抽卡：五星10%，四星30%，三星60%
        rand = ra.random()
        if rand < 0.1:
            star_level = 5
        elif rand < 0.4:
            star_level = 4
        else:
            star_level = 3
    
    # 5. 根据星级筛选卡片（卡池不变，仅筛选）
    star_pics = []
    for f in card_pool:
        if star_level == 3 and 'star3' in f.lower():
            star_pics.append(f)
        elif star_level == 4 and 'star4' in f.lower():
            star_pics.append(f)
        elif star_level == 5 and 'star5' in f.lower():
            star_pics.append(f)
    
    # 兜底：如果对应星级无卡片，随机选一张
    if not star_pics:
        star_pics = list(card_pool)
        print(f"警告：未找到{star_level}星卡片，从卡池随机选取")
    
    # 6. 随机选取卡片（卡池数量不变）
    selected_pic = ra.choice(star_pics)
    initpic = list(card_pool).index(selected_pic)
    picname = card_pool[initpic]
    
    # 7. 更新保底计数（出五星重置，否则+1）
    if star_level == 5:
        pull_counter = 0
    else:
        pull_counter += 1
    np.save(COUNTER_FILE, np.array(pull_counter))
    
    # 8. 记录抽卡历史
    star_text = {3: '三星', 4: '四星', 5: '五星'}
    record_line = (
        f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] '
        f'抽到：{picname} ({star_text[star_level]})'
        f'{" [保底]" if is_guaranteed else ""} | 剩余祈愿币：{new_mana}\n'
    )
    
    if os.path.isfile('receive_card.npy'):
        receive = np.load('receive_card.npy')
        receive = np.append(receive, record_line)
    else:
        receive = np.array([record_line])
    np.save('receive_card.npy', receive)
    
    # 9. 输出结果
    picpath, _ = init_file()
    picdir = os.path.join(picpath, picname)
    print(f"抽卡结果：{picname} ({star_text[star_level]}) | 剩余祈愿币：{new_mana}")
    return picdir, initpic


# 抽卡背景视频播放（仅随机选视频，不影响卡池/祈愿币）
def gachi_v_out():
    picpath, _ = init_file()
    count_video, video_files = list_video(picpath)
    if count_video == 0:
        print("错误：无视频文件")
        return ""
    initpic = ra.randint(0, count_video - 1)
    picname = video_files[initpic]
    picdir = os.path.join(picpath, picname)
    print(f"背景视频：{picdir}")
    return picdir


# 获取本地图片文件（卡池素材）
def list_pic(picpath):
    print("获取图片文件...")
    files = os.listdir(picpath)
    pic_files = []
    for f in files:
        file_path = os.path.join(picpath, f)
        if os.path.isdir(file_path):
            continue
        ext = get_file_ext(f).lower()
        if ext in ['.jpg', '.jpeg', '.png']:
            pic_files.append(f)
    count_pic = len(pic_files)
    print(f"找到{count_pic}张图片")
    return count_pic, pic_files


# 获取本地视频文件（背景素材）
def list_video(videopath):
    print("获取视频文件...")
    files = os.listdir(videopath)
    video_files = []
    for f in files:
        file_path = os.path.join(videopath, f)
        if os.path.isdir(file_path):
            continue
        ext = get_file_ext(f).lower()
        if ext == '.mp4':
            video_files.append(f)
    count_video = len(video_files)
    print(f"找到{count_video}个视频")
    return count_video, video_files


# 获取文件后缀
def get_file_ext(file_name):
    dot_pos = file_name.rfind('.')
    return file_name[dot_pos:] if dot_pos != -1 else ''


# 手动重置祈愿币
def reset_mana(mana_num=INIT_MANA):
    np.save(MANA_FILE, np.array(mana_num))
    print(f"祈愿币已重置为：{mana_num}")
    return mana_num


# 手动重置保底计数
def reset_pull_counter():
    np.save(COUNTER_FILE, np.array(0))
    print("保底计数已重置")