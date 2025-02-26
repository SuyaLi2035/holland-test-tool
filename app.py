import streamlit as st
import pandas as pd
import random
import openai
import time

# 📌 **DeepSeek API Key**
DEEPSEEK_API_KEY = "sk-b2QUOEmlAArQ528ekQr3FzyEiI9shAJSyJW5jI4Dav8HAVzp"

# ✅ **配置 OpenAI 访问 DeepSeek**
openai.api_base = "https://tbnx.plus7.plus/v1"

# ================================ #
# 📌 **读取 Excel 数据**
# ================================ #
file_path = "职业生涯规划6个代码.xlsx"
xls = pd.ExcelFile(file_path)

def clean_data(df):
    """ 解析霍兰德代码表格，提取低/中/高的解读文本 + 总结 """
    parsed_data = {}
    levels = ["低", "中", "高"]
    
    for _, row in df.iterrows():
        level = str(row.iloc[0]).strip()
        text = str(row.iloc[1]).strip()
        summary = str(row.iloc[2]).strip() if len(row) > 2 else "暂无总结"
        
        if level in levels and pd.notna(text):
            parsed_data[level] = {"text": text, "summary": summary}
    
    return parsed_data

holland_data = {
    "R": clean_data(pd.read_excel(xls, sheet_name='R')),
    "I": clean_data(pd.read_excel(xls, sheet_name='I')),
    "A": clean_data(pd.read_excel(xls, sheet_name='A')),
    "S": clean_data(pd.read_excel(xls, sheet_name='S')),
    "E": clean_data(pd.read_excel(xls, sheet_name='E')),
    "C": clean_data(pd.read_excel(xls, sheet_name='C')),
}

def get_holland_report(scores):
    """ 生成解读报告（包含解读文本 + 总结），并按照分值从高到低排序 """
    report = []
    summary_report = []
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    for code, score in sorted_scores:
        level = "低" if score < 15 else "中" if score <= 20 else "高"

        data = holland_data.get(code, {}).get(level, {"text": "暂无解读", "summary": "暂无总结"})
        text = data["text"]
        summary = data["summary"]
        
        report.append(f"**{code}（{level}）**: {text}")
        summary_report.append(f"**{code} 总结**: {summary}")

    return "\n\n".join(report), "\n\n".join(summary_report)

# ================================ #
# 📌 **函数：调用 DeepSeek API 进行 AI 总结（非流式）**
# ================================ #
def summarize_report(report):
    """ 使用 DeepSeek API 进行总结 """
    client = openai.OpenAI(
        base_url="https://tbnx.plus7.plus/v1",
        api_key=DEEPSEEK_API_KEY
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个国际职业生涯规划师，请生成一段清晰、精准的总结，总结控制在200-300字区间，用‘你’描述，不要使用该用户，结尾给出1-2句简短的建议，语言要温和，客户听了会很舒服，不需要强调职业方向，只需要描述客户是一个什么样的人。"},
                {"role": "user", "content": f"请总结以下霍兰德测试报告内容：\n\n{report}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 总结失败：{str(e)}"

# ================================ #
# 📌 **函数：调用 DeepSeek API 进行异议解答（流式输出）**
# ================================ #
def answer_objection(question):
    """ 使用 DeepSeek API 进行异议解答，并调用知识库 """
    client = openai.OpenAI(
        base_url="https://tbnx.plus7.plus/v1",
        api_key=DEEPSEEK_API_KEY
    )

    # **构造 AI 指令**
    system_prompt = (
        "请你作为一个沟通高手，懂人性、懂心理学，会讲人话，很会利用损失厌恶、沉没成本等法则。\n\n"
        "请使用以下框架回答问题：Praise-赞美】：接纳并理解你的情绪和感受，明确识别出你内心的需求，【Feature-产品特征】：明确定义问题、拆分分类（表面现象vs深层原因、行为表现vs内心需求、情绪感受vs事实真相），体现这种沟通方式的特征，【Advantage-产品优势】：说明精准定义和分类后，能带来的直接优势（比如摆脱情绪困扰、理清真正问题），【Benefit-好处】提供长期主义或教育减法的新视角，建立积极或客观的认知，提升沟通效率和效果，【Close-结尾关单】最后通过建议或发起行动，引导你去实际应用和实践。在使用以上框架回答问题的时候，确保产出的内容，说人话，框架于框架之间连贯，且沟通的视角是我向客户说的视角，建立1-2次互动，客户听感舒服。。\n"
        "同时，你可以参考以下知识库中的信息，结合信息库按照框架，以确保回答准确且有说服力。\n"
        "如果知识库中有相关内容，请优先使用；如果没有，则自由发挥，但一定是和教育、长期主义相关。\n\n"

    )

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"用户的问题：{question}"}
            ],
            stream=True  # ✅ 启用流式输出
        )

        response_text = ""
        response_container = st.empty()

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content.strip()
                if text:
                    response_text += text + "\n\n"  # **确保换行**
                    response_container.markdown(response_text)  # **实时更新 UI**
                    yield text  # ✅ 逐步返回内容

    except Exception as e:
        st.error(f"❌ 解答失败：{str(e)}")
        yield f"❌ 解答失败：{str(e)}"


# 📌 **函数：加载知识库**
import os
from PyPDF2 import PdfReader
import docx

def load_knowledge_base():
    """ 读取 knowledge_base 目录下的所有 Word 和 PDF 文件，并合并内容 """
    knowledge_base_text = ""

    if not os.path.exists("knowledge_base"):
        os.makedirs("knowledge_base")  # **如果目录不存在，创建它**

    for file in os.listdir("knowledge_base"):
        file_path = os.path.join("knowledge_base", file)

        if file.endswith(".pdf"):
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    knowledge_base_text += page.extract_text() + "\n"
            except Exception as e:
                print(f"❌ 读取 PDF 失败：{file_path}，错误：{str(e)}")

        elif file.endswith(".docx"):
            try:
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    knowledge_base_text += para.text + "\n"
            except Exception as e:
                print(f"❌ 读取 Word 失败：{file_path}，错误：{str(e)}")

    if not knowledge_base_text.strip():
        print("⚠️ 知识库为空，AI 将自行回答。")
    
    return knowledge_base_text

# ✅ **加载知识库**
knowledge_base_content = load_knowledge_base()



# ================================ #
# 📌 **函数：调用 AI 进行异议解答**
# ================================ #
def answer_objection(question):
    """ 使用 DeepSeek API 进行异议解答，并调用知识库 """
    client = openai.OpenAI(
        base_url="https://tbnx.plus7.plus/v1",
        api_key=DEEPSEEK_API_KEY
    )

    # **确保知识库内容被正确传递**
    if knowledge_base_content.strip():
        system_prompt = (
            "你是一个营销沟通高手，懂人性、懂心理学，很会利用损失厌恶、沉没成本等法则，促使客户成交。\n\n"
            "请使用‘Praise-赞美 / Feature-产品特征 / Advantage-产品优势 / Benefit-对你的收益 / Close-结尾关单’框架回答用户问题。\n"
            "请优先参考以下知识库内容，以确保回答准确且有说服力：\n\n"
            f"📚 知识库内容（部分）：\n{knowledge_base_content[:2000]}\n\n"  # **截取前 2000 字**
            "如果知识库中没有相关内容，可以自由发挥，但仍然遵循上述结构进行回答。\n"
        )
    else:
        system_prompt = (
            "你是一个营销沟通高手，懂人性、懂心理学，很会利用损失厌恶、沉没成本等法则，促使客户成交。\n\n"
            "请使用‘Praise-赞美 / Feature-产品特征 / Advantage-产品优势 / Benefit-对你的收益 / Close-结尾关单’框架回答用户问题。\n"
            "⚠️ 知识库为空，你需要自行推理并回答。\n"
        )

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"用户的问题：{question}"}
            ],
            stream=True  # ✅ 启用流式输出
        )

        response_text = ""  # 用于存储完整回答
        buffer = ""  # 临时存储单句
        response_container = st.empty()

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content.strip()

                if text:
                    buffer += text

                    # **检测句号、问号、感叹号，判断是否完整句子**
                    if any(end in buffer for end in ["。", "！", "？"]):
                        response_text += buffer + "\n\n"  # **添加换行，确保分行显示**
                        buffer = ""  # **清空临时存储，准备存下一句**
                        response_container.markdown(response_text)  # **更新 UI**

        # **确保最后的内容也被渲染**
        if buffer:
            response_text += buffer + "\n\n"
            response_container.markdown(response_text)

    except Exception as e:
        st.error(f"❌ 解答失败：{str(e)}")
        yield f"❌ 解答失败：{str(e)}"




st.markdown("<h1 style='text-align: center; color: #FF4B4B; font-weight: bold;'>霍兰德职业兴趣测试</h1>", unsafe_allow_html=True)


# ================================ #
# 📌 **异议解答模块（流式输出 + 知识库支持）**
# ================================ #
with st.sidebar:
    st.markdown("## 🤖 **异议解答**")
    user_question = st.text_input("🔍 请输入你的问题：", key="objection_input_1")
    
    if st.button("🚀 提交并解答", key="objection_submit_1"):
        if user_question.strip():
            with st.spinner("🤖 AI 正在查询，请稍候..."):
                response_text = ""
                response_container = st.empty()

                for partial_response in answer_objection(user_question):
                    response_text += partial_response + "\n\n"  # ✅ 逐步拼接，强制换行
                    response_container.markdown(response_text)




# ================================ #
# 📌 **代码解读输入框**
# ================================ #
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

st.markdown("---")

# ================================ #
# 📌 **提交按钮**
# ================================ #
if st.button("📌 **提交并查看解读**", key="report_submit"):
    scores = {"R": r, "I": i, "A": a, "S": s, "E": e, "C": c}
    report, summary = get_holland_report(scores)

    st.markdown("## 📌 **你的解读报告**")
    st.markdown(report)

    with st.spinner("🤖 AI 正在总结你的报告，请稍候..."):
        ai_summary = summarize_report(report)

    st.markdown("## 🤖 **AI 生成总结**")
    st.markdown(ai_summary)
