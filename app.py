import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 页面配置
st.set_page_config(page_title="26H1 销售进度看板", layout="wide")

# 2. 增强型数据加载逻辑
@st.cache_data
def load_data():
    # 尝试读取两个可能的文件名
    file_name = "data.xlsx" if os.path.exists("data.xlsx") else "26H1数据.xlsx"
    if not os.path.exists(file_name):
        return None
    
    try:
        # 自动定位表头行：尝试前10行，寻找包含关键列名的行
        for i in range(10):
            df_temp = pd.read_excel(file_name, skiprows=i)
            cols = [str(c) for c in df_temp.columns]
            # 只要列名里包含 LEL, 行标签, TAM, TV, SV 之一就认为是表头
            if any(k in "".join(cols) for k in ["LEL", "行标签", "TAM", "TV", "SV"]):
                df_temp.columns = df_temp.columns.astype(str).str.strip()
                # 过滤掉全空行和总计行
                df_temp = df_temp.dropna(how='all')
                df_temp = df_temp[~df_temp.iloc[:, 0].astype(str).str.contains("总计|Total", na=False)]
                return df_temp
        return pd.read_excel(file_name)
    except Exception as e:
        st.error(f"加载失败: {e}")
        return None

df = load_data()

if df is not None:
    # 3. 动态列名映射 (兼容你的 Excel 标题)
    col_map = {
        'LEL': next((c for c in df.columns if "LEL" in c or "行标签" in c), df.columns[0]),
        'TAM': next((c for c in df.columns if "TAM" in c or "代表" in c), None),
        'Target': next((c for c in df.columns if "TV" in c or "目标" in c), None),
        'Sales': next((c for c in df.columns if "SV" in c or "实际" in c), None),
        'Ach': next((c for c in df.columns if "达成" in c), None)
    }

    # 4. 侧边栏：区域筛选
    st.sidebar.header("🔍 筛选控制")
    lel_options = ["全部"] + list(df[col_map['LEL']].dropna().unique())
    selected_lel = st.sidebar.selectbox("选择 LEL 区域", options=lel_options)

    # 数据过滤
    display_df = df.copy()
    if selected_lel != "全部":
        display_df = display_df[display_df[col_map['LEL']] == selected_lel]

    # 5. 核心指标展示 (KPI Cards)
    if col_map['Target'] and col_map['Sales']:
        total_tv = pd.to_numeric(display_df[col_map['Target']], errors='coerce').sum()
        total_sv = pd.to_numeric(display_df[col_map['Sales']], errors='coerce').sum()
        avg_ach = (total_sv / total_tv) if total_tv > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("总目标 (Target)", f"{total_tv/1000:,.1f}k")
        m2.metric("总实际 (Actual)", f"{total_sv/1000:,.1f}k")
        m3.metric("总达成率", f"{avg_ach*100:.1f}%" if avg_ach < 10 else f"{avg_ach:.1f}%")

    # 6. 可视化图表
    st.subheader("📊 达成表现分析")
    if col_map['Ach']:
        # 转换达成率为数值
        display_df['ach_num'] = pd.to_numeric(display_df[col_map['Ach']], errors='coerce')
        if display_df['ach_num'].max() < 2: # 说明是 0.85 这种格式
            display_df['ach_num'] = display_df['ach_num'] * 100
            
        fig = px.bar(display_df.sort_values('ach_num'), 
                     x='ach_num', y=col_map['LEL'], 
                     orientation='h', title="各区域达成率 (%)",
                     color='ach_num', color_continuous_scale='Greens')
        # 添加 75% 时间进度参考线
        fig.add_vline(x=75, line_dash="dash", line_color="red", annotation_text="时间进度(75%)")
        st.plotly_chart(fig, use_container_width=True)

    # 7. 数据明细清单
    st.subheader("📋 详细数据清单")
    st.dataframe(display_df, use_container_width=True)

else:
    st.error("❌ 没找到数据文件。请确保 GitHub 仓库里有 '26H1数据.xlsx' 或 'data.xlsx'")
