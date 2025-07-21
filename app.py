from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = 'secret'

UPLOAD_FOLDER = 'data'
STATIC_FOLDER = 'static'
REPORT_FOLDER = 'reports'
USER_FILE = 'users.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# Load users from file
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save users to file
def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

users = load_users()

data_frame = None
chart_files = []

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    if data_frame is None:
        return redirect(url_for('upload'))
    total_revenue = data_frame['Revenue'].sum()
    total_profit = data_frame['Profit'].sum()
    total_units = data_frame['Units_Sold'].sum()
    products = sorted(data_frame['Product'].unique())
    summary = data_frame.to_dict(orient='records')
    return render_template('index.html', revenue=total_revenue, profit=total_profit,
                           units=total_units, products=products, chart_path=chart_files,
                           summary_table=summary)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email] == password:
            session['user'] = email
            return redirect(url_for('home'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users:
            return 'User already exists'
        users[email] = password
        save_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global data_frame, chart_files
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            data_frame = pd.read_csv(filepath)
            chart_files.clear()
            return redirect(url_for('home'))
    return render_template('upload.html')

@app.route('/chart', methods=['POST'])
def chart():
    global chart_files
    chart_type = request.form['chart_type']
    metric = request.form.get('metric', 'Revenue')
    product_filter = request.form['product']

    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    data_frame['Month'] = pd.Categorical(data_frame['Month'], categories=month_order, ordered=True)
    data_frame.sort_values('Month', inplace=True)

    df = data_frame if product_filter == 'All' or chart_type == 'pie' else data_frame[data_frame['Product'] == product_filter]

    chart_name = f"{chart_type}_{metric}_{product_filter}.png".replace(" ", "_")
    chart_path = os.path.join(STATIC_FOLDER, chart_name)

    plt.figure()
    if chart_type in ['bar', 'line']:
        df.groupby('Month')[metric].sum().plot(kind=chart_type)
    elif chart_type == 'pie':
        df.groupby('Product')[metric].sum().plot(kind='pie', autopct='%1.1f%%')
        plt.ylabel('')

    plt.title(f'{chart_type.capitalize()} Chart - {metric} - {product_filter}')
    plt.ylabel(metric)
    plt.tight_layout()
    plt.savefig(chart_path)
    chart_files.append(os.path.basename(chart_path))

    return redirect(url_for('home'))

@app.route('/download')
def download():
    report_path = os.path.join(REPORT_FOLDER, 'business_report.pdf')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="e-Infosoft Business Report", ln=True, align='C')
    pdf.ln(10)

    if data_frame is not None:
        for chart in chart_files:
            chart_path = os.path.join(STATIC_FOLDER, chart)
            if os.path.exists(chart_path):
                pdf.image(chart_path, w=180)
                pdf.ln(10)

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Summary Table:", ln=True)
        pdf.ln(5)
        for index, row in data_frame.iterrows():
            line = f"{row['Month']} - {row['Product']}: Units={row['Units_Sold']}, Revenue={row['Revenue']}, Profit={row['Profit']}"
            pdf.multi_cell(0, 10, txt=line)

    pdf.output(report_path)
    return send_file(report_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
