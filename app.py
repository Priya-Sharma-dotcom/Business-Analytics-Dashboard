from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from fpdf import FPDF
from io import BytesIO
import base64
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(minutes=30)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_users():
    return {"admin@example.com": "admin123"}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        flash('Registration currently disabled in this demo.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        if email in users and users[email] == password:
            session.permanent = True
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['csvfile']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            session['csv_path'] = filepath
            return redirect(url_for('analysis'))
    return render_template('upload.html')

@app.route('/analysis')
def analysis():
    if 'user' not in session or 'csv_path' not in session:
        return redirect(url_for('login'))

    df = pd.read_csv(session['csv_path'])

    charts = []

    product_types = ['Fridge', 'TV', 'AC', 'Laptop']
    metrics = ['Revenue', 'Profit', 'Units Sold']

    for metric in metrics:
        for product in product_types:
            product_df = df[df['Product'] == product]
            if product_df.empty or metric not in product_df.columns:
                continue

            # Bar chart
            plt.figure(figsize=(6,4))
            sns.barplot(x=product_df['Month'], y=product_df[metric])
            plt.title(f'{metric} for {product} (Bar)')
            plt.tight_layout()
            bar_io = BytesIO()
            plt.savefig(bar_io, format='png')
            bar_io.seek(0)
            bar_base64 = base64.b64encode(bar_io.read()).decode('utf-8')
            charts.append(('Bar', product, metric, bar_base64))
            plt.close()

            # Line chart
            plt.figure(figsize=(6,4))
            sns.lineplot(x=product_df['Month'], y=product_df[metric])
            plt.title(f'{metric} for {product} (Line)')
            plt.tight_layout()
            line_io = BytesIO()
            plt.savefig(line_io, format='png')
            line_io.seek(0)
            line_base64 = base64.b64encode(line_io.read()).decode('utf-8')
            charts.append(('Line', product, metric, line_base64))
            plt.close()

            # Pie chart (total value)
            plt.figure(figsize=(4,4))
            total = product_df.groupby('Product')[metric].sum()
            plt.pie(total, labels=total.index, autopct='%1.1f%%')
            plt.title(f'{metric} Distribution for {product} (Pie)')
            pie_io = BytesIO()
            plt.savefig(pie_io, format='png')
            pie_io.seek(0)
            pie_base64 = base64.b64encode(pie_io.read()).decode('utf-8')
            charts.append(('Pie', product, metric, pie_base64))
            plt.close()

    return render_template('analysis.html', charts=charts)

@app.route('/forecast')
def forecast():
    if 'user' not in session or 'csv_path' not in session:
        return redirect(url_for('login'))

    df = pd.read_csv(session['csv_path'])

    forecast_data = {}
    for product in df['Product'].unique():
        prod_df = df[df['Product'] == product]
        if len(prod_df) < 2:
            continue
        prod_df = prod_df.sort_values('Month')
        prod_df['Revenue_forecast'] = prod_df['Revenue'].rolling(2).mean().fillna(method='bfill')
        forecast_data[product] = prod_df[['Month', 'Revenue', 'Revenue_forecast']]

    return render_template('forecast.html', forecast_data=forecast_data)

@app.route('/segment')
def segment():
    if 'user' not in session or 'csv_path' not in session:
        return redirect(url_for('login'))

    df = pd.read_csv(session['csv_path'])

    try:
        features = df[['Units Sold', 'Revenue', 'Profit']]
        model = KMeans(n_clusters=3)
        df['Segment'] = model.fit_predict(features)
    except:
        df['Segment'] = 'N/A'

    return render_template('segment.html', table=df.to_html(classes='table table-striped'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
