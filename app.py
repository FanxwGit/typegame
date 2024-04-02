from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, disconnect, emit
import random
import json
import db.db as db
from datetime import datetime
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 存储客户端信息
client = {}

# game time
GAMETIME = 10

# max round
MAXROUND = 10


# route
@app.route("/")
def index():
    return render_template("index.html")


# 查询用户信息
# return {status:1或0, msg:' ', stuId: 'xxx', times: 1或0}
@app.route("/api/getuser", methods=["GET"])  # calhost:5000/api/getuser?stuId=xxx
def get_connection_status():
    res = db.check_id(request.args.get("stuId"))
    if res != None:
        return jsonify(
            {
                "status": 1,
                "msg": "Success",
                "stuId": res[1],
                "times": res[2],
                "score": res[3],
            }
        )
    else:
        return jsonify({"status": 0, "msg": "Invalid", "stuId": "", "times": 0})


# get_rank api
@app.route("/api/getrank", methods=["GET"])
def get_rank():
    result = db.get_rank()
    return jsonify(result)


@socketio.on("query")
def query_word():

    # print("client query the word")
    id = request.sid
    # 判断是否在client中
    if id in client:
        print(f"Client {client[id]['stuId']} reconnected")
    else:
        socketio.emit("reject", room=id)
        return

    client[id]["time"] = time.time()
    round = client[id]["round"]
    if round == 10:
        handle_disconnect(id)
        socketio.emit("gameover", room=id)
        return
    unencryptedWord = client[id]["words"][round]  #  unencrypted word

    # encrypt the word
    key = unencryptedWord[1][0] + "*"
    for i in range(2, len(unencryptedWord[1])):
        if random.randint(0, 1) == 1 and unencryptedWord[1][i] != '-':
            key += "*"
        else:
            key += unencryptedWord[1][i]

    # 向客户端发送单词
    socketio.emit("word", {"word": key, "explanation": unencryptedWord[2]}, room=id)


@socketio.on("submit")
def submit_word(user_submit, user_round):
    id = request.sid
    # 判断是否在client中
    if id in client:
        print(f"Client {id} reconnected")
    else:
        print(f"Client {id} disconnected")
        return
    clientTime = client[id]["time"]
    client[id]["time"] = time.time()
    print("user submit:" + user_submit)
    round = client[id]["round"]
    answer = client[id]["words"][round][1]

    # 错误轮次
    # 这行代码主要是解决，当user发过来的一瞬间，后台系统已经判定超时了
    if user_round != round + 1:
        return

    # BUG:这里有一个并发隐患，当代码运行到这一段的时候 下面维护的client[id]['round']可能已经被更新了，要加锁
    # 判断是否正确
    if user_submit == answer:
        client[id]["score"] += 1
        client[id]["history"].append(1)
        client[id]["consumption"] += time.time()- clientTime
        socketio.emit("correct", {"answer": answer}, room=id)
        print(f"Client {id} submit correct")
    else:
        socketio.emit("wrong", {"answer": answer}, room=id)
        client[id]["history"].append(0)
        print(f"Client {id} submit wrong")

    # 消耗的时间 / 正确的个数
    db.update_score(client[id]["stuId"], client[id]["score"], client[id]["consumption"])
    # 更新round
    client[id]["round"] += 1


@socketio.on("start")
def handle_start(stuId):
    id = request.sid
    print(f"Client {id} start")
    # 检测用户的time是否>0
    if db.check_id(stuId)[2] < 0:
        socketio.emit("reject", room=id)
        return
    db.update_times(stuId, -1)

    # 客户端注册
    client[id] = {
        "time": time.time(),
        "stuId": stuId,
        "score": 0,
        "round": 0,
        "words": db.get_word(),
        "history": [],
        "consumption": 0,
    }

    print(f'words: {client[id]["words"]}')
    # 向客户端发送accept消息
    socketio.emit("accept", room=id)


# 结算
def handle_disconnect(cid):
    # disconnect
    print(cid + " disconnected")
    # delete
    if cid in client:
        del client[cid]


# 维护玩家信息
def check_timeout():
    while True:
        now = time.time()
        # cline的key
        for id in list(client.keys()):
            sendPlayerInfo = {}
            sendPlayerInfo["score"] = client[id]["score"]
            sendPlayerInfo["time"] = GAMETIME - (now - client[id]["time"])
            sendPlayerInfo["history"] = client[id]["history"]
            if sendPlayerInfo["time"] < 0:
                if client[id]["round"] >= MAXROUND:
                    handle_disconnect(id)
                    socketio.emit("gameover", room=id)
                else:
                    socketio.emit(
                        "wrong",
                        {"answer": client[id]["words"][client[id]["round"]][1]},
                        room=id,
                    )
                    client[id]["round"] += 1
                    client[id]["history"].append(0)
                    client[id]["time"] = time.time()
                continue
            else:
                socketio.emit("update", sendPlayerInfo, room=id)
        socketio.sleep(0.5)


# 每日更新数据 这里需要优化）
def renew_daily():
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            db.renew_daily()
            socketio.sleep(60)
        socketio.sleep(1)


if __name__ == "__main__":
    socketio.start_background_task(target=check_timeout)
    socketio.start_background_task(target=renew_daily)
    socketio.run(app,allow_unsafe_werkzeug=True) 
