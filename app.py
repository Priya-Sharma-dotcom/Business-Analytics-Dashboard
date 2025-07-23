from flask import Flask, render_template, request, redirect, url_for, session
import os
import pandas as pd
import matplotlib.pyplot as plt
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Save directly in static folder
UPLOAD_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}

# Dummy user database
users = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route: Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users[email] = password
        return redirect(url_for('login'))
    return render_template('register.html')

# Route: Login
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

# Route: Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# Route: Dashboard & Upload
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    charts = None
    if request.method == 'POST':
        file = request.files['csv_file']
        chart_type = request.form.get('chart_type')
        metric = request.form.get('metric')

        if file and allowed_file(file.filename):
            filename = str(uuid.uuid4()) + ".csv"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            df = pd.read_csv(filepath)
            charts = generate_charts(df, chart_type, metric)
        else:
            return "Please upload a valid CSV file."

    return render_template('dashboard.html', charts=charts)

# Generate charts and return filenames
def generate_charts(df, chart_type, metric):
    if metric not in df.columns:
        return []

    chart_filename = f"chart_{uuid.uuid4()}.png"
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], chart_filename)

    plt.figure()
    if chart_type == 'bar':
        df[metric].value_counts().plot(kind='bar')
    elif chart_type == 'line':
        df[metric].plot(kind='line')
    elif chart_type == 'pie':
        df[metric].value_counts().plot(kind='pie', autopct='%1.1f%%')
    else:
        return []

    plt.title(f"{chart_type.capitalize()} Chart of {metric}")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return [chart_filename]

if __name__ == '__main__':
    app.run(debug=True)
