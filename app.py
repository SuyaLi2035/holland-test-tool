import streamlit as st
import pandas as pd

# 读取 Excel 数据
file_path = "职业生涯规划6个代码.xlsx"
xls = pd.ExcelFile(file_path)

def clean_data(df):
    parsed_data = {}
    levels = ["低", "中", "高"]
    for _, row in df.iterrows():
        level = str(row.iloc[0]).strip()
        text = str(row.iloc[1]).strip()
        if level in levels and pd.notna(text):
            parsed_data[level] = text
    return parsed_data

holland_data = {
    "R": clean_data(pd.read_excel(xls, sheet_name='R')),
    "I": clean_data(pd.read_excel(xls, sheet_name='I')),
    "A": clean_data(pd.read_excel(xls, sheet_name='A')),
    "S": clean_data(pd.read_excel(xls, sheet_name='S')),
    "E": clean_data(pd.read_excel(xls, sheet_name='E')),
    "C": clean_data(pd.read_excel(xls, sheet_name='C')),
}

def clean_data(df):
    """
    解析霍兰德代码表格，提取低/中/高对应的解读文本和总结
    """
    df.columns = df.columns.str.strip()  # 去除列名空格，防止 "总结 " 解析失败
    parsed_data = {}
    levels = ["低", "中", "高"]

    summary_index = df.columns.get_loc("总结") if "总结" in df.columns else None

    for _, row in df.iterrows():
        level = str(row.iloc[0]).strip()  # 低 / 中 / 高
        text = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else "暂无解读"
        summary = str(row.iloc[summary_index]).strip() if summary_index is not None and pd.notna(row.iloc[summary_index]) else "暂无总结"

        if level in levels:
            parsed_data[level] = {"text": text, "summary": summary}  # 存储解读和总结

    return parsed_data

# ========== Streamlit UI ==========
st.title("霍兰德职业兴趣测试 🔍")
st.write("📌 请输入你的 6 个代码分值（0-40），可以滑动选择或手动输入，然后点击 **提交** 按钮查看解读结果。")

# 用 Streamlit 的 columns 布局
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

# 显示滑块（与输入框同步）
with col1:
    r = st.slider("🔧 R（实际型）", 0, 40, r)
    i = st.slider("🔬 I（研究型）", 0, 40, i)

with col2:
    a = st.slider("🎨 A（艺术型）", 0, 40, a)
    s = st.slider("🤝 S（社会型）", 0, 40, s)

with col3:
    e = st.slider("💼 E（企业型）", 0, 40, e)
    c = st.slider("📊 C（常规型）", 0, 40, c)

# 实时显示当前分值
st.markdown(f"""
**当前分值：**
- 🔧 R: {r} 
- 🔬 I: {i}
- 🎨 A: {a}
- 🤝 S: {s}
- 💼 E: {e}
- 📊 C: {c}
""")

# 提交按钮
if st.button("📌 **提交并查看解读**"):
    scores = {"R": r, "I": i, "A": a, "S": s, "E": e, "C": c}
    
    # 🚀 确保 get_holland_report() 被正确调用
    report, summary = get_holland_report(scores)
    
    st.markdown("## 🎯 **你的霍兰德解读报告**")
    st.markdown(report)
    
    st.markdown("## 📌 **你的总结**")
    st.markdown(summary)

