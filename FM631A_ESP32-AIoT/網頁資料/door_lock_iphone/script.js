// 定義名稱。要與 images 資料夾內相同名稱 
var labels = prompt("請輸入名稱並以逗號隔開人名:","Teddy,Chuan").toString().split(",")
var username = prompt("請輸入 AIO 使用者名稱:","flagweng")

const video1 = document.getElementById('inputVideo')
const conDev = document.getElementById('connDiv') 
const discon = document.getElementById('disconnBtn')
const con = document.getElementById('connBtn')
const idn = document.getElementById('identify')
const connBtnImg = document.getElementById('connBtnImg')
const inputtext = document.getElementById('inputtext')

// 讓輸入框圓角一點  需要 jquery-ui.min.js 和 jquery-ui.min.css
$('input:text').addClass("ui-widget ui-widget-content ui-corner-all ui-textfield");

setInterval(async () => {
    inputtext.style.width = video1.offsetWidth.toString()+"px"
    inputtext.style.height = video1.offsetHeight.toString()/8+"px"
    idn.style.height = video1.offsetHeight.toString()/8+"px"
    idn.style.fontSize = video1.offsetHeight.toString()/15+"px"
    checkCookie()
},100)

// 儲存 cookie 的值(cookie的名字、cookie的值、儲存的天數)
function setCookie(cname,cvalue,exdays)
{
  var d = new Date();
  d.setTime(d.getTime()+(exdays*24*60*60*1000+8*60*60*1000));   // 因為是毫秒, 所以要乘以1000
  var expires = "expires="+d.toGMTString();
  document.cookie = cname + "=" + cvalue + "; " + expires;
}

// 得到 cookie 的值
function getCookie(cname)
{
  var name = cname + "=";
  var ca = document.cookie.split(';');
  for(var i=0; i<ca.length; i++) 
  {
    var c = ca[i].trim();
    if (c.indexOf(name)==0) return c.substring(name.length,c.length);
  }
  return "";
}

var first = false  // 是否初始化網頁
var last_key = getCookie("key")

// 確認 cookie 的值
function checkCookie()
{
  var key = ""
  if(first == false){
    // 從 Cookie 中取值
    key = getCookie("key");
    inputtext.value = key
    first = true
  }

  key = inputtext.value

  //if (key != "" && key != null)
  if(key != last_key)
  {
    setCookie("key",key,30);
    console.log("change:",key)
  }
  last_key = key
}

Promise.all([
    inputtext.style.width = video1.offsetWidth.toString()+"px",
    inputtext.style.height = video1.offsetHeight.toString()/8+"px",
    mask.style.display = "block",
    loadImg.style.display = "block",
    checkCookie(),
    faceapi.nets.ssdMobilenetv1.loadFromUri('./models'),
    faceapi.nets.faceRecognitionNet.loadFromUri('./models'), 
    faceapi.nets.faceLandmark68Net.loadFromUri('./models'),
    console.log("模型載入成功"),
    ]).then(startVideo)

async function startVideo(){
    await navigator.mediaDevices.getUserMedia({video: {}},)   
      .then(function(stream){
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


function  changeCanvasSize(){
    setInterval(async () => {
        canvas.style.width = video1.offsetWidth.toString()+"px"
        canvas.style.height = video1.offsetHeight.toString()+"px"
        canvas.style.left = getPosition(video1)["x"] + "px";
        canvas.style.top = getPosition(video1)["y"] + "px";
    }, 100)
}

async function canRecognizeFaces(sta){
    if(init == false){
        console.log(init)
        console.log("初始化成功")
        labeledDescriptors = await loadLabel()
        // 描述標籤
        console.log(labeledDescriptors)
        faceMatcher = new faceapi.FaceMatcher(labeledDescriptors,0.7)
        canvas =  faceapi.createCanvasFromMedia(video1)
        document.body.append(canvas)
        mask.style.display = "none"
        loadImg.style.display = "none"
        changeCanvasSize()
        // 將 canvas 的位置設定成與影像一樣
        canvas.style.left = getPosition(video1)["x"] + "px";
        canvas.style.top = getPosition(video1)["y"] + "px";
        displaySize = { width: video1.offsetWidth, height: video1.offsetHeight}
        faceapi.matchDimensions(canvas, displaySize)
        init = true
    }
    if(init == true && sta==1){   
        displaySize = { width: video1.offsetWidth, height: video1.offsetHeight}
        faceapi.matchDimensions(canvas, displaySize) ///
        detections = await faceapi.detectAllFaces(video1).withFaceLandmarks().withFaceDescriptors()
        resizedDetections = faceapi.resizeResults(detections, displaySize)
        canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
        results = resizedDetections.map((d) => {
            return faceMatcher.findBestMatch(d.descriptor)
        })

        results.forEach((result,i) =>{
            console.log(results[i]["label"])     // 顯示所有偵測到的名稱
            lab = parseFloat(labels.indexOf(results[i]["label"]))
            dis = parseFloat(results[i]["distance"])
            //console.log(labels.indexOf(results[i]["label"]))
            console.log(lab+dis)
            //sendMsg(results[i]["label"]+":"+results[i]["distance"])

            $.ajax({
                url: "https://io.adafruit.com/api/v2/"+username+"/feeds/door/data?X-AIO-Key="+inputtext.value,
                type: "POST",
                data: {
                  "value":lab+dis
                },
              })

            const box = resizedDetections[i].detection.box
            const drawBox = new faceapi.draw.DrawBox(box, { label: result })
            drawBox.draw(canvas)
        })
        setTimeout(async () => {
            canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
        },1000)
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
function getPosition (element) {
    var x = 0;
    var y = 0;
    while ( element ) {
      x += element.offsetLeft - element.scrollLeft + element.clientLeft;
      y += element.offsetTop - element.scrollLeft + element.clientTop;
      element = element.offsetParent;
    }
    return { x: x, y: y };
  }