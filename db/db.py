import datetime

# 管理数据库
'''
三个表格
1. 用户表
序号(从1自动增长) 用户名, 剩余次数,分数,正确回答问题的平均耗时
2. 单词表
序号(从1自动增长) 单词, 解释
3. 排行版
用户名, 分数
'''

# 建表
def create_table():
    import sqlite3
    conn = sqlite3.connect('db/typegame.db')
    c = conn.cursor()
    # 删除所有表格
    c.execute('DROP TABLE IF EXISTS user')
    c.execute('DROP TABLE IF EXISTS word')
    # 时间默认空
    c.execute('CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, stuId TEXT, times INTEGER, score INTEGER, consumption INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS word (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT, explanation TEXT)')
    conn.commit()
    conn.close()


#用户表格信息初始化

def init_user():
    import sqlite3
    conn = sqlite3.connect('db/typegame.db')
    c = conn.cursor()
    # 读取userinfo.txt
    with open('data/userinfo.txt', 'r') as f:
        lines = f.readlines()
    # 删除该表格信息
    c.execute('DELETE FROM user')
    # 插入数据库
    for line in lines:
        stuId = line.strip()
        if stuId != None:
            c.execute('INSERT INTO user (stuId, times, score) VALUES (?, ?, ?)', (stuId, 2, 0))
    conn.commit()
    conn.close()

# 单词表格初始化
def init_word():
    import sqlite3
    conn = sqlite3.connect('db/typegame.db')
    c = conn.cursor()
    # 读取word.txt
    with open('data/words.txt', 'r') as f:
        lines = f.readlines()
    # 删除该表格信息
    c.execute('DELETE FROM word')
    # 插入数据库
    for line in lines:
        word, explanation = line.strip().split('\t')
        c.execute('INSERT INTO word (word, explanation) VALUES (?, ?)', (word, explanation))
    conn.commit()
    conn.close()
# 查看各个表格
def select_all():
    import sqlite3
    conn = sqlite3.connect('db/typegame.db')
    c = conn.cursor()
    c.execute('SELECT * FROM user')
    print(c.fetchall())
    # c.execute('SELECT * FROM
    #  word')
    # print(c.fetchall())
    conn.close()

# 删除指定表格
def delete_table(table):
    import sqlite3
    conn = sqlite3.connect('db/typegame.db')
    c = conn.cursor()
    c.execute(f'DROP TABLE {table}')
    conn.commit()
    conn.close()
    
# 初始化全部
def init():
    create_table()
    init_user()
    init_word()
    print('数据库初始化完成')

# 业务功能

#查询获取对应id的信息，如果没获取到就返回null
def check_id(id):
    import sqlite3
    conn = sqlite3.connect('db/typegame.db')
    c = conn.cursor()
    c.execute('SELECT * FROM user where stuId = ?', (id,)) # (1, 'CST19011', 10, 0)
    result = c.fetchone()
    conn.close()
    return result

#修改剩余次数
def update_times(id, value):
    import sqlite3
    conn = sqlite3.connect('db/typegame.db')
    c = conn.cursor()
    c.execute('UPDATE user SET times = times + ? WHERE stuId = ?', (value, id))
    conn.commit()
    conn.close()

#随机10个单词
def get_word():
    import sqlite3
    conn = sqlite3.connect('db/typegame.db')
    c = conn.cursor()
    c.execute('SELECT * FROM word ORDER BY RANDOM() LIMIT 10')
    result = c.fetchall()
    result.sort(key=lambda x: len(x[1]))
    conn.close()
    return result

#修改分数
def update_score(id, score, consumption):
    import sqlite3
    conn = sqlite3.connect('db/typegame.db')
    c = conn.cursor()
    # 获取当前分数
    c.execute('SELECT score, consumption FROM user WHERE stuId = ?', (id,))
    result = c.fetchone()
    if result == None:
        print("can't find specified user")
        return
    # 如果当前分数小于新分数，更新分数
    print(consumption, result)
    # 新的成绩
    if result[0] < score or (result[0] == score and (result == None or result[1] > consumption)):
        c.execute('UPDATE user SET score = ?, consumption = ? WHERE stuId = ?', (score, consumption, id))
    conn.commit()
    conn.close()

#获取排行
def get_rank():
    import sqlite3
    conn = sqlite3.connect('db/typegame.db')
    c = conn.cursor()
    # 先按分数降序，再按时间升序 不要时间为空的
    c.execute('SELECT stuId, score FROM user WHERE consumption IS NOT NULL ORDER BY score DESC, consumption')
    result = c.fetchall()
    conn.close()
    return result

#获取用户信息
def get_all_user():
    import sqlite3
    conn = sqlite3.connect('db/typegame.db')
    c = conn.cursor()
    c.execute('SELECT * FROM user')
    result = c.fetchall()
    conn.close()
    return result

#每日数据存档
def renew_daily():
    file = open("db/rank.log", "a")
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    file.write(now + "\n")
    for i in get_rank():
        file.write(str(i) + "\n")
    file.close()
    init()
       
# if __name__ == '__main__': 
#     # init()
#     # select_all()
