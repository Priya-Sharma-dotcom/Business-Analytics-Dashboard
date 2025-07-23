from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from sklearn.cluster import KMeans
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to something secure
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size

# ---------------- Utility Functions ----------------

def generate_plot(df, x, y, title, xlabel, ylabel):
    plt.figure(figsize=(10, 5))
    plt.plot(df[x], df[y], marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return image_base64

def calculate_kpis(df):
    total_revenue = df['Revenue'].sum()
    total_profit = df['Profit'].sum()
    average_monthly_sales = df.groupby('Month')['Revenue'].sum().mean()
    top_product = df.groupby('Product')['Revenue'].sum().idxmax()
    return total_revenue, total_profit, average_monthly_sales, top_product

def segment_customers(df):
    data = df.groupby('Customer')['Revenue'].sum().reset_index()
    kmeans = KMeans(n_clusters=3, random_state=0).fit(data[['Revenue']])
    data['Segment'] = kmeans.labels_
    return data

def inventory_optimization(df):
    inventory = df.groupby('Product')['Quantity Sold'].sum().reset_index()
    inventory['Status'] = pd.cut(inventory['Quantity Sold'],
                                  bins=[-1, 20, 100, float('inf')],
                                  labels=['Slow-moving', 'Optimal', 'Fast-moving'])
    return inventory

# ---------------- Routes ----------------

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Simple hardcoded check – replace with real authentication later
        if email == 'admin@einfi.com' and password == '1234':
            session['user'] = email
            return redirect('/dashboard')
        else:
            error = "Invalid email or password"
    return render_template('login.html', error=error)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/')

    chart = None
    kpi = {}
    segment_data = None
    inventory_data = None
    error = None

    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                df = pd.read_csv(file)

                # Validate columns
                required_columns = {'Date', 'Product', 'Customer', 'Quantity Sold', 'Price'}
                if not required_columns.issubset(df.columns):
                    error = "CSV is missing one or more required columns."
                    return render_template('index.html', chart=chart, kpi=kpi, segment_data=segment_data,
                                           inventory_data=inventory_data, error=error)

                df['Month'] = pd.to_datetime(df['Date']).dt.strftime('%B')
                df['Revenue'] = df['Quantity Sold'] * df['Price']
                df['Profit'] = df['Revenue'] * 0.2

                chart = generate_plot(df.groupby('Month')['Revenue'].sum().reset_index(),
                                      'Month', 'Revenue',
                                      'Monthly Revenue', 'Month', 'Revenue')

                total_revenue, total_profit, avg_monthly_sales, top_product = calculate_kpis(df)
                kpi = {
                    'Total Revenue': total_revenue,
                    'Total Profit': total_profit,
                    'Avg Monthly Sales': avg_monthly_sales,
                    'Top Product': top_product
                }

                segment_data = segment_customers(df)
                inventory_data = inventory_optimization(df)

            except Exception as e:
                error = f"Error processing file: {str(e)}"

    return render_template('index.html', chart=chart, kpi=kpi, segment_data=segment_data,
                           inventory_data=inventory_data, error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ---------------- Run ----------------

if __name__ == '__main__':
    app.run(debug=True)
