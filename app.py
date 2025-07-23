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
        file = request.files['file']
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

    # Simple forecast (average revenue projection)
    if 'Revenue' in df.columns:
        forecast = df['Revenue'].mean() * 1.1
        return render_template('forecast.html', forecast=forecast)
    else:
        return 'Revenue column not found in CSV'

@app.route('/segment')
def segment():
    if 'csv_file' not in session:
        return redirect(url_for('dashboard'))

    df = pd.read_csv(session['csv_file'])

    if 'CustomerID' in df.columns and 'Amount' in df.columns:
        kmeans = KMeans(n_clusters=3, random_state=0).fit(df[['Amount']])
        df['Segment'] = kmeans.labels_
        segment_counts = df['Segment'].value_counts().to_dict()
        return render_template('segment.html', segments=segment_counts)
    else:
        return 'Required columns not found in CSV'

if __name__ == '__main__':
    app.run(debug=True)
