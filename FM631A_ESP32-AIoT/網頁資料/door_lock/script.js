// 定義名稱。要與 images 資料夾內相同名稱
var labels

const video1 = document.getElementById('inputVideo')
const conDev = document.getElementById('connDiv')
const discon = document.getElementById('disconnBtn')
const con = document.getElementById('connBtn')
const idn = document.getElementById('identify')
const connBtnImg = document.getElementById('connBtnImg')
const loadBLE = document.getElementById('loadBLE')
const inputtext = document.getElementById('inputtext')

setInterval(async () => {
    con.style.height = (con.offsetWidth / 1).toString() + "px"
    connBtnImg.style.height = (con.offsetWidth / 1.5).toString() + "px"
    connBtnImg.style.width = (con.offsetWidth / 2.5).toString() + "px"
    checkCookie()
}, 100)

// 儲存 cookie 的值(cookie的名字、cookie的值、儲存的天數)
function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000 + 8 * 60 * 60 * 1000));   // 因為是毫秒, 所以要乘以1000
    var expires = "expires=" + d.toGMTString();
    document.cookie = cname + "=" + cvalue + "; " + expires;
}

// 得到 cookie 的值
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i].trim();
        if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
    }
    return "";
}

var first = false  // 是否初始化網頁
var last_name = getCookie("name")

// 確認 cookie 的值
function checkCookie() {
    var name = ""
    if (first == false) {
        // 從 Cookie 中取值
        name = getCookie("name");
        inputtext.value = name
        first = true
    }

    name = inputtext.value

    if (name != last_name) {
        setCookie("name", name, 30);
        console.log("change:", name)
    }
    last_name = name
}

// 先讀取完模型再開啟攝影機
function loadModel() {
    Promise.all([
        faceapi.nets.ssdMobilenetv1.loadFromUri('./models'),
        faceapi.nets.faceRecognitionNet.loadFromUri('./models'),
        faceapi.nets.faceLandmark68Net.loadFromUri('./models'),
        console.log("模型載入成功"),
        checkCookie()
    ]).then(startVideo)
}

async function startVideo() {
    await navigator.mediaDevices.getUserMedia({ video: {} },)
        .then(function (stream) {
            console.log("setting")
            video1.setAttribute("autoplay", "true");
            video1.setAttribute("playsinline", "true");
            video1.setAttribute("muted", "true");
            video1.setAttribute("loop", "true");
            //video1.setAttribute("controls", "true");
            video1.srcObject = stream;
        })
    await video1.play();
    canRecognizeFaces(0)
}

var labeledDescriptors;
var faceMatcher;
var canvas;
var detections;
var resizedDetections;
var results;
var init = false;


function changeCanvasSize() {
    setInterval(async () => {
        canvas.style.width = video1.offsetWidth.toString() + "px"
        canvas.style.height = video1.offsetHeight.toString() + "px"
        canvas.style.left = getPosition(video1)["x"] + "px";
        canvas.style.top = getPosition(video1)["y"] + "px";
    }, 100)
}

async function canRecognizeFaces(sta) {
    if (init == false) {
        console.log(init)
        console.log("初始化成功")
        labels = inputtext.value.toString().split(",")    // 將輸入框的值切割出來
        console.log(labels)
        labeledDescriptors = await loadLabel()
        // 描述標籤
        console.log(labeledDescriptors)
        faceMatcher = new faceapi.FaceMatcher(labeledDescriptors, 0.7)
        canvas = faceapi.createCanvasFromMedia(video1)
        document.body.append(canvas)
        mask.style.display = "none"
        loadImg.style.display = "none"
        changeCanvasSize()
        // 將 canvas 的位置設定成與影像一樣
        canvas.style.left = getPosition(video1)["x"] + "px";
        canvas.style.top = getPosition(video1)["y"] + "px";
        displaySize = { width: video1.offsetWidth, height: video1.offsetHeight }
        faceapi.matchDimensions(canvas, displaySize)
        init = true
    }
    if (init == true && sta == 1) {
        displaySize = { width: video1.offsetWidth, height: video1.offsetHeight }
        faceapi.matchDimensions(canvas, displaySize) ///
        detections = await faceapi.detectAllFaces(video1).withFaceLandmarks().withFaceDescriptors()
        resizedDetections = faceapi.resizeResults(detections, displaySize)
        canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
        results = resizedDetections.map((d) => {
            return faceMatcher.findBestMatch(d.descriptor)
        })

        results.forEach((result, i) => {
            console.log(results[i]["label"])     // 顯示所有偵測到的名稱
            sendMsg(results[i]["label"] + ":" + results[i]["distance"])
            const box = resizedDetections[i].detection.box
            const drawBox = new faceapi.draw.DrawBox(box, { label: result })
            drawBox.draw(canvas)
        })
        setTimeout(async () => {
            canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
        }, 1000)
    }
}

$('#identify').click((e) => {
    console.log("辨識")
    canRecognizeFaces(1);
});

function loadLabel() {
    var labels_len = labels.length;
    var succ = true;
    return Promise.all(
        labels.map(async (label) => {
            console.log(label)
            const descriptions = []
            for (let i = 1; i <= 3; i++) {
                try {
                    img = await faceapi.fetchImage(`images/${label}/${i}.jpg`)
                }
                catch (e) {
                    console.log("換PNG啦")
                    try {
                        img = await faceapi.fetchImage(`images/${label}/${i}.png`)
                    }
                    catch (err) {
                        console.log("錯誤啊!!!")
                        succ = false
                    }
                }
                if (succ) {
                    const detections = await faceapi.detectSingleFace(img).withFaceLandmarks().withFaceDescriptor()
                    descriptions.push(detections.descriptor)
                }
            }
            labels_len--
            if (labels_len == 0 && !succ) {
                alert("名稱有誤, 請重新確認!!");
                window.location.reload()
            }
            return new faceapi.LabeledFaceDescriptors(label, descriptions)
        })
    )
}

// 取得元素位置
function getPosition(element) {
    var x = 0;
    var y = 0;
    while (element) {
        x += element.offsetLeft - element.scrollLeft + element.clientLeft;
        y += element.offsetTop - element.scrollLeft + element.clientTop;
        element = element.offsetParent;
    }
    return { x: x, y: y };
}



// 藍牙設定---------------------------------------------------
const UART_SERVICE = "6e400001-b5a3-f393-e0a9-e50e24dcca9e";
const RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e";
const TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e";
var BLEDevice = null;
var UARTService = null;

// 連線藍牙
async function connectBLE() {
    let opt = {
        // 會搜尋所有藍牙裝置
        acceptAllDevices: true,
        optionalServices: [UART_SERVICE]
        // 限制搜尋到的藍牙裝置
        //filters: [
        //    { namePrefix: 'ESP32' },
        //    { services: [UART_SERVICE] }
        //],
    }

    try {
        console.log('請求BLE裝置連線…');
        // 連線藍牙裝置
        BLEDevice = await navigator.bluetooth.requestDevice(opt);
        mask.style.display = "block",
            loadImg.style.display = "none",
            loadBLE.style.display = "block",
            console.log('裝置名稱：' + BLEDevice.name);
        con.style.display = "none"        // 不顯連線按鈕
        connBtnImg.style.display = "none"
        inputtext.style.display = "none"
        video1.style.display = "block";
        conDev.style.display = "block";   // 顯示連線裝置
        //discon.style.display = "block";   // 顯示關閉連線按鈕
        idn.style.display = "block";      // 顯示辨識按鈕
        $("#deviceName").text(BLEDevice.name);

        console.log('連接GATT伺服器…');
        const server = await BLEDevice.gatt.connect();

        console.log('取得UART服務…');
        UARTService = await server.getPrimaryService(UART_SERVICE);

        console.log('取得TX特徵…');
        const txChar = await UARTService.getCharacteristic(TX_UUID);

        await txChar.startNotifications();

        txChar.addEventListener('characteristicvaluechanged',
            e => {
                let val = e.target.value;
                let str = new TextDecoder("utf-8").decode(val)
                $('#magnet').text(str)
            }
        );
        loadBLE.style.display = "none",
            mask.style.display = "block",
            loadImg.style.display = "block",
            loadModel();
    } catch (err) {
        console.log('出錯啦～' + err);
    }
}


$("#connBtn").click((e) => {
    if (!navigator.bluetooth) {
        console.log('你的瀏覽器不支援Web Bluetooth API，換一個吧～');
        return false;
    }
    connectBLE();
});


async function sendMsg(msg) {
    if (!BLEDevice) {
        return;
    }
    // 如果藍芽裝置有連接GATT伺服器
    if (BLEDevice.gatt.connected) {
        try {
            const uartChar = await UARTService.getCharacteristic(RX_UUID);
            let enc = new TextEncoder();
            uartChar.writeValue(
                enc.encode(msg),
            )
        } catch (err) {
            console.log('出錯啦～' + err);
        }

    } else {
        return;
    }
}