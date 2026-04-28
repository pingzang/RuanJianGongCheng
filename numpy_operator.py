# code:utf-8
import os
import numpy as np
import random as ra
# 存放一些与本地相关的操作函数
from datetime import datetime


# 初始化读取本地文件
def read_num():
    picpath, save_video = init_file()

    if os.path.isfile('picnum1.npy'):
        # print('remove old now')
        # os.remove('picnum1.npy')
        print('YES,get num')
        pic = np.load('picnum1.npy')
        # print(pic)
        count_pic = len(pic)
        if count_pic > 0:
            # 应该返回的重要数值有 图片数组 抽到的路径 图片的数组位置 当前图片数量
            return pic, count_pic
        else:
            print('remove old now')
            os.remove('picnum1.npy')
            print('create num now')
            count_pic, pic_files = list_pic(picpath)
            pic = np.array(pic_files)

            # 修改这里：可以设置一个自定义的初始玛娜数
            # 例如设置为 100
            INIT_MANA = 100  # 你想要的数量
            if INIT_MANA > count_pic:
                # 如果自定义值超过图片数量，就使用图片数量
                return pic, count_pic
            else:
                # 只取前INIT_MANA张图片作为初始卡池
                pic = pic[:INIT_MANA]
                np.save('picnum1.npy', pic)
                return pic, len(pic)

            # 应该返回的重要数值有 图片数组 抽到的路径 当前图片数量
            return pic, count_pic

    elif not os.path.isfile('picnum1.npy'):
        print('create num now')
        count_pic, pic_files = list_pic(picpath)
        pic = np.array(pic_files)

        # 同样在这里设置初始玛娜数
        INIT_MANA = 100
        if INIT_MANA < count_pic:
            pic = pic[:INIT_MANA]
            np.save('picnum1.npy', pic)
            return pic, len(pic)
            
        # 应该返回的重要数值有 图片数组 抽到的路径 当前图片数量
        return pic, count_pic


# 强制更新
def renew_num():
    picpath, save_video = init_file()
    if os.path.isfile('picnum1.npy'):
        print('remove old now')
        os.remove('picnum1.npy')
        print('create num now')
        count_pic, pic_files = list_pic(picpath)
        pic = np.array(pic_files)
        # 应该返回的重要数值有 图片数组 抽到的路径 当前图片数量
        return pic, count_pic

    elif not os.path.isfile('picnum1.npy'):
        print('create num now')
        count_pic, pic_files = list_pic(picpath)
        pic = np.array(pic_files)
        # 应该返回的重要数值有 图片数组 抽到的路径 当前图片数量
        return pic, count_pic


# # 获得抽到的卡
# def gachi_card_out(pic, count_pic):
#     picpath, save_video = init_file()
#     try:
#         initpic = int(ra.randint(0, count_pic - 1))
#     except:
#         initpic = 0
#     picname = pic[initpic]

#     if os.path.isfile('receive_card.npy'):
#         print('YES,get the record')
#         receive = np.load('receive_card.npy')
#         str0 = '创建时间：(UTC+8)' + str(datetime.now()) + '\n'
#         str1 = '本次抽到的图片为:' + picname + '\n' + '当前玛娜值' + str(count_pic) + '\n'
#         receive = np.append(receive, str0)
#         receive = np.append(receive, str1)
#         # print(receive)
#         np.save('receive_card.npy', receive)

#     else:
#         print('creative a record')
#         strs = []
#         str0 = '创建时间：(UTC+8)' + str(datetime.now()) + '\n'
#         str1 = '本次抽到的图片为:' + picname + '\n' + '当前玛娜值' + str(count_pic) + '\n'
#         strs.append(str0)
#         receive = np.array(strs)
#         receive = np.append(receive, str1)
#         np.save('receive_card.npy', receive)

#     print(picname)
#     picdir = picpath + '\\' + picname
#     print(picdir)
#     return picdir, initpic

# 抽卡计数文件路径
COUNTER_FILE = 'pull_counter.npy'

# 获得抽到的卡（带保底机制）
def gachi_card_out(pic, count_pic):
    picpath, save_video = init_file()
    
    # 读取当前抽卡计数（距离上次出金已抽次数）
    if os.path.isfile(COUNTER_FILE):
        pull_counter = int(np.load(COUNTER_FILE).item())
    else:
        pull_counter = 0
    
    # 判断是否为保底（20抽未出金则保底）
    is_guaranteed = (pull_counter >= 19)  # 第20抽保底
    
    if is_guaranteed:
        # 保底出五星
        star_level = 5
        print(f"保底触发！第{pull_counter + 1}抽必出五星")
    else:
        # 正常概率抽卡：五星10%，四星30%，三星60%
        rand = ra.random()  # 0.0 ~ 1.0
        if rand < 0.1:      # 10% 五星
            star_level = 5
        elif rand < 0.4:    # 30% 四星 (0.1~0.4)
            star_level = 4
        else:               # 60% 三星 (0.4~1.0)
            star_level = 3
    
    # 根据星级筛选对应的图片
    star_pics = []
    for f in pic:
        # 文件名包含星级标识
        if star_level == 3 and ('三星' in f or '3星' in f or 'star3' in f):
            star_pics.append(f)
        elif star_level == 4 and ('四星' in f or '4星' in f or 'star4' in f):
            star_pics.append(f)
        elif star_level == 5 and ('五星' in f or '5星' in f or 'star5' in f):
            star_pics.append(f)
    
    # # 如果没有匹配星级的图片，则从所有图片中随机选
    # if not star_pics:
    #     star_pics = list(pic)
    #     print(f"警告：未找到星级{star_level}对应的图片，从全部中随机")
    
    # 从对应星级图片中随机选一张
    try:
        selected_pic = ra.choice(star_pics)
        initpic = list(pic).index(selected_pic)
    except:
        initpic = 0
    
    picname = pic[initpic]
    
    # 更新抽卡计数（出金重置，否则+1）
    if star_level == 5:
        pull_counter = 0
    else:
        pull_counter += 1
    np.save(COUNTER_FILE, np.array(pull_counter))
    
    # 记录抽卡历史
    star_text = {3: '三星', 4: '四星', 5: '五星'}
    record_line = f'抽到：{picname} ({star_text[star_level]})' + (' [保底]' if is_guaranteed else '') + f' | 剩余玛娜：{count_pic-1}\n'
    
    if os.path.isfile('receive_card.npy'):
        receive = np.load('receive_card.npy')
        receive = np.append(receive, record_line)
        np.save('receive_card.npy', receive)
    else:
        receive = np.array([record_line])
        np.save('receive_card.npy', receive)
    
    print(f"抽卡结果：{picname} ({star_text[star_level]})")
    picdir = picpath + '\\' + picname
    return picdir, initpic




# 抽卡背景视频播放
def gachi_v_out(pic, count_pic, picpath):
    try:
        initpic = int(ra.randint(0, count_pic - 1))
    except:
        initpic = 0
    picname = pic[initpic]
    print(picname)
    picdir = picpath + '\\' + picname
    print(picdir)
    return picdir


# 初始化文件路径
def init_file():
    picpath = os.getcwd() + '\\' + 'pic'
    if not os.path.isdir(picpath):
        os.mkdir("pic")
    save_video = os.getcwd() + '\\' + 'video'
    if not os.path.isdir(save_video):
        os.mkdir("video")
    return picpath, save_video


# 获取本地文件图片
def list_pic(picpath):
    print("Get image files ... ", end='\n')

    files = os.listdir(picpath)
    print(files, end='\n')
    pic_files = []

    for f in files:
        if os.path.isdir(f):
            continue

        if get_file_ext(f).lower() == '.jpg':
            pic_files.append(f)

        if get_file_ext(f).lower() == '.jpeg':
            pic_files.append(f)

        if get_file_ext(f).lower() == '.png':
            pic_files.append(f)

    count_pic = len(pic_files)
    print("%s found" % count_pic)
    print(picpath, end='\n')
    return count_pic, pic_files


# 获取文件后缀
def get_file_ext(file_name):
    dot_pos = file_name.rfind('.')
    if dot_pos == -1:
        ext = ''
    else:
        ext = file_name[dot_pos:]

    return ext


# 获取本地文件视频
def list_video(picpath):
    files = os.listdir(picpath)
    print(files, end='\n')
    pic_files = []

    for f in files:
        if os.path.isdir(f):
            continue

        if get_file_ext(f).lower() == '.mp4':
            pic_files.append(f)

    count_pic = len(pic_files)
    print("%s found" % count_pic)
    print(picpath, end='\n')
    return count_pic, pic_files


