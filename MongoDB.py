import pymongo

# 连接到MongoDB数据库
myClient = pymongo.MongoClient("mongodb://localhost:27017/")
dblist = myClient['lineBot']
kindOfNews = dblist.list_collection_names()


# 新增
def add_site(user_id, query):
    mycol = dblist[query]
    mydict = {"user_id": user_id}
    mycol.insert_one(mydict)


# 删除
def delete_site(name):
    mycol = dblist["sites"]
    query = {"name": name}
    result = mycol.delete_one(query)
    if result.deleted_count > 0:
        print(f"Deleted site with name: {name}")
    else:
        print(f"No site found with name: {name}")


# 查询
def find_site(collection_name, user_id):
    mycol = dblist[collection_name]
    results = mycol.find({"user_id": user_id}, {"_id": 0})  # 排除 "_id" 字段
    return results



# 示例调用
# add_site("RUNOOB", "10000", "https://www.runoob.com")
# update_site("RUNOOB", new_alexa="5000", new_url="https://runoob.com")
# delete_site("RUNOOB")
# find_site("RUNOOB")
