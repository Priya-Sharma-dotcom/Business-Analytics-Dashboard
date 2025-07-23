from flask import Flask, render_template, request, redirect, url_for, session
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Simple in-memory user store
users = {'admin': 'admin123'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        if username in users:
            return 'Username already exists.'
        users[username] = password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        if users.get(username) == password:
            session['username'] = username
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

    charts = None
    if request.method == 'POST':
        file = request.files['csv_file']
        chart_type = request.form['chart_type']
        metric = request.form['metric']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = pd.read_csv(filepath)
            session['last_uploaded_csv'] = filepath
            charts = generate_charts(df, chart_type, metric)

    return render_template('dashboard.html', charts=charts)

@app.route('/forecast')
def forecast():
    if 'username' not in session:
        return redirect(url_for('login'))

    chart = None
    filepath = session.get('last_uploaded_csv')
    if filepath and os.path.exists(filepath):
        df = pd.read_csv(filepath)
        if 'Month' in df.columns and 'Revenue' in df.columns:
            df['Month'] = pd.to_datetime(df['Month'], errors='coerce')
            df = df.dropna(subset=['Month'])
            df = df.groupby(df['Month'].dt.to_period('M')).sum(numeric_only=True).reset_index()
            df['Month'] = df['Month'].dt.to_timestamp()

            x = np.arange(len(df))
            y = df['Revenue'].values
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            forecast = p(x)

            plt.figure(figsize=(6,4))
            plt.plot(df['Month'], y, label='Actual Revenue')
            plt.plot(df['Month'], forecast, linestyle='--', label='Forecast')
            plt.xlabel('Month')
            plt.ylabel('Revenue')
            plt.legend()
            plt.tight_layout()
            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            chart = base64.b64encode(img.getvalue()).decode()
            plt.close()

    return render_template('forecast.html', forecast_chart=chart)

@app.route('/segment')
def segment():
    if 'username' not in session:
        return redirect(url_for('login'))

    chart = None
    filepath = session.get('last_uploaded_csv')
    if filepath and os.path.exists(filepath):
        df = pd.read_csv(filepath)
        if 'CustomerID' in df.columns and 'SpendingScore' in df.columns:
            X = df[['SpendingScore']].dropna()
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            kmeans = KMeans(n_clusters=3, random_state=0)
            df['Segment'] = kmeans.fit_predict(X_scaled)

            plt.figure(figsize=(6,4))
            for i in range(3):
                plt.scatter(df[df['Segment']==i].index, df[df['Segment']==i]['SpendingScore'], label=f'Segment {i}')
            plt.legend()
            plt.title('Customer Segments by Spending')
            plt.xlabel('Customer Index')
            plt.ylabel('Spending Score')
            plt.tight_layout()
            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            chart = base64.b64encode(img.getvalue()).decode()
            plt.close()

    return render_template('segment.html', segment_chart=chart)

def generate_charts(df, chart_type, metric):
    chart_images = []
    products = df['Product'].unique() if 'Product' in df.columns else []
    for product in products:
        subset = df[df['Product'] == product]
        if subset.empty:
            continue

        plt.figure(figsize=(6,4))
        if chart_type == 'bar':
            plt.bar(subset['Month'], subset[metric])
        elif chart_type == 'line':
            plt.plot(subset['Month'], subset[metric], marker='o')
        elif chart_type == 'pie':
            grouped = subset.groupby('Month')[metric].sum()
            plt.pie(grouped, labels=grouped.index, autopct='%1.1f%%')
            plt.title(f'{metric} for {product}')
            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            chart_url = base64.b64encode(img.getvalue()).decode()
            chart_images.append((chart_type, product, metric, chart_url))
            plt.close()
            continue

        plt.title(f'{metric} for {product}')
        plt.xlabel('Month')
        plt.ylabel(metric)
        plt.tight_layout()
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        chart_url = base64.b64encode(img.getvalue()).decode()
        chart_images.append((chart_type, product, metric, chart_url))
        plt.close()
    return chart_images

if __name__ == '__main__':
    app.run(debug=True)
