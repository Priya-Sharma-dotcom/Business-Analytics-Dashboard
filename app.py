from flask import Flask, render_template, request, redirect, url_for, session
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from fpdf import FPDF
from sklearn.cluster import KMeans
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory user store for simplicity
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users[email] = password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if users.get(email) == password:
            session['username'] = email
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['csv_file']
        if file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            session['csv_file'] = filepath
            return render_template('dashboard.html', uploaded=True)
    return render_template('dashboard.html')


@app.route('/forecast')
def forecast():
    if 'csv_file' not in session:
        return redirect(url_for('dashboard'))

    df = pd.read_csv(session['csv_file'])

    if 'Date' in df.columns and 'Revenue' in df.columns:
        # Step 1: Convert Date to datetime
        df['Date'] = pd.to_datetime(df['Date'])

        # Step 2: Group by Date and sum Revenue
        daily_revenue = df.groupby('Date')['Revenue'].sum().reset_index()

        # Step 3: Forecast using moving average
        daily_revenue['Forecast'] = daily_revenue['Revenue'].rolling(window=3, min_periods=1).mean()

        # Step 4: Plot
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=daily_revenue, x='Date', y='Revenue', label='Actual Revenue')
        sns.lineplot(data=daily_revenue, x='Date', y='Forecast', label='Forecast (3-day MA)')
        plt.title('Revenue Forecast')
        plt.xlabel('Date')
        plt.ylabel('Revenue')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Step 5: Convert to base64 image
        img = io.BytesIO()
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        forecast_plot = base64.b64encode(img.read()).decode('utf8')

        return render_template('forecast.html', forecast_plot=forecast_plot)
    else:
        return 'Required columns "Date" and "Revenue" not found in CSV'

@app.route('/segment')
def segment():
    if 'csv_file' not in session:
        return redirect(url_for('dashboard'))

    df = pd.read_csv(session['csv_file'])

    if 'Customer Email' in df.columns and 'Revenue' in df.columns:
        # Step 1: Group revenue per customer
        customer_data = df.groupby('Customer Email')['Revenue'].sum().reset_index()
        customer_data.rename(columns={'Customer Email': 'CustomerEmail', 'Revenue': 'TotalRevenue'}, inplace=True)

        # Step 2: KMeans clustering
        kmeans = KMeans(n_clusters=3, random_state=0)
        customer_data['Segment'] = kmeans.fit_predict(customer_data[['TotalRevenue']])

        # Step 3: Convert to dictionary for HTML rendering
        data_dict = customer_data.to_dict(orient='records')

        return render_template('segment.html', customer_data=data_dict)
    else:
        return 'Required columns "Customer Email" and "Revenue" not found in CSV'



if __name__ == '__main__':
    app.run(debug=True)
