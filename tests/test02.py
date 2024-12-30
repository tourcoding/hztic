import pandas as pd
from rapidfuzz import process, fuzz
import re

path = r"D:\Projects\hztic\hztic\config\download\branch_info.xlsx"

# 读取表格数据
df = pd.read_excel(path, '网点信息导出', engine="calamine")
choices = [name.replace("股份有限公司", "") for name in df['网点名称'].tolist()]

# 用户输入的支行名称
query = "招商银行北京分行营业部"

# 对用户输入进行预处理
query_parts = re.split(r'行', query)
first_word = query_parts[0]
remaining_parts = query_parts[1:]

# 使用 Rapidfuzz 进行模糊匹配
first_word_weight = 0.8
remaining_parts_weight = 0.2

first_word_results = process.extract(first_word, choices, scorer=fuzz.partial_token_sort_ratio, score_cutoff=80, limit=5)
remaining_parts_results = []
for part in remaining_parts:
    part_results = process.extract(part, choices, scorer=fuzz.partial_token_sort_ratio, score_cutoff=80, limit=5)
    remaining_parts_results.extend(part_results)

# 合并结果并按照得分排序
results = []
for match, score, extra in first_word_results:
    if match.startswith(first_word):
        results.append((match, score * first_word_weight, extra))
for match, score, extra in remaining_parts_results:
    if any(part in match for part in remaining_parts):
        results.append((match, score * remaining_parts_weight, extra))

results.sort(key=lambda x: x[1], reverse=True)

# 输出结果
print(f"用户输入支行: {query}")
for match, score, extra in results[:5]:
    print(f"Match: {match}, Score: {score:.2f}, Extra: {extra}")
