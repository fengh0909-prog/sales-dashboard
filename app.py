import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. 页面配置 (Canvas 商务风格)
st.set_page_config(page_title="26H1 销售进度看板", layout="wide", initial_sidebar_state="expanded")

# 自定义 CSS 提升美观度
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_stdio=True)

st.title("📊 伊赫莱 & 大妥 销售进度 Canvas 看板")

# 2. 增强型数据加载逻辑 (解决 Unnamed 报错)
@st.cache_data
def load_data():
    file_name = "data.xlsx" if os.path.exists("data.xlsx") else "26H1数据.xlsx"
    if not os.path.exists(file_name):
        return None
    
    try:
        # 核心逻辑：自动定位表头行 (跳过垃圾信息)
        for i in range(5):
            df_temp = pd.read_excel(file_name, skiprows=i)
            # 识别包含核心字段的那一行
            cols = [str(c) for c in df_temp.columns]
            if any("行标签" in c or "LEL" in c for c in cols):
                df_temp.columns = df_temp.columns.astype(str).str.strip()
                # 过滤掉全为空的行和总计行
                df_temp = df_temp.dropna(subset=[df_temp.columns[0]])
                df_temp = df_temp[~df_temp.iloc[:, 0].astype(str).str.contains("总计|Total", na=False)]
                return df_temp
        return pd.read_excel(file_name)
    except Exception as e:
        st.error(f"加载失败: {e}")
        return None

df = load_data()

if df is not None:
    # 自动识别列名映射
    col_map = {
        'LEL': next((c for c in df.columns if "LEL" in c or "行标签" in c), None),
        'TAM': next((c for c in df.columns if "TAM" in c), None),
        'Target': next((c for c in df.columns if "TV" in c), None),
        'Sales': next((c for c in df.columns if "SV" in c), None),
        'Achievement': next((c for c in df.columns if "达成" in c), None),
        'TimeProgress': next((c for c in df.columns if "时间进度" in c), None)
    }

    # 3. 侧边栏交互
    st.sidebar.header("🔍 维度筛选")
    lel_list = ["全部"] + list(df[col_map['LEL']].unique())
    selected_lel = st.sidebar.selectbox("选择 LEL 区域", lel_list)

    # 数据联动过滤
    display_df = df.copy()
    if selected_lel != "全部":
        display_df = display_df[display_df[col_map['LEL']] == selected_lel]

    # 4. 指标卡片 (Top Metrics)
    total_tv = display_df[col_map['Target']].sum() if col_map['Target'] else 0
    total_sv = display_df[col_map['Sales']].sum() if col_map['Sales'] else 0
    avg_ach = (total_sv / total_tv * 100) if total_tv > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("总目标 (Target)", f"{total_tv/1000:,.1f}k")
    m2.metric("总实际 (Actual)", f"{total_sv/1000:,.1f}k")
    m3.metric("总达成率", f"{avg_ach:.1f}%", delta=f"{avg_ach - 75:.1f}% 对标进度")
    m4.metric("缺口 (Gap)", f"{(total_tv - total_sv)/1000:,.1f}k")

    # 5. 可视化图表 (Visual Analysis)
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("区域/代表 表现排行")
        # 绘制排行图
        fig_bar = px.bar(display_df.sort_values(by=col_map['Achievement'], ascending=True), 
                         y=col_map['LEL'], x=col_map['Achievement'],
                         orientation='h', title="达成率排名",
                         color=col_map['Achievement'], color_continuous_scale='Greens')
        fig_bar.add_vline(x=75, line_dash="dash", line_color="red", annotation_text="时间进度线")
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("达成区间分布")
        # 绩效分段
        bins = [0, 80, 100, 999]
        labels = ['待提升 (<80%)', '合格 (80-100%)', '优秀 (>100%)']
        display_df['Performance_Level'] = pd.cut(display_df[col_map['Achievement']], bins=bins, labels=labels)
        fig_pie = px.pie(display_df, names='Performance_Level', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    # 6. 数据明细清单
    st.subheader("📋 详细数据清单")
    st.dataframe(display_df.style.highlight_max(subset=[col_map['Achievement']], color='#deff9a'), use_container_width=True)

else:
    st.error("❌ 无法读取数据。请确保 GitHub 仓库中有 'data.xlsx' 或 '26H1数据.xlsx'")

您的 26H1 销售看板已经彻底进化！现在您可以享受到：
1.  **自动修复表头**：再也不怕 Excel 前几行有空行了。
2.  **手机适配**：顶部的 Metric 卡片在手机上会自动堆叠，非常精美。
3.  **Gap 预警**：红色的时间进度线能一眼看出谁在拖后腿。

快去 GitHub 更新代码并刷新您的网页吧！有问题随时跟我反馈。
