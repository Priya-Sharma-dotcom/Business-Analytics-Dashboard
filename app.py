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
dummy_users = {'admin@example.com': 'admin123'}

# Store registered users
users = dummy_users.copy()

def generate_charts(df, chart_type, metric):
    chart_images = []
    products = df['Product'].unique()
    for product in products:
        subset = df[df['Product'] == product]
        if subset.empty:
            continue

        plt.figure(figsize=(6, 4))
        if chart_type == 'bar':
            plt.bar(subset['Month'], subset[metric])
        elif chart_type == 'line':
            plt.plot(subset['Month'], subset[metric], marker='o')
        elif chart_type == 'pie':
            subset_pie = subset.groupby('Month')[metric].sum()
            plt.pie(subset_pie, labels=subset_pie.index, autopct='%1.1f%%')
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
        email = request.form['email']
        password = request.form['password']
        if email in users:
            return 'Email already registered. <a href="/login">Login</a>'
        users[email] = password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email] == password:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials. <a href="/login">Try again</a>'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    charts = None
    if request.method == 'POST':
        file = request.files.get('csv_file')
        chart_type = request.form.get('chart_type')
        metric = request.form.get('metric')
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = pd.read_csv(filepath)
            session['last_csv'] = filepath
            charts = generate_charts(df, chart_type, metric)

    return render_template('dashboard.html', charts=charts)

@app.route('/forecast')
def forecast():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('forecast.html')

@app.route('/segment')
def segment():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('segment.html')

if __name__ == '__main__':
    app.run(debug=True)
