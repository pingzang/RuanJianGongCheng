import streamlit as st
import os
from collection_utils import get_user_collection, get_card_image_path, load_card_image

CONFIG = {
    "all_cards": ["card_01", "card_02", "card_03", "card_04", "card_05"],
    "card_img_dir": "card_images/",
    "placeholder_img": "unlocked_placeholder.png",
    "error_img": "default_error.png",
    "columns_num": 5,
    "page_title": "卡牌图鉴"
}

def show_collection(username):
    st.set_page_config(page_title=CONFIG["page_title"], page_icon="🎴", layout="wide")
    st.title(CONFIG["page_title"])
    owned = get_user_collection(username)

    cols = st.columns(CONFIG["columns_num"])
    for idx, card_id in enumerate(CONFIG["all_cards"]):
        col = cols[idx % CONFIG["columns_num"]]
        with col:
            st.subheader(f"卡牌{idx+1}")
            img_path = get_card_image_path(card_id, owned, CONFIG["card_img_dir"])
            img = load_card_image(img_path)
            if img:
                st.image(img, use_column_width=True)
            status = "已获得" if card_id in owned else "未获得"
            st.caption(f"状态：{status}")

    total = len(CONFIG["all_cards"])
    collected = len([c for c in owned if c in CONFIG["all_cards"]])
    st.sidebar.metric("已收集", f"{collected}/{total}")
    if total > 0:
        st.sidebar.progress(collected / total)