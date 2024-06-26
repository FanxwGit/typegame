// 混淆加密网址
// https://www.json.cn/jshx/
var word = "";
var maxWord = 15;
var gameTime = false; //判断是否是游戏时间
var round = 0; //本地的回合数
var pingInterval; // 定义开始定期发送 ping 的函数
var isSended = false; //判断是否已经发送
var question = ""; //题目
var isQuery = false; //判断是否已经查询过题目
// var pingUserInfo;

//sounds effect
// audioTyping = new Audio("static/sounds/type.mp3")
audioWrongBuzz = new Audio("static/sounds/wrong-buzz.mp3");
audioCorrectPop = new Audio("static/sounds/correct-pop.mp3");

// dom事件

// 监听键盘更新word，只接收字符和退格 最大长度为10
document.onkeydown = function (e) {
    if (isSended) {
        return;
    }
    e = e || window.event;
    var key = e.which || e.keyCode;
    if (key == 8) {
        word = word.substring(0, word.length - 1);
    }
    // /
    else if ((key >= 65 && key <= 90) || key == 189) {
        if (word.length < maxWord) {
            if (key >= 65 && key <= 90) {
                soundEffect("typing");
                word += String.fromCharCode(key).toLowerCase();
            } else if (key == 189) {
                soundEffect("typing");
                word += "-";
            }
        } else {
            warnning(".bottom");
        }
    }
    printword(word, ".bottom");
};
// 判断是否有cookie为stu-id的值,如果没有就弹输入框 然后注册进cookie里
function checkCookie() {
    var stuId = Cookies.get("stu-id");
    if (stuId == "" || stuId == null || stuId == undefined) {
        stuId = prompt("Please enter your student id:", "");
        if (stuId == "" || stuId == null || stuId == undefined) {
            //reload
            location.reload();
            return;
        }
    }
    //请求服务器 查询id是否合法
    var isIdExist = false;
    // 发get请求 /api/getuser?stuId=cookie
    fetch(`/api/getuser?stuId=${stuId}`)
        .then((response) => response.json())
        .then((data) => {
            if (data.status == 1) {
                document.querySelector("#stuid").innerText = `stuid: ${stuId}`;
                document.querySelector(
                    "#score"
                ).innerText = `score: ${data.score}`;
                updateEligibility(data.times);
                Cookies.set("stu-id", stuId, 30);
                startPinging();
            } else {
                alert("Invalid student id. Please try again.");
                Cookies.remove("stu-id");
                checkCookie();
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("Net error occurred. Please try again later.");
            checkCookie();
        });
    console.log("Welcome again " + stuId);
}

// 根据参数，打印到dom上
function printword(s, dom) {
    var bottom = document.querySelector(dom);
    // // 修改word里的文本
    bottom.innerText = s;
}
// sound effect
function soundEffect(type) {
    audioTyping = new Audio(
        "data:audio/mpeg;base64,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"
    );
    const audioMap = {
        correct: audioCorrectPop,
        wrong: audioWrongBuzz,
        typing: audioTyping,
        default: audioTyping,
    };
    const audio = audioMap[type] || audioMap.default;
    audio.play();
}
// 动画函数
function warnning(dom) {
    //把.bottom里面的字体变红0.5秒，再变回来，再变0.5 秒再回来
    var bottom = document.querySelector(dom);
    soundEffect("wrong");
    bottom.style.color = "red";
    setTimeout(() => {
        bottom.style.color = "black";
        setTimeout(() => {
            bottom.style.color = "red";
            setTimeout(() => {
                bottom.style.color = "black";
            }, 500);
        }, 500);
    }, 500);
}

// 动画函数
function correct(dom) {
    //把.bottom里面的字体变绿0.5秒，再变回来，异步
    var bottom = document.querySelector(dom);
    bottom.style.color = "green";
    soundEffect("correct");
    setTimeout(() => {
        bottom.style.color = "black";
        setTimeout(() => {
            bottom.style.color = "green";
            setTimeout(() => {
                bottom.style.color = "black";
            }, 500);
        }, 500);
    }, 500);
}

//检测键盘输入
function watching() {
    if (word == "go" && !gameTime) {
        gameTime = true;
        console.log("Sent start to server");
        fetch(`/api/getuser?stuId=${Cookies.get("stu-id")}`)
            .then((response) => response.json())
            .then((data) => {
                // console.log(data);
                if (data.status == 1) {
                    if (data.times < 1) {
                        msg = "You have already started the game today. ";
                        //修改mid里的
                        var mid = document.querySelector(".mid");
                        //变红色
                        mid.style.color = "red";
                        mid.innerText = msg;
                    } else {
                        //3秒倒计时 修改top里的 3 2 1
                        var top = document.querySelector(".top");
                        top.innerText = "3";
                        setTimeout(() => {
                            top.innerText = "2";
                            setTimeout(() => {
                                top.innerText = "1";
                                setTimeout(() => {
                                    top.innerText = "GO";
                                    setTimeout(() => {
                                        top.innerText = "";
                                        //游戏开始
                                        //发送请求
                                        socket.emit(
                                            "start",
                                            Cookies.get("stu-id")
                                        );
                                        // console.log("sended")
                                        round = 0;
                                    }, 1000);
                                }, 1000);
                            }, 1000);
                        }, 1000);
                    }
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("Net error occurred. Please try again later.");
                //刷新
                location.reload();
            })
            .finally(() => {
                word = "";
                printword(word, ".bottom");
            });
    } else if (gameTime) {
        //判断word的长度是否question的长度一致 触发submit
        if (!isSended && question != "" && word.length >= question.length) {
            //发送请求
            socket.emit("submit", word, round);
            console.log("Submit");
            isSended = true;
        }
    }
}

//获取排行榜
function getRank() {
    fetch(`/api/getrank`)
        .then((response) => response.json())
        .then((data) => {
            // console.log(data)
            var rankDom = document.querySelector(".leaderbord");
            var firstChild = rankDom.firstElementChild;
            rankDom.innerHTML = "";
            rankDom.appendChild(firstChild);
            // 在rankDom里面的末尾添加子div
            for (var i = 0; i < data.length; i++) {
                var rankItem = document.createElement("div");
                rankItem.className = "leaderbord-item";
                rankItem.innerText = `${data[i][0]} ${data[i][1]}`;
                //如果data[i].stuId = cookie的stu-id 那么就高亮
                if (data[i][0] == Cookies.get("stu-id")) {
                    rankItem.className += " leaderbord-highlight";
                }

                var tip = document.createElement("div");
                tip.className = "tip-box pixel";
                tip.innerText = `${data[i][2]}s`;
                rankItem.appendChild(tip);

                rankDom.appendChild(rankItem);
            }
        });
}

// 更新用户是否可玩的状态
function updateEligibility(state) {
    var eligibility = document.querySelector("#eligibility");
    if (state == 0) {
        eligibility.innerText = "ineligible";
        eligibility.style.color = "red";
    } else {
        eligibility.innerText = "eligible";
        eligibility.style.color = "green";
    }
}

// 获取用户最新消息 更新左侧状态栏
function queryUserInfo() {
    fetch(`/api/getuser?stuId=${Cookies.get("stu-id")}`)
        .then((response) => response.json())
        .then((data) => {
            if (data.status == 1) {
                document.querySelector(
                    "#stuid"
                ).innerText = `stuid: ${Cookies.get("stu-id")}`;
                document.querySelector(
                    "#score"
                ).innerText = `score: ${data.score}`;
                updateEligibility(data.times);
            }
        });
}

// 定时事件
function startPinging() {
    pingInterval = setInterval(watching, 200);
    // pingUserInfo = setInterval(queryUserInfo, 500);
    pingRank = setInterval(getRank, 3000);
}

function stopPinging() {
    clearInterval(pingInterval);
    // clearInterval(pingUserInfo);
    clearInterval(pingRank);
}

// 请求单词
function query() {
    // console.log("query the word from server")
    round++;
    socket.emit("query");
    queryUserInfo();
}
const socket = io();

//accpet 开始游戏
socket.on("accept", function () {
    console.log("Received accept from server");
    query();
});

/*
      //timeout 
    socket.on("timeout", function () {
        console.log("timeout");
        query();
    })
    */

//更新游戏信息 当前的时间, 当前的分数
socket.on("update", function (info) {
    // console.log(info)//score time
    document.querySelector("#lefttime").innerText = Math.ceil(info.time);
    // 获取round下面的所有div  info.history
    for (var i = 0; i < Math.min(info.history.length, 10); i++) {
        //第i个 div
        var roundBox = document.querySelector(
            ".round-box:nth-child(" + (i + 1) + ")"
        );
        if (info.history[i] == 1) {
            roundBox.style.backgroundColor = "green";
        } else {
            roundBox.style.backgroundColor = "red";
        }
    }
});

socket.on("reject", function (msg) {
    console.log("be rejected");
});

//服务器发题目
socket.on("word", function (data) {
    question = data.enpWord;
    //清空word
    word = "";
    printword(word, ".bottom");
    isSended = false;

    //mid
    document.querySelector(".mid").innerText = data.explanation;
    //top
    document.querySelector(".top").innerText = data.enpWord;

    // 创建Blob对象并播放语音
    const audioBlob = new Blob([new Uint8Array(data.audioData)], {
        type: "audio/mpeg",
    });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audioEl = new Audio(audioUrl);
    audioEl.play();

});

//答案错误
socket.on("wrong", function (msg) {
    document.querySelector(".top").innerText = msg.answer;
    warnning(".bottom");
    console.log("wrong");
    setTimeout(() => {
        query();
    }, 2000);
});

//答案正确
socket.on("correct", function (msg) {
    document.querySelector(".top").innerText = msg.answer;
    console.log("correct");
    correct(".bottom");
    setTimeout(() => {
        query();
    }, 2000);
});

//游戏结束 gameover
socket.on("gameover", function (msg) {
    stopPinging();
    console.log("game over");
    gameTime = false;
    //显示时间到
    var timeup = document.querySelector(".timeup");
    //文本修改time up
    timeup.style.display = "block";
    timeup.querySelector("p").innerText = "Game Over";
    //清空mid
    var mid = document.querySelector(".mid");
    mid.innerText = "Please reload the page to start a new game.";
    //清空top
    var top = document.querySelector(".top");
    top.innerText = "";
    //清空bottom
    var bottom = document.querySelector(".bottom");
    bottom.innerHTML = "";
    //清空gameinfo
    var gameinfo = document.querySelector(".gameinfo");
    gameinfo.style.display = "none";

    queryUserInfo();
});

// 在页面加载完成后调用检测函数
window.onload = function () {
    checkCookie();
    getRank();
    queryUserInfo();
};

setTimeout(stopPinging, 600000);
