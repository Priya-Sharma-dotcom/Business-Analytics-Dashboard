# 📊 Business Analytics Dashboard - e-Infosoft

A secure, user-friendly business analytics dashboard designed for **e-Infosoft**, an electronics showroom. This Flask-based web application allows users to:

✅ Register and log in
📁 Upload business CSV files
📈 Generate dynamic charts (Line, Bar, Pie)
📄 Download a PDF business report with visual charts and table summaries
🌙 Toggle between dark and light modes

---

## 🔧 Features

* **User Authentication**: Registration & Login
* **CSV Upload**: Upload your sales or inventory data securely
* **Chart Generation**: Select metric & chart type dynamically
* **Summary Table**: Auto-generated table from your uploaded CSV
* **PDF Export**: Create a downloadable business report with charts & summary
* **Dark Mode**: Toggle theme for better visibility
* **Responsive Design**: Clean layout styled using HTML/CSS

---

## 📁 Project Structure

```
BusinessAnalyticsSite/
├── app.py
├── data/                  # Uploaded CSV files (optional to keep empty)
├── reports/               # Auto-generated business reports (PDF)
├── static/                # Stores generated chart images
├── templates/             # HTML files (login, register, dashboard, etc.)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── upload.html
├── users.json             # Stores registered users' data
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/Priya-Sharma-dotcom/Business-Analytics-Dashboard.git
cd Business-Analytics-Dashboard
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## 📊 Sample CSV Format

| Month   | Product | Units\_Sold | Revenue | Profit |
| ------- | ------- | ----------- | ------- | ------ |
| January | Fridge  | 20          | 100000  | 15000  |
| January | TV      | 10          | 70000   | 12000  |

---

## 💡 Future Enhancements

* Email-based password reset
* Chart downloads individually
* Admin dashboard
* Support for Excel (.xlsx) uploads

---

## 🧠 Built With

* Python 3
* Flask
* Pandas
* Matplotlib
* FPDF
* HTML/CSS

---

## 🏢 About e-Infosoft

This project was built as part of the **e-Infosoft** initiative to analyze sales data for electronics showrooms.
🔗 Powered by: `e-Infosoft`

---

## 📬 Contact

👤 Priya Sharma
📧 [priya.sharma01312@gmail.com](mailto:priya.sharma01312@gmail.com)
🔗 [LinkedIn](https://www.linkedin.com/in/priya-sharma-blockchain/)
🌐 [GitHub](https://github.com/Priya-Sharma-dotcom)
