import streamlit as st
import pandas as pd
import random  # 🚀 导入随机模块

# ✨ 40 句精句库
quotes = [
    "别人的孩子，成绩好、会规划、懂目标，而你家孩子，只会等着你安排。",
    "你在焦虑补课，他在焦虑作业，最后补了个寂寞，考了个遗憾。",
    "孩子不是被逼出来的，是被看见、被引导出来的。",
    "你想让孩子考好大学，他却连自己想干嘛都不知道，大学四年白读了。",
    "很多家长忙着给孩子规划‘好学校’，却忘了孩子未来最重要的是‘好方向’。",
    "家长焦虑的不是分数，而是孩子没有清晰的未来。",
    "成绩好≠人生好，能找到方向，才是真正的赢。",
    "你家孩子不是‘不努力’，而是根本不知道‘努力往哪用’。",
    "补课能补知识，补不了认知；鸡娃能催成绩，催不出方向。",
    "培养孩子的核心竞争力，不是多学多少知识，而是找到适合他生存的赛道。",
    "有目标的孩子，早在做准备；没目标的孩子，还在等家长安排。",
    "如果你不帮孩子提前找到方向，他就只能在社会里被反复试错。",
    "到大学才迷茫的孩子，比没考上大学的更可怕。",
    "选错方向比选错学校更致命！四年换不回一次错误的选择。",
    "你不带孩子提前看见未来，未来就会带孩子狠狠教训你。",
    "规划得越早，试错成本越低，孩子未来走得越顺。",
    "与其焦虑孩子不努力，不如帮他找到值得努力的方向。",
    "职业规划不是等高考完再想，而是现在就该提前布局。",
    "职业生涯规划，帮你让孩子的努力不白费，让成长有方向。",
    "来做规划，不是给孩子增加负担，而是让他少走弯路，赢在起点。",
]

# ✅ **使用 session_state 让精句只在网页刷新时变化**
if "random_quote" not in st.session_state:
    st.session_state.random_quote = random.choice(quotes)

# 📌 **UI：标题**
st.markdown("<h1 style='text-align: center; color: #FF4B4B; font-weight: bold;'>霍兰德职业兴趣测试</h1>", unsafe_allow_html=True)

# ✅ **副标题：今日提示**
st.markdown(f"""
</h2>
<p style='text-align: center; font-size:20px; color: black; font-weight: bold;'>
👉 {st.session_state.random_quote}
</p>
""", unsafe_allow_html=True)



# 📌 **读取 Excel 数据**
file_path = "职业生涯规划6个代码.xlsx"
xls = pd.ExcelFile(file_path)

# ✅ **确保 `clean_data()` 在 `holland_data` 之前定义**
def clean_data(df):
    """
    解析霍兰德代码表格，提取低/中/高的解读文本 + 总结
    """
    parsed_data = {}
    levels = ["低", "中", "高"]
    
    for _, row in df.iterrows():
        level = str(row.iloc[0]).strip()
        text = str(row.iloc[1]).strip()
        summary = str(row.iloc[2]).strip() if len(row) > 2 else "暂无总结"  # 处理总结字段
        
        if level in levels and pd.notna(text):
            parsed_data[level] = {"text": text, "summary": summary}  # ✅ 返回文本和总结
    
    return parsed_data

# ✅ **调用 clean_data()**
holland_data = {
    "R": clean_data(pd.read_excel(xls, sheet_name='R')),
    "I": clean_data(pd.read_excel(xls, sheet_name='I')),
    "A": clean_data(pd.read_excel(xls, sheet_name='A')),
    "S": clean_data(pd.read_excel(xls, sheet_name='S')),
    "E": clean_data(pd.read_excel(xls, sheet_name='E')),
    "C": clean_data(pd.read_excel(xls, sheet_name='C')),
}

# ✅ **优化 `get_holland_report()`，确保结果按照分值从高到低排序**
def get_holland_report(scores):
    """
    根据用户输入的 6 个分值，自动生成解读报告（包含解读文本 + 总结），并按照分值从高到低排序
    """
    report = []
    summary_report = []
    
    # 1️⃣ **按照分值从高到低排序**
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    for code, score in sorted_scores:  # 🔥 这里用排序后的顺序
        if score < 15:
            level = "低"
        elif 15 <= score <= 20:
            level = "中"
        else:
            level = "高"

        # 2️⃣ **获取解读文本和总结**
        data = holland_data.get(code, {}).get(level, {"text": "暂无解读", "summary": "暂无总结"})
        text = data["text"]
        summary = data["summary"]
        
        report.append(f"**{code}（{level}）**: {text}")
        summary_report.append(f"**{code} 总结**: {summary}")

    return "\n\n".join(report), "\n\n".join(summary_report)

# ✅ **输入框（移除滑块）**
col1, col2, col3 = st.columns(3)

with col1:
    r = st.number_input("🔧 R（实际型）", min_value=0, max_value=40, value=20, step=1)
    i = st.number_input("🔬 I（研究型）", min_value=0, max_value=40, value=20, step=1)

with col2:
    a = st.number_input("🎨 A（艺术型）", min_value=0, max_value=40, value=20, step=1)
    s = st.number_input("🤝 S（社会型）", min_value=0, max_value=40, value=20, step=1)

with col3:
    e = st.number_input("💼 E（企业型）", min_value=0, max_value=40, value=20, step=1)
    c = st.number_input("📊 C（常规型）", min_value=0, max_value=40, value=20, step=1)

st.markdown("---")  # 添加分割线

# ✅ **提交按钮**
if st.button("📌 **提交并查看解读**", key="submit_button"):
    scores = {"R": r, "I": i, "A": a, "S": s, "E": e, "C": c}
    report, summary = get_holland_report(scores)
    
    st.markdown("## 🎯 **你的霍兰德解读报告**")
    st.markdown(report)

    st.markdown("## 📌 **你的总结**")
    st.markdown(summary)
