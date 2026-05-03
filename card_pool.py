# 卡池配置：key为星级，value为对应卡片列表
CARD_POOL = {
    5: [
        {"name": "大开门", "star": 5, "color": "金色", "pic_path": "pic/star5_1.jpg"},
        {"name": "双箭头", "star": 5, "color": "金色", "pic_path": "pic/star5_2.png"},
        {"name": "忘本猫", "star": 5, "color": "金色", "pic_path": "pic/star5_3.png"}
    ],
    4: [
        {"name": "oiia猫", "star": 4, "color": "紫色", "pic_path": "pic/star4_1.jpg"},
        {"name": "香蕉猫", "star": 4, "color": "紫色", "pic_path": "pic/star4_2.jpg"},
        {"name": "Huh猫", "star": 4, "color": "紫色", "pic_path": "pic/star4_3.jpg"},
        {"name": "听泉猫", "star": 4, "color": "紫色", "pic_path": "pic/star4_4.png"},
        {"name": "蛛猫", "star": 4, "color": "紫色", "pic_path": "pic/star4_5.png"},
        {"name": "抱头尖叫猫", "star": 4, "color": "紫色", "pic_path": "pic/star4_6.png"},
        {"name": "大笑猫", "star": 4, "color": "紫色", "pic_path": "pic/star4_7.png"}
    ],
    3: [
        {"name": "猫粮", "star": 3, "color": "蓝色", "pic_path": "pic/star3_1.jpg"},
        {"name": "毛线", "star": 3, "color": "蓝色", "pic_path": "pic/star3_2.jpg"}
    ]
}

# 抽卡概率配置
GACHA_PROB = {
    5: 0.1,   # 五星概率10%
    4: 0.3,   # 四星概率30%
    3: 0.6    # 三星概率60%
}

# 保底配置
PITY_GUARANTEE = 20  # 20抽保底五星