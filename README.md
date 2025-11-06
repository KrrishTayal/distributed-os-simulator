# ☁️ Cloud OS Simulator

A **Cloud-based Operating System Simulator** that demonstrates **CPU Scheduling (Round Robin)** and **Dynamic Memory Allocation** in a **distributed environment** using an interactive Streamlit web app.

---

## 🚀 Features

✅ Simulates **Round Robin scheduling** across multiple worker nodes  
✅ Each worker acts as a cloud server with limited memory (100 MB)  
✅ **Dynamic memory allocation** — tasks request and release memory  
✅ Real-time **visual dashboard** for tasks, workers, and memory usage  
✅ Built using **Streamlit** and **Python**

---

## 🧠 Objective

> To simulate scheduling and memory allocation in a cloud-based distributed environment — mimicking how modern operating systems allocate CPU time and memory resources fairly among parallel tasks.

---

## 🏗️ Architecture Overview

- **Tasks** → represent processes with burst time and memory requirement  
- **Workers** → represent distributed nodes with their own memory  
- **Scheduler** → implements Round Robin CPU scheduling  
- **Memory Manager** → allocates and frees memory dynamically  
- **UI** → Streamlit dashboard for visualization  

---

## 📸 Live Preview

🔗 **[Run the App on Streamlit Cloud](https://distributed-os-simulator-4kq9ue9w2f3zk4tiwbziqz.streamlit.app/)**

---

## ⚙️ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/krrishtayal/cloud-os-simulator.git
cd cloud-os-simulator
```

2️⃣ Install the requirements

streamlit

pandas

numpy

matplotlib

time

3️⃣ Run the app
```bash
streamlit run app.py
