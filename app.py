from flask import Flask, render_template, request, redirect, url_for, session
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from fpdf import FPDF
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dummy credentials
users = {'admin': 'admin123'}

def generate_charts(df, chart_type, metric):
    chart_images = []
    products = ['TV', 'Fridge', 'AC', 'Laptop']
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
            subset = subset.groupby('Month')[metric].sum()
            plt.pie(subset, labels=subset.index, autopct='%1.1f%%')
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return 'Username already exists.'
        users[username] = password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
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
            session['last_csv'] = filepath
            charts = generate_charts(df, chart_type, metric)

    return render_template('dashboard.html', charts=charts)

@app.route('/forecast')
def forecast():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('forecast.html')

@app.route('/segment')
def segment():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('segment.html')

if __name__ == '__main__':
    app.run(debug=True)
