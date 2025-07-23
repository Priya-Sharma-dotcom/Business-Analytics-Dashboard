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
app.secret_key = 'e-infosoft-secret-key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dummy user database
users = {'admin@example.com': 'admin123'}

data_cache = {}

@app.route('/')
def index():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email] == password:
            session['email'] = email
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid email or password.")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users[email] = password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = pd.read_csv(filepath)
            session['uploaded_file'] = filepath
            data_cache[session['email']] = df
            return redirect(url_for('dashboard'))
    return render_template('upload.html')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session or 'uploaded_file' not in session:
        return redirect(url_for('login'))

    df = data_cache.get(session['email'])
    if df is None:
        return redirect(url_for('upload'))

    summary = df[['Revenue', 'Profit', 'Units Sold']].sum().to_dict()
    product_summary = df.groupby('Product')[['Revenue', 'Profit', 'Units Sold']].sum()

    # Plot
    plt.figure(figsize=(10, 6))
    product_summary[['Revenue', 'Profit']].plot(kind='bar')
    plt.title('Revenue and Profit by Product')
    plt.tight_layout()
    bar_chart = save_plot_to_base64()

    plt.figure(figsize=(6, 6))
    product_summary['Units Sold'].plot(kind='pie', autopct='%1.1f%%')
    plt.title('Units Sold by Product')
    plt.ylabel('')
    pie_chart = save_plot_to_base64()

    return render_template('dashboard.html', summary=summary, bar_chart=bar_chart, pie_chart=pie_chart)

@app.route('/forecast')
def forecast():
    if 'email' not in session or 'uploaded_file' not in session:
        return redirect(url_for('login'))

    df = data_cache.get(session['email'])
    if df is None or 'Date' not in df.columns:
        return redirect(url_for('upload'))

    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    df.set_index('Date', inplace=True)
    monthly_revenue = df['Revenue'].resample('M').sum()

    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    model = ExponentialSmoothing(monthly_revenue, trend='add', seasonal='add', seasonal_periods=12)
    fit = model.fit()
    forecasted = fit.forecast(6)

    plt.figure(figsize=(10, 6))
    monthly_revenue.plot(label='Actual')
    forecasted.plot(label='Forecast')
    plt.legend()
    plt.title('Revenue Forecast')
    plt.tight_layout()
    line_chart = save_plot_to_base64()

    return render_template('forecast.html', line_chart=line_chart)

@app.route('/segment')
def segment():
    if 'email' not in session or 'uploaded_file' not in session:
        return redirect(url_for('login'))

    df = data_cache.get(session['email'])
    if df is None:
        return redirect(url_for('upload'))

    customer_data = df.groupby('Customer')[['Revenue', 'Units Sold']].sum().dropna()
    kmeans = KMeans(n_clusters=3, random_state=0)
    customer_data['Cluster'] = kmeans.fit_predict(customer_data)

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='Revenue', y='Units Sold', hue='Cluster', data=customer_data, palette='Set1')
    plt.title('Customer Segments')
    plt.tight_layout()
    segment_chart = save_plot_to_base64()

    return render_template('segment.html', segment_chart=segment_chart)

def save_plot_to_base64():
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64

if __name__ == '__main__':
    app.run(debug=True)
