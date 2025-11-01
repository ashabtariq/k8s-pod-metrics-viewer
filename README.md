# 🚀 Kubernetes Pod Metrics Viewer (Flask + Redis + Socket.IO)

A lightweight real-time **Kubernetes Pod Metrics Dashboard** built with **Flask**, **Socket.IO**, and **Redis**.  
It displays live CPU and memory usage for pods running in your cluster using the **Kubernetes Metrics API**.

---

## 🧩 Features

- 🔹 Real-time pod metrics using `metrics.k8s.io`
- 🔹 Live updates over WebSockets (Flask-SocketIO)
- 🔹 Persistent visitor counter backed by Redis
- 🔹 Works both **inside Kubernetes** and **locally**
- 🔹 Responsive frontend served directly from Flask
- 🔹 Auto-reconnect and smooth refresh via Socket.IO

---

## 🏗️ Architecture Overview

```
        ┌──────────────────┐
        │  Flask + SocketIO│
        │ (Pod Metrics API)│
        └───────┬──────────┘
                │
     ┌──────────┴──────────┐
     │                     │
 ┌────────────┐      ┌───────────┐
 │ Redis Pod  │◄────►│  Frontend │
 └────────────┘      └───────────┘
         ▲
         │
 ┌───────────────────────────┐
 │ Kubernetes Metrics Server │
 └───────────────────────────┘
```

---

## ⚙️ Technologies Used

| Component | Purpose |
|------------|----------|
| **Flask** | Web server and API backend |
| **Flask-SocketIO** | Real-time WebSocket communication |
| **Redis** | Visitor counter and caching backend |
| **Kubernetes Python Client** | Interacts with K8s API to fetch pod info |
| **dotenv** | Loads environment variables |
| **Gunicorn + Eventlet** | Production-ready async web server |

---

## 📦 Directory Structure

```
├── app.py                # Main Flask application
├── templates/
│   └── pods.html         # HTML dashboard
├── requirements.txt
├── Dockerfile
├── k8s/
│   ├── visitor-stack.yaml     # Flask app Deployment + Service + Ingress + Redis
|   |── RBAC.yaml              # RBAC Control for fetching pods metrics
└── README.md
```

---

## 🐳 Running Locally

### 1️⃣ Clone the repo
```bash
git clone https://github.com/ashabtariq/k8s-pod-metrics-viewer.git
cd k8s-pod-metrics-viewer
```

### 2️⃣ Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Run locally (requires `kubectl` context)
```bash
python3 app.py
```

Then open [http://localhost:5000](http://localhost:5000)

---

## ☸️ Running on Kubernetes

```
### 1️⃣ Apply Stack File

```bash

cd k8s
kubectl apply -f .

```

### 4️⃣ Access the dashboard

If you’re using Minikube:

```bash
minikube service frontend

```

Or if you have Ingress enabled, open:

```
https://YOUD DOMAIN <-- ADD YOUR DOMAIN HERE
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|-----------|----------|-------------|
| `REDIS_HOST` | `redis-instance` | Hostname for Redis service |
| `REDIS_PORT` | `6379` | Redis port |

---

## 🧠 Notes

- The app automatically detects whether it’s running **inside** or **outside** a Kubernetes cluster:
  - Inside cluster → uses `load_incluster_config()`
  - Outside cluster → falls back to `~/.kube/config`
- Redis is used only for a **simple visitor counter** (you can replace it with a database or disable it easily).

---

## 🧰 Useful Commands

```bash
# Check pod status
kubectl get pods -o wide

# View logs
kubectl logs -l app=frontend

# Delete resources
kubectl delete -f k8s/
```

---

## 🧑‍💻 Author

**Ashab Tariq**  
Cloud • DevOps • Security Engineer  
---

## 📄 License

MIT License © 2025 Ashab Tariq
