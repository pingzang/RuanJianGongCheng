# card_collection.py
import streamlit as st
import os
from collection_utils import load_received_cards, get_card_image_path, load_card_image

# ---------------------- 配置项（需根据项目修改） ----------------------
CONFIG = {
    "all_cards": ["card_01", "card_02", "card_03", "card_04", "card_05"],  # 全卡牌ID列表
    "card_img_dir": "card_images/",  # 原有卡牌图片目录
    "placeholder_img": "unlocked_placeholder.png",  # 未获得卡牌占位图
    "error_img": "default_error.png",  # 图片加载失败兜底图（可选）
    "npy_path": "receive_card.npy",  # 原有抽卡记录文件路径
    "columns_num": 5,  # 图鉴每行显示列数
    "page_title": "卡牌图鉴"
}

# ---------------------- 页面初始化 ----------------------
st.set_page_config(page_title=CONFIG["page_title"], page_icon="🎴", layout="wide")
st.title(CONFIG["page_title"])

# ---------------------- 核心逻辑 ----------------------
# 1. 读取已获得卡牌
received_cards = load_received_cards(CONFIG["npy_path"])

# 2. 渲染图鉴网格
cols = st.columns(CONFIG["columns_num"])
for idx, card_id in enumerate(CONFIG["all_cards"]):
    col = cols[idx % CONFIG["columns_num"]]
    with col:
        # 卡牌标题
        st.subheader(f"卡牌{idx+1}")
        # 获取图片路径
        img_path = get_card_image_path(
            card_id=card_id,
            received_cards=received_cards,
            card_img_dir=CONFIG["card_img_dir"],
            placeholder_img=CONFIG["placeholder_img"]
        )
        # 加载并显示图片
        img = load_card_image(img_path, CONFIG["error_img"])
        if img:
            st.image(img, use_column_width=True)
        else:
            st.write("⚠️ 图片资源缺失")
        # 显示状态
        status = "已获得" if card_id in received_cards else "未获得"
        st.caption(f"状态：{status}")

# ---------------------- 辅助信息 ----------------------
st.sidebar.header("图鉴统计")
st.sidebar.metric("已收集", f"{len(received_cards)}/{len(CONFIG['all_cards'])}")
st.sidebar.progress(len(received_cards)/len(CONFIG['all_cards']))