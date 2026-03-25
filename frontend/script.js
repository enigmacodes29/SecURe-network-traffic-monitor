let chart;
function showSection(section, btn) {
  // hide all sections
  document.querySelectorAll(".section").forEach(div => {
    div.classList.remove("active");
  });

  // remove active button highlight
  document.querySelectorAll(".nav-btn").forEach(b => {
    b.classList.remove("active");
  });

  // show correct section
  if (section === "logs") {
    document.getElementById("logsSection").classList.add("active");
  } else if (section === "alerts") {
    document.getElementById("alertsSection").classList.add("active");
  } else {
    document.getElementById(section).classList.add("active");
  }

  // highlight active button
  if (btn) btn.classList.add("active");
}

async function loadLogs() {
  let res = await fetch("http://localhost:8000/logs");
  let data = await res.json();

  // logs
  let logsDiv = document.getElementById("logs");
  logsDiv.innerHTML = "";
  data.logs.forEach(log => {
    logsDiv.innerHTML += `<p>${log.ip} - ${log.status}</p>`;
  });

  // alerts
  let alertsDiv = document.getElementById("alerts");
  alertsDiv.innerHTML = "";
  data.alerts.forEach(alert => {
    alertsDiv.innerHTML += `<p>${alert}</p>`;
  });

  // stats
  document.getElementById("count").innerText = data.logs.length;

 
data.logs.forEach(log => {
  if (log.status === "OK") ok++;
  else failed++;
});

let ok = 0;
let failed = 0;

data.logs.forEach(log => {
  if (log.status === "OK") ok++;
  else failed++;
});

// destroy old chart if exists
if (chart) {
  chart.destroy();
}

const ctx = document.getElementById("trafficChart").getContext("2d");

chart = new Chart(ctx, {
  type: "bar",
  data: {
    labels: ["Successful", "Failed"],
    datasets: [{
      label: "Login Attempts",
      data: [ok, failed],
      backgroundColor: [
        "#a855f7",   // purple
        "#facc15"    // yellow
      ],
      borderRadius: 8
    }]
  },
  options: {
    plugins: {
      legend: {
        labels: {
          color: "#f5f3ff"
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: "#ddd6fe"
        },
        grid: {
          color: "rgba(255,255,255,0.05)"
        }
      },
      y: {
        ticks: {
          color: "#ddd6fe"
        },
        grid: {
          color: "rgba(255,255,255,0.05)"
        }
      }
    }
  }
});
}

async function encrypt() {
  let res = await fetch("http://localhost:8000/encrypt", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: message.value})
  });

  let data = await res.json();
  document.getElementById("enc").innerText = data.encrypted;
}

async function decrypt() {
  let encrypted = document.getElementById("enc").innerText;

  let res = await fetch("http://localhost:8000/decrypt", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: encrypted})
  });

  let data = await res.json();
  document.getElementById("dec").innerText = data.decrypted;
}

async function getKey() {
  let res = await fetch("http://localhost:8000/key");
  let data = await res.json();
  document.getElementById("key").innerText = data.key;
}



// sample alerts (always show something cool)
let sampleAlerts = [
  "🚨 Unauthorized access attempt detected",
  "⚠️ Multiple failed login attempts",
  "🔐 Suspicious encryption activity",
  "📡 Unusual outbound traffic"
];

// combine backend + sample
let allAlerts = [...data.alerts, ...sampleAlerts];

// remove duplicates
allAlerts = [...new Set(allAlerts)];

let alertsDiv = document.getElementById("alerts");
alertsDiv.innerHTML = "";

allAlerts.forEach(alert => {
  alertsDiv.innerHTML += `<p>${alert}</p>`;
});


// default load
 // refresh every 5 sec

// set default active tab
document.querySelectorAll(".nav-btn")[0].classList.add("active");
showSection("home");
setInterval(loadLogs, 5000);
