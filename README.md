# e-Infosoft Business Analytics Dashboard

**e-Infosoft** is a comprehensive business analytics dashboard designed to empower electronics showrooms and similar businesses with deep insights from their sales data. This tool supports CSV file upload, generates insightful visualizations (bar, line, and pie charts), predicts future trends, performs customer segmentation, and optimizes inventory levels.

---

## 🚀 Features

* **Secure Login & Registration System**
* **CSV Upload and Persistent Session Memory**
* **Interactive Dashboards**

  * Bar Chart: Revenue/Profit by Product
  * Line Chart: Time-based Revenue Trends
  * Pie Chart: Revenue Share by Category
* **Forecasting with Linear Regression**
* **Customer Segmentation using KMeans Clustering**
* **Inventory Optimization Suggestions**
* **PDF Report Generation**
* **Background Video Support**

---

## 🔧 Technologies Used

* **Frontend:** HTML, CSS, JavaScript (with Chart.js)
* **Backend:** Python (Flask)
* **Data Science:** Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn
* **Deployment:** Railway, Render

---

## 📂 Folder Structure

```
e-infosoft/
├── app.py                  # Main Flask backend
├── templates/              # HTML templates (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── upload.html
│   ├── dashboard.html
│   ├── forecast.html
│   └── segment.html
├── static/                 # CSS, JS, video
│   └── background.mp4
├── data/                   # Uploaded CSV files
├── reports/                # Generated PDF reports
├── users.json              # User credentials (hashed)
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python version
├── Procfile                # For Railway deployment
├── render.yaml             # For Render deployment
└── README.md               # This file
```

---

## 📊 Sample CSV Columns

Your CSV file should include the following columns:

```
Date, Product, Category, Units Sold, Revenue, Cost, Customer Name, Customer Email, Location, Customer Type, Stock Level
```

---

## 🔄 How Forecasting Works

Forecasting is done using **Linear Regression** to predict revenue trends based on date. It maps each date to a numerical index and predicts future values using the fitted regression line.

---

## � Customer Segmentation

Uses **KMeans clustering** on normalized Revenue, Units Sold, and Stock Level to identify different customer segments.

---

## 📥 Installation

```bash
git clone https://github.com/your-username/e-infosoft.git
cd e-infosoft
pip install -r requirements.txt
python app.py
```

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
