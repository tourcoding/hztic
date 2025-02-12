# http://prod.hanzibeacon.com:8003/api/hr/emp/notify

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/hr/emp/notify', methods=['POST'])
def process_variable():
    # 1. 接收 JSON 数据
    data = request.get_json()  # 获取请求体中的 JSON 数据
    if not data:  # 如果 data 为空
        return jsonify({"error": "Invalid input. JSON data required."}), 400

    # 2. 获取 `processVariableDic`
    process_variable_dic = data.get("processVariableDic", {})  # 提取 `processVariableDic` 字段
    if not isinstance(process_variable_dic, dict):  # 验证字段是否为字典
        return jsonify({"error": "processVariableDic must be a dictionary."}), 400

    # 3. 解析具体字段
    employee_name = process_variable_dic.get("employeeName", "Unknown")
    entry_date = process_variable_dic.get("entryDate", "Unknown")
    
    # 4. 返回处理结果
    return jsonify({
        "status": "success",
        "parsedData": {
            "employeeName": employee_name,
            "entryDate": entry_date
        }
    }), 200