import pandas as pd  # 导入 pandas 处理 Excel

# 读取 Excel 文件
file_path = "职业生涯规划6个代码.xlsx"  # 确保文件名正确
xls = pd.ExcelFile(file_path)  # 加载 Excel 文件

# 显示所有工作表的名称，看看数据结构
print("Excel 工作表列表：", xls.sheet_names)

# 读取各个霍兰德代码的工作表
df_R = pd.read_excel(xls, sheet_name='R')
df_I = pd.read_excel(xls, sheet_name='I')
df_A = pd.read_excel(xls, sheet_name='A')
df_S = pd.read_excel(xls, sheet_name='S')
df_E = pd.read_excel(xls, sheet_name='E')
df_C = pd.read_excel(xls, sheet_name='C')

# 显示前几行数据，看看格式是否正确
print("R 代码数据预览：")
print(df_R.head())  # 只显示 R 代码的前几行数据

def clean_data(df):
    """
    解析霍兰德代码表格，提取低/中/高对应的解读文本
    """
    parsed_data = {}
    levels = ["低", "中", "高"]

    for i, row in df.iterrows():
        level = str(row.iloc[0]).strip()  # 获取第一列的"低/中/高"
        text = str(row.iloc[1]).strip()   # 获取第二列的解读文本
        
        if level in levels and pd.notna(text):  # 确保数据有效
            parsed_data[level] = text

    return parsed_data

# 处理所有代码
holland_data = {
    "R": clean_data(pd.read_excel(xls, sheet_name='R')),
    "I": clean_data(pd.read_excel(xls, sheet_name='I')),
    "A": clean_data(pd.read_excel(xls, sheet_name='A')),
    "S": clean_data(pd.read_excel(xls, sheet_name='S')),
    "E": clean_data(pd.read_excel(xls, sheet_name='E')),
    "C": clean_data(pd.read_excel(xls, sheet_name='C')),
}

# 测试输出
print("\n==== 解析后的霍兰德解读数据 ====")
print(holland_data)

def get_holland_report(scores):
    """
    根据用户输入的 6 个分值，自动生成解读报告
    """
    report = []
    for code, score in scores.items():
        # 计算低/中/高
        if score <= 10:
            level = "低"
        elif score <= 20:
            level = "中"
        else:
            level = "高"

        # 获取对应的解读文本
        description = holland_data[code].get(level, "暂无解读")
        report.append(f"{code}（{level}）: {description}")

    return "\n".join(report)

# 让用户输入 6 个代码的分值
user_scores = {}
codes = ["R", "I", "A", "S", "E", "C"]

print("请输入 6 个代码的分值（0-40）：")
for code in codes:
    while True:
        try:
            score = int(input(f"{code} 分值: "))
            if 0 <= score <= 40:
                user_scores[code] = score
                break
            else:
                print("请输入 0 到 40 之间的数值！")
        except ValueError:
            print("请输入有效的整数！")

# 生成解读报告
final_report = get_holland_report(user_scores)
print("\n===== 你的霍兰德解读报告 =====")
print(final_report)

