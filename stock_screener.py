import streamlit as st
import akshare as ak
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="金龙A股选股器", page_icon="📈", layout="wide")
st.title("🚀 金龙AIA股实时选股器（手机版友好）")
st.markdown("**数据来源：东方财富** | 每分钟更新 | 仅供学习，非投资建议")

st.sidebar.header("🔍 自定义筛选条件")
pe_max = st.sidebar.slider("动态市盈率 (PE) < ", 0, 200, 25)
pb_max = st.sidebar.slider("市净率 (PB) < ", 0.0, 15.0, 3.0)
turnover_min = st.sidebar.slider("换手率 (%) > ", 0.0, 30.0, 1.5)
amount_min = st.sidebar.slider("成交额 (亿) > ", 0.5, 200.0, 8.0)
change_min = st.sidebar.slider("今日涨跌幅 (%) > ", -15.0, 30.0, 2.0)

if st.sidebar.button("🚀 开始筛选全市场", type="primary", use_container_width=True):
    with st.spinner("正在拉取最新5000+只A股实时数据..."):
        try:
            df = ak.stock_zh_a_spot_em()
            
            # 关键列处理
            df = df.rename(columns={
                "代码": "代码", "名称": "名称", "最新价": "最新价",
                "涨跌幅": "涨跌幅", "成交额": "成交额", "换手率": "换手率",
                "市盈率-动态": "动态PE", "市净率": "市净率"
            })
            
            df_filtered = df[
                (df["动态PE"] > 0) & (df["动态PE"] < pe_max) &
                (df["市净率"] < pb_max) &
                (df["换手率"] > turnover_min) &
                (df["成交额"] / 100_000_000 > amount_min) &
                (df["涨跌幅"] > change_min)
            ].copy()
            
            df_filtered["成交额(亿)"] = (df_filtered["成交额"] / 100_000_000).round(2)
            df_filtered = df_filtered[["代码", "名称", "最新价", "涨跌幅", "动态PE", "市净率", "换手率", "成交额(亿)"]]
            
            st.success(f"✅ 找到 **{len(df_filtered)} 只** 符合条件的股票！")
            
            st.dataframe(
                df_filtered.sort_values("涨跌幅", ascending=False),
                use_container_width=True,
                height=600
            )
            
            fig = px.scatter(
                df_filtered.head(80), x="动态PE", y="涨跌幅",
                size="成交额(亿)", color="换手率",
                hover_name="名称", title="📊 PE vs 涨跌幅气泡图",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 下载筛选结果CSV",
                data=csv,
                file_name=f"金龙选股_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"⚠️ 拉取失败：{str(e)}。请稍等10秒再点一次按钮（网络波动正常）")

st.caption("💡 小技巧：先把条件放宽看结果，再慢慢收紧滑块。想加ROE、K线、AI点评，随时告诉我！")
