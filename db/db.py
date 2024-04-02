import datetime
import json
import sqlite3

# 管理数据库
"""
三个表格
1. 用户表
序号(从1自动增长) 用户名, 剩余次数,分数,正确回答问题的平均耗时
2. 单词表
序号(从1自动增长) 单词, 解释
3. 排行版
用户名, 分数
"""


# 获取数据库地址
def get_addr():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config


# 建表
def create_table():
    conn = sqlite3.connect(get_addr()["database"])
    c = conn.cursor()
    # 删除所有表格
    c.execute("DROP TABLE IF EXISTS user")
    c.execute("DROP TABLE IF EXISTS word")
    # 时间默认空
    c.execute(
        "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, stuId TEXT, times INTEGER, score INTEGER, consumption NUMERIC(5,1))"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS word (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT, explanation TEXT)"
    )
    conn.commit()
    conn.close()


# 用户表格信息初始化


def init_user():
    conn = sqlite3.connect(get_addr()["database"])
    c = conn.cursor()
    # 读取userinfo.txt
    with open(get_addr()["userinfo"], "r") as f:
        lines = f.readlines()
    # 删除该表格信息
    c.execute("DELETE FROM user")
    # 插入数据库
    for line in lines:
        stuId = line.strip()
        if stuId != None:
            c.execute(
                "INSERT INTO user (stuId, times, score) VALUES (?, ?, ?)", (stuId, 1, 0)
            )
    conn.commit()
    conn.close()


# 单词表格初始化
def init_word():
    conn = sqlite3.connect(get_addr()["database"])
    c = conn.cursor()
    # 读取word.txt
    with open(get_addr()["words"], "r", encoding="utf-8") as f:
        lines = f.readlines()
    # 删除该表格信息
    c.execute("DELETE FROM word")
    # 插入数据库
    for line in lines:
        word, explanation = line.strip().split("\t")
        c.execute(
            "INSERT INTO word (word, explanation) VALUES (?, ?)", (word, explanation)
        )
    conn.commit()
    conn.close()


# 查看各个表格
def select_all():
    conn = sqlite3.connect(get_addr()["database"])
    c = conn.cursor()
    c.execute("SELECT * FROM user")
    print(c.fetchall())
    # c.execute('SELECT * FROM
    #  word')
    # print(c.fetchall())
    conn.close()


# 删除指定表格
def delete_table(table):
    conn = sqlite3.connect(get_addr()["database"])
    c = conn.cursor()
    c.execute(f"DROP TABLE {table}")
    conn.commit()
    conn.close()


# 初始化全部
def init():
    create_table()
    init_user()
    init_word()
    print("数据库初始化完成")


# 业务功能


# 查询获取对应id的信息，如果没获取到就返回null
def check_id(id):
    conn = sqlite3.connect(get_addr()["database"])
    c = conn.cursor()
    c.execute("SELECT * FROM user where stuId = ?", (id,))  # (1, 'CST19011', 10, 0)
    result = c.fetchone()
    conn.close()
    return result


# 修改剩余次数
def update_times(id, value):
    conn = sqlite3.connect(get_addr()["database"])
    c = conn.cursor()
    c.execute("UPDATE user SET times = ? WHERE stuId = ?", (value, id))
    conn.commit()
    conn.close()


# 随机10个单词
def get_word():
    conn = sqlite3.connect(get_addr()["database"])
    c = conn.cursor()
    c.execute("SELECT * FROM word ORDER BY RANDOM() LIMIT 10")
    result = c.fetchall()
    result.sort(key=lambda x: len(x[1]))
    conn.close()
    return result


# 修改分数
def update_score(id, score, consumption):
    conn = sqlite3.connect(get_addr()["database"])
    c = conn.cursor()
    
    # 获取当前分数
    c.execute("SELECT score, consumption FROM user WHERE stuId = ?", (id,))
    result = c.fetchone()

    # 如果当前分数小于新分数，更新分数
    consumption = round(consumption, 1)

    # 修改的逻辑 1. 分数超越  2. 分数相同，耗时更短
    isFaster = result[0] == score and (result[1] == None or result[1] > consumption)
    if result[0] < score or isFaster:
        c.execute(
            "UPDATE user SET score = ?, consumption = ? WHERE stuId = ?",
            (score, consumption, id),
        )
    conn.commit()
    conn.close()
    #每日默认只能玩一次 当前分数>=今日的最大分数，就能再玩一次
    if result[0] <= score:
        update_times(id, 1)

# 获取排行
def get_rank():
    conn = sqlite3.connect(get_addr()["database"])
    c = conn.cursor()
    # 先按分数降序，再按时间升序 不要时间为空的
    c.execute(
        "SELECT stuId, score, consumption FROM user WHERE consumption IS NOT NULL ORDER BY score DESC, consumption"
    )
    result = c.fetchall()
    conn.close()
    return result


# 获取用户信息
def get_all_user():
    conn = sqlite3.connect(get_addr()["database"])
    c = conn.cursor()
    c.execute("SELECT * FROM user")
    result = c.fetchall()
    conn.close()
    return result


# 每日数据存档
def renew_daily():
    file = open(get_addr()["rank"], "a")
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    file.write(now + "\n")
    for i in get_rank():
        file.write(str(i) + "\n")
    file.close()
    init()


if __name__ == "__main__":
    init()
