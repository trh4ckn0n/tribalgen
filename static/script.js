
function generateImage() {
    const prompt = document.getElementById("promptInput").value;
    const count = parseInt(document.getElementById("imageCount").value || 1);
    fetch("/generate", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt, count})
    })
    .then(res => res.json())
    .then(data => {
        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = `<h2>R茅sultats (${data.urls.length}) :</h2>`;
        data.urls.forEach(url => {
            resultDiv.innerHTML += `
                <div>
                    <img src="${url}" alt="Motif g茅n茅r茅">
                    <a href="${url}" download>馃捑 T茅l茅charger</a>
                    <button onclick="exportCapCut('${url}')">Export CapCut</button>
                </div><br>`;
        });
    });
}

function autoPrompt() {
    const theme = prompt("Style voulu ? (ex: azt猫que, cyber, etc)");
    fetch("/auto_prompt", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({theme})
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("promptInput").value = data.prompt;
    });
}

function usePreset() {
    const value = document.getElementById("presetSelect").value;
    document.getElementById("promptInput").value = value;
}

function loadHistory() {
    fetch("/history")
    .then(res => res.json())
    .then(history => {
        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = "<h2>馃晿 Historique :</h2>";
        history.forEach(entry => {
            resultDiv.innerHTML += `
                <div>
                    <p><strong>${entry.prompt}</strong> (${entry.date})</p>
                    <img src="${entry.url}" alt="image"><br>
                    <a href="${entry.url}" download>馃捑</a>
                </div><br>`;
        });
    });
}

function exportCapCut(url){
    fetch("/capcut_json", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url})
    })
    .then(res => res.json())
    .then(json => {
        const blob = new Blob([JSON.stringify(json, null, 2)], {type: "application/json"});
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "capcut_export.json";
        link.click();
    });
}
