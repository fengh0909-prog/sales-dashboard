import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="销售进度看板", layout="wide")
st.title("📊 伊赫莱 & 大妥 销售进度看板")

@st.cache_data
def load_data():
    # 自动尝试文件名
    file_name = "data.xlsx" if os.path.exists("data.xlsx") else "26H1数据.xlsx"
    if not os.path.exists(file_name):
        return None
    
    # 关键修改：自动寻找含有“行标签”或“LEL”的那一行作为表头
    for i in range(10): # 尝试前10行
        df_temp = pd.read_excel(file_name, skiprows=i)
        if '行标签' in df_temp.columns or 'LEL' in df_temp.columns:
            # 清理列名空格
            df_temp.columns = df_temp.columns.astype(str).str.strip()
            return df_temp
    return pd.read_excel(file_name) # 如果找不到，就按默认读

df = load_data()

if df is not None:
    # 动态确定列名
    # 如果你的表里叫“行标签”，我们就用“行标签”来做筛选
    target_col = None
    for col in ['LEL', '行标签', 'TAM']:
        if col in df.columns:
            target_col = col
            break

    if target_col:
        st.sidebar.header("🔍 筛选控制")
        options = df[target_col].dropna().unique().tolist()
        selected = st.sidebar.multiselect(f"选择 {target_col}", options=options, default=options)
        
        filtered_df = df[df[target_col].isin(selected)]
        st.subheader(f"📅 数据明细 (筛选: {target_col})")
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("⚠️ 未能自动识别到 'LEL' 或 '行标签' 列，请检查 Excel 表头。")
        st.dataframe(df)
else:
    st.error("❌ 未找到数据文件，请确保 Excel 已上传。")
