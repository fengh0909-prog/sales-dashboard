import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 设置页面配置
st.set_page_config(page_title="伊赫莱 & 大妥 销售进度仪表盘", layout="wide")
st.title("📊 伊赫莱 (Itovebi) & 大妥 (Phesgo) 销售进度看板")

# 2. 智能寻找并加载数据
@st.cache_data
def load_data():
    # 自动尝试可能的文件名（无论是原来的长名字还是改过的短名字）
    possible_names = ["26H1数据.xlsx", "data.xlsx"]
    for name in possible_names:
        if os.path.exists(name):
            df = pd.read_excel(name)
            df.columns = df.columns.astype(str).str.strip()
            return df
    return None

df = load_data()

if df is None:
    st.error("⚠️ 找不到数据文件！请确保您的 Excel 文件已经上传，并且名字是 '26H1沪闽赣-0427.xlsx' 或 'data.xlsx'。")
    st.stop()

# 确定代表的列名（如果数据里有TAM列则用TAM，否则用LEL）
rep_col_name = "TAM" if "TAM" in df.columns else "LEL"

# 3. 侧边栏：交互式筛选器
st.sidebar.header("🔍 数据筛选")

if 'LEL' in df.columns:
    lel_options = df['LEL'].dropna().unique().tolist()
    selected_lels = st.sidebar.multiselect("1. 选择 LEL", options=lel_options, default=lel_options)

    filtered_by_lel = df[df['LEL'].isin(selected_lels)]
    rep_options = filtered_by_lel[rep_col_name].dropna().unique().tolist() if rep_col_name in filtered_by_lel.columns else []
    selected_reps = st.sidebar.multiselect(f"2. 选择代表 ({rep_col_name})", options=rep_options, default=rep_options)
else:
    st.error("表格中未检测到 'LEL' 列，无法生成筛选器。将展示全量数据。")
    selected_lels = []
    selected_reps = []

# 过滤数据
mask = pd.Series(True, index=df.index)
if selected_lels:
    mask = mask & df['LEL'].isin(selected_lels)
if selected_reps:
    mask = mask & df[rep_col_name].isin(selected_reps)
filtered_df = df[mask]

# 4. 图表与明细展示
st.subheader("📋 数据明细")
st.dataframe(filtered_df, use_container_width=True)
