# Business Analytics Dashboard

A Flask-based web application that allows users to upload CSV sales data, generate charts, perform revenue forecasting, segment customers using clustering, and visualize insights — all through a simple web interface.

---

## 🔧 Features

* 📂 Upload CSV files securely
* 📊 Generate interactive bar, line, and pie charts
* 📈 Forecast revenue trends using 3-day moving average
* 👥 Segment customers based on revenue using K-Means clustering
* 📤 Session-based CSV reuse (no need to re-upload)

---

## 📁 Project Structure

```
├── app.py               # Main Flask app
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment config
├── runtime.txt          # Python runtime version
├── Procfile             # For platforms like Heroku
├── data/                # Example/sample data CSVs
├── reports/             # Reserved for future PDF report generation
├── static/              # Uploaded files & static assets
├── templates/           # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── forecast.html
│   ├── segment.html
│   └── upload.html
└── users.json           # (Optional) Placeholder for persistent user storage
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/business-analytics-dashboard.git
cd business-analytics-dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

---

## 📝 Usage Guide

### Step 1: Register/Login

* Visit `/register` to create a new account.
* Login at `/login`.

### Step 2: Upload CSV

* Upload a `.csv` with columns like:

  * `Date`, `Product`, `Revenue`, `Cost`, `Customer Email`

### Step 3: Generate Charts

* Choose chart type (bar, line, pie)
* Select a metric (Revenue or Profit)

### Step 4: Forecast Revenue

* Navigate to `/forecast` to view 3-day moving average revenue forecasts

### Step 5: Customer Segmentation

* Go to `/segment` to segment customers using KMeans clustering

---

## 📌 Notes

* CSV is stored in-session; you do **not** need to re-upload for every action.
* "Profit" is auto-computed if `Revenue` and `Cost` are present.
* Charts are dynamically generated and embedded via base64.

---

## 🧠 Future Improvements

* 🧾 Auto-generate downloadable PDF reports
* 📬 Email PDF summaries to users
* 📈 Add more advanced ML-based forecasts (ARIMA, Prophet)

---

## 🛠 Tech Stack

* Python 3.x
* Flask
* Pandas, Matplotlib, Seaborn
* scikit-learn (KMeans)
* HTML/CSS with Jinja2 Templates

---

## 🖼️ Sample Data

Make sure your CSV has a structure similar to:

```csv
Date,Product,Category,Units Sold,Revenue,Cost,Customer Name,Customer Email,Location,Customer Type,Stock Level
2024-06-01,TV,Electronics,10,50000,40000,John Doe,john@example.com,Delhi,Returning,20
...
```

---

## 📤 Deployment

Supports Render, Railway, and similar platforms.
Ensure `render.yaml`, `Procfile`, and `runtime.txt` are configured.

---

## ⚖️ License

MIT License

---

## 🌐 Live Demo

[https://web-production-451ec.up.railway.app](https://web-production-451ec.up.railway.app)

---

## 👨‍💼 Author

**Priya Sharma**
[LinkedIn Profile]https://www.linkedin.com/in/priya-sharma-blockchain/
*Powered by e-Infosoft*
