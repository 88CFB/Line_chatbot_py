from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)

# 設置MongoDB連接
app.config["MONGO_URI"] = "mongodb://localhost:27017/lineBot"  # 替換為您的MongoDB連接字符串
mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/addUser')
def add_user_page():
    return render_template('addUser.html')


@app.route('/deleteUser')
def delete_user_page():
    return render_template('deleteUser.html')


@app.route('/updateUser')
def update_user_page():
    return render_template('updateUser.html')


@app.route('/addUser/<collection_name>', methods=['POST'])
def add_user(collection_name):
    data = request.json  # 從 POST 請求中獲取 JSON 數據
    user_id = data.get('user_id', '')

    # 檢查資料集中是否已經存在相同的 user_id
    existing_user = mongo.db[collection_name].find_one({'user_id': user_id})
    if existing_user:
        return jsonify(message="User already exists"), 400  # 返回錯誤碼 400，表示用戶已存在

    # 根據 collection_name 的不同來執行相應的插入操作
    if collection_name == 'sport':
        time = data.get('time', '')
        distance = data.get('distance', '')
        times = data.get('times', '')
        mongo.db[collection_name].insert_one({'user_id': user_id, 'time': time, 'distance': distance, 'times': times})
    elif collection_name == 'health':
        MHR = data.get('MHR', '')
        sbp = data.get('sbp', '')
        dbp = data.get('dbp', '')
        height = data.get('height', '')
        weight = data.get('weight', '')
        mongo.db[collection_name].insert_one(
            {'user_id': user_id, 'MHR': MHR, 'sbp': sbp, 'dbp': dbp, 'height': height, 'weight': weight})

    return jsonify(message="User added successfully"), 201


@app.route('/deleteUser/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    result_sport = mongo.db['sport'].delete_one({'user_id': user_id})
    result_health = mongo.db['health'].delete_one({'user_id': user_id})

    if result_sport.deleted_count or result_health.deleted_count:
        return jsonify(message="User deleted successfully"), 200
    else:
        return jsonify(message="User not found"), 404


@app.route('/updateUser/<collection_name>/<user_id>', methods=['PUT'])
def update_user(collection_name, user_id):
    data = request.json
    if collection_name == 'sport':
        time = data.get('time', '')
        distance = data.get('distance', '')
        times = data.get('times', '')
        existing_user = mongo.db[collection_name].find_one({'user_id': user_id})
        if existing_user:
            mongo.db[collection_name].update_one({'user_id': user_id}, {'$set': {'time': time, 'distance': distance, 'times': times}})
            return jsonify(message="User updated successfully"), 200
        else:
            mongo.db[collection_name].insert_one({'user_id': user_id, 'time': time, 'distance': distance, 'times': times})
            return jsonify(message="New user added successfully"), 201
    elif collection_name == 'health':
        MHR = data.get('MHR', '')
        sbp = data.get('sbp', '')
        dbp = data.get('dbp', '')
        height = data.get('height', '')
        weight = data.get('weight', '')
        existing_user = mongo.db[collection_name].find_one({'user_id': user_id})
        if existing_user:
            mongo.db[collection_name].update_one({'user_id': user_id}, {'$set': {'MHR': MHR, 'sbp': sbp, 'dbp': dbp, 'height': height, 'weight': weight}})
            return jsonify(message="User updated successfully"), 200
        else:
            mongo.db[collection_name].insert_one({'user_id': user_id, 'MHR': MHR, 'sbp': sbp, 'dbp': dbp, 'height': height, 'weight': weight})
            return jsonify(message="New user added successfully"), 201


# 其他路由保持不變
if __name__ == '__main__':
    app.run(debug=True, port=8080)
