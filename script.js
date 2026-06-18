const video = document.getElementById("videoEl");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const API_URL = "https://thebell-010-sibi-recognition.hf.space/predict";
let predicting = false;

navigator.mediaDevices.getUserMedia({video: true})
    .then(stream => {
        video.srcObject = stream;
        startLoop();
    })
    .catch(() => alert("Camera not found"));

async function predict(){
    if (predicting) return;
    predicting = true;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {
        const form = new FormData();
        form.append("file", blob, "frame.jpg");

        try {
            const res = await fetch(API_URL, {method: "POST", body: form});
            const data = await res.json();

            if (data.success) {
                document.getElementById("knn-label").textContent = data.KNN_Model.label;
                document.getElementById("knn-conf").textContent = `${data.KNN_Model.confidence}%`;
                document.getElementById("knn-time").textContent = `${data.KNN_Model.time_ms}ms`;

                document.getElementById("rf-label").textContent = data.RF_Model.label;
                document.getElementById("rf-conf").textContent = `${data.RF_Model.confidence}%`;
                document.getElementById("rf-time").textContent = `${data.RF_Model.time_ms}ms`;

                document.getElementById("ens-label").textContent = data.Ensemble_Model.label;
                document.getElementById("ens-conf").textContent = `${data.Ensemble_Model.confidence}%`;
                document.getElementById("ens-time").textContent = `${data.Ensemble_Model.time_ms}ms`;
            } 
        } catch {
        }

        predicting = false;
    }, "image/jpeg", 0.85);
}

function startLoop() {
    setInterval(predict, 500);
}

function switchTab(tab) {
    document.getElementById("panel-detect").style.display = tab === "detect" ? "block" : "none";
    document.getElementById("panel-translate").style.display = tab === "translate" ? "block" : "none";
    document.getElementById("tab-detect").classList.toggle("active", tab === "detect");
    document.getElementById("tab-translate").classList.toggle("active", tab === "translate");
}

function showGestures() {
    const word = document.getElementById("wordInput").value.toUpperCase();
    const display = document.getElementById("gestureDisplay");
    display.innerHTML = "";

    if (word.trim() === "") {
        display.innerHTML = "<p class='text-muted'>Please enter a word first.</p>";
        return;
    }

    for (let char of word) {
        if (!/^[A-Z]$/.test(char) || char === "J" || char === "Z") continue;

        const div = document.createElement("div");
        div.className = "gesture-card";
        div.innerHTML = `
            <img src="images/${char}.jpg"
                alt="${char}"
                onerror="this.src='images/unknown.jpg'">
            <p>${char}</p>
        `;
        display.appendChild(div);
    }
}