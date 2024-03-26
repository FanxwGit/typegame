from flask import Flask, request,jsonify, render_template
from flask_socketio import SocketIO, disconnect, emit
from datetime import datetime, timedelta
import random
import json
import db.db as db
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 存储客户端信息
client = {}

# game time
GAMETIME = 10

# max round
MAXROUND = 10

# route
@app.route('/')
def index():
    return render_template('index.html')

# 查询用户信息
# return {status:1或0, msg:' ', stuId: 'xxx', times: 1或0}
@app.route('/api/getuser', methods=['GET'])# calhost:5000/api/getuser?stuId=xxx
def get_connection_status():
    res = db.check_id(request.args.get('stuId'))
    if res != None:
        return jsonify({'status':1, 'msg':'Success', 'stuId':res[1], 'times':res[2], 'score':res[3]})
    else:
        return jsonify({'status':0, 'msg':'Invalid', 'stuId':'', 'times':0})

# get_rank api
@app.route('/api/getrank', methods=['GET'])
def get_rank():
    result = db.get_rank()
    return jsonify(result)

@socketio.on('query')
def query_word():
    
    # print("client query the word")
    id = request.sid
    # 判断是否在client中
    if id in client:
        print(f"Client {client[id]['stuId']} reconnected")
    else:
        socketio.emit('reject', room=id)
        return
    
    client[id]['time'] = datetime.now()
    round = client[id]['round']
    if round == 10:
        handle_disconnect(id)
        socketio.emit('gameover', room=id)
        return
    unencryptedWord = client[id]['words'][round] #  unencrypted word

    # encrypt the word
    key = unencryptedWord[1][0] + "*"
    for i in range(2, len(unencryptedWord[1])):
        if random.randint(0, 1) == 1:
            key += "*"
        else:
            key += unencryptedWord[1][i]
    
    # 向客户端发送单词
    socketio.emit('word', {'word':key, "explanation":unencryptedWord[2]}, room=id)

@socketio.on('submit')
def submit_word(user_submit, user_round):
    id = request.sid
    # 判断是否在client中
    if id in client:
        print(f'Client {id} reconnected')
    else:
        # 
        print(f'Client {id} disconnected')
        return
 
    client[id]['time'] = datetime.now()
    print("user submit:" + user_submit)
    round = client[id]['round']
    answer = client[id]['words'][round][1]

   # 错误轮次
    if user_round != round + 1:
        return
    
    # 判断是否正确
    if user_submit == answer:
        client[id]['score'] += 1
        client[id]['history'].append(1)
        socketio.emit('correct',{'answer':answer}, room=id)
        print(f'Client {id} submit correct')    
    else:
        socketio.emit('wrong',{'answer':answer}, room=id)
        client[id]['history'].append(0)
        print(f'Client {id} submit wrong')

    db.update_score(client[id]['stuId'], client[id]['score'])
    # 更新round
    client[id]['round'] += 1
    
@socketio.on('start')
def handle_start(stuId):
    id = request.sid
    print(f'Client {id} start')
    # 检测用户的time是否>0
    if db.check_id(stuId)[2] < 0:
        socketio.emit('reject', room=id)
        return
    db.update_times(stuId, -1)      

    # 客户端注册
    client[id] = {'time':datetime.now(), 'stuId':stuId, 'score':0, 'round':0, 'words':db.get_word(),'history':[]}

    print(f'words: {client[id]["words"]}')
    # 向客户端发送accept消息
    socketio.emit('accept', room=id) 

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
        now = datetime.now()
        # cline的key
        for id in list(client.keys()):
            playerInfo = {}
            playerInfo['score'] = client[id]['score']
            playerInfo['time'] = GAMETIME - (now - client[id]['time']).seconds 
            playerInfo['history'] = client[id]['history']
            if playerInfo['time'] < 0:
                if client[id]['round'] >= MAXROUND:
                    handle_disconnect(id)
                    socketio.emit('gameover', room=id)
                else:
                    client[id]['round']+=1
                    client[id]['history'].append(0)
                    socketio.emit('timeout', room=id)

                continue
            else:
                socketio.emit('update', playerInfo, room=id)
        socketio.sleep(1)       

# 每日更新数据 这里需要优化）
def renew_daily():
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            out = now.strftime("%Y-%m-%d")
            print(out)
            file = open("/home/fxw/workspace/typegame/rank.log", "a")
            file.write(out + "\n")
            for i in db.get_rank():
                file.write(str(i) + "\n")
            file.close()
            db.init()
            socketio.sleep(60)
                
if __name__ == '__main__':
    socketio.start_background_task(target=check_timeout)
    socketio.start_background_task(target=renew_daily)
    socketio.run(app)   