from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import pandas as pd
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

users = {}  # In-memory user store (can upgrade to CSV or DB)

# === Routes ===

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email] == password:
            session['user'] = email
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users:
            flash('Email already registered')
        else:
            users[email] = password
            flash('Registered successfully, please login')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            session['csv_file'] = filepath
            return redirect(url_for('analysis'))
    return render_template('upload.html')

@app.route('/analysis')
def analysis():
    if 'csv_file' not in session:
        return redirect(url_for('upload_file'))

    df = pd.read_csv(session['csv_file'])

    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_quantity = df['Quantity'].sum()

    fig, ax = plt.subplots()
    df.groupby('Category')['Sales'].sum().plot(kind='bar', ax=ax)
    ax.set_title('Sales by Category')
    ax.set_ylabel('Sales')
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return render_template('analysis.html',
                           total_sales=total_sales,
                           total_profit=total_profit,
                           total_quantity=total_quantity,
                           chart=chart_base64)

@app.route('/generate_pdf')
def generate_pdf():
    if 'csv_file' not in session:
        return redirect(url_for('upload_file'))

    df = pd.read_csv(session['csv_file'])

    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_quantity = df['Quantity'].sum()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Business Report Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Total Sales: {total_sales:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total Profit: {total_profit:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total Quantity Sold: {total_quantity}", ln=True)

    # Save and serve the file
    report_path = os.path.join('static', 'report.pdf')
    pdf.output(report_path)

    return redirect('/static/report.pdf')


# === Utility ===

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === Main ===

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
