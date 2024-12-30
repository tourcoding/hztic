import json

# 打开文件
with open(r"D:\Projects\hztic\tests\data.json", "r",encoding='utf-8') as file:
  # 读取文件内容
  json_data = json.load(file)

# 打印文件内容
jobNumber = []
for i in range(0, len(json_data['data'])):
    jobNumber.append(json_data['data'][i]['recordInfo']['jobNumber'])

print(jobNumber)
print(len(jobNumber))