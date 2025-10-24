from flask import Flask, render_template, request, redirect, url_for, session, flash
import os                                           //filesystem paths
import pandas as pd                                 //CSV reading
import matplotlib.pyplot as plt      
import seaborn as sns                              //plotting
import numpy as np                                 //numerical library
from fpdf import FPDF                              //generating pdf
from sklearn.cluster import KMeans                  
from datetime import datetime
import io                                         //in-memory binary streams (used when creating images)
import base64                                     //coverts image to text strings for embedding in HTML
import time


app = Flask(__name__)                             //Flask App starts
app.secret_key = 'supersecretkey'                 //required to sign the session cookies and flash messages. Note: Hardcoding 'supersecretkey' is insecure for production.

UPLOAD_FOLDER = 'static'                             //Defines where uploaded files get saved.
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER          //In Flask, app.config is like a dictionary (key-value store) that holds configuration settings for your app.

# In-memory user store for simplicity
users = {}                                          //A Python dictionary storing email: password. This is only suitable for demos. Passwords are stored in plaintext — insecure.Instead store hashes

@app.route('/')                                      //When a visitor hits /, Flask renders index.html. (By convention Template files must be in a templates/ folder.)
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])       //GET: show registration page.POST: read email and password from form, store them in users, then redirect to login.
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users[email] = password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])          //POST: checks if password matches the stored one and sets session['username'] to mark user logged in.  GET: shows login form.
def login():
    if request.method == 'POST':
        email = request.form['email']                  //read email and password from form
        password = request.form['password']
        if users.get(email) == password:
            session['username'] = email
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')                                                //Removes username from session, logs user out, and redirects to home.
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])                               
def dashboard():
    if 'username' not in session:                                        //If user not logged in → redirect to login.
        return redirect(url_for('login'))

    charts = []                                                        //is used to collect chart info to pass to template.

    if request.method == 'POST':                                                  //If form POST includes a file named csv_file, it:Checks filename ends with .csv.Builds filename by prefixing a timestamp to avoid collisions.Saves file to static/ folder and stores session['csv_file'] = filepath.flash a success or error message.
        # Handle CSV Upload
        if 'csv_file' in request.files:
            file = request.files['csv_file']                                      //Get uploaded files
            if file and file.filename.endswith('.csv'):
                filename = f"{int(time.time())}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)           //os.path.join(...) → safely joins folder + filename into a full path, like:uploads/picture.png
                file.save(filepath)
                session['csv_file'] = filepath
                flash('✅ CSV uploaded successfully.', 'success')
            else:
                flash('❌ Please upload a valid .csv file.', 'error')                      //Redirect back to dashboard after upload (so page refresh doesn’t re-post).
            return redirect(url_for('dashboard'))

        # Handle Chart Generation
        if 'chart_type' in request.form and 'metric' in request.form:
            if 'csv_file' not in session:
                flash("❌ Please upload a CSV file first.", 'error')
                return redirect(url_for('dashboard'))

            filepath = session['csv_file']
            try:
                df = pd.read_csv(filepath)                                             //Reads CSV into a pandas DataFrame df.

                if 'Profit' not in df.columns and 'Revenue' in df.columns and 'Cost' in df.columns:
                    df['Profit'] = df['Revenue'] - df['Cost']

                chart_type = request.form['chart_type']
                metric = request.form['metric']


                
//Requires Product column and the chosen metric column in CSV.
//Groups data by Product and sums the metric (so each product has a single number).
//Creates a matplotlib figure:bar, line, or pie depending on chart_type.

                if 'Product' in df.columns and metric in df.columns:
                    grouped = df.groupby('Product')[metric].sum().reset_index()

                    fig, ax = plt.subplots()
                    if chart_type == 'bar':
                        ax.bar(grouped['Product'], grouped[metric])
                        ax.set_title(f'{metric} by Product')
                    elif chart_type == 'line':
                        ax.plot(grouped['Product'], grouped[metric], marker='o')
                        ax.set_title(f'{metric} by Product')
                    elif chart_type == 'pie':
                        ax.pie(grouped[metric], labels=grouped['Product'], autopct='%1.1f%%')
                        ax.set_title(f'{metric} Distribution')

                    ax.set_xlabel('Product') if chart_type != 'pie' else None
                    ax.set_ylabel(metric) if chart_type != 'pie' else None
                    plt.xticks(rotation=45)
                    plt.tight_layout()

                    buf = io.BytesIO()                                  //Converts the figure to PNG in-memory using io.BytesIO, base64-encodes it so it can be embedded into HTML as a data:image/png;base64,... string.
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    chart_url = base64.b64encode(buf.read()).decode('utf-8')
                    plt.close(fig)

                    charts.append((chart_type, 'All Products', metric, chart_url))      //Closes the figure and appends (chart_type, 'All Products', metric, chart_url) to charts list which the template will display.
                else:
                    flash("❌ Required columns missing in CSV.", 'error')
            except Exception as e:
                flash(f"❌ Error processing CSV: {str(e)}", 'error')

    return render_template('dashboard.html', charts=charts)

@app.route('/reset_csv', methods=['POST'])
def reset_csv():
    session.pop('csv_file', None)
    flash("🗂️ CSV reset. Please upload a new file.", 'info')       //Removes the saved CSV from the session (so user can upload a new one)
    return redirect(url_for('dashboard'))



@app.route('/forecast')
def forecast():
    if 'csv_file' not in session:                                  //Ensures a CSV is uploaded.
        return redirect(url_for('dashboard'))

    df = pd.read_csv(session['csv_file'])

    if 'Date' in df.columns and 'Revenue' in df.columns:                   //Reads CSV and checks for Date and Revenue.
        # Step 1: Convert Date to datetime
        df['Date'] = pd.to_datetime(df['Date'])

        # Step 2: Group by Date and sum Revenue
        daily_revenue = df.groupby('Date')['Revenue'].sum().reset_index()     //Aggregates revenue per date (groupby('Date').sum()).

        # Step 3: Forecast using moving average
//daily_revenue['Revenue'] → selects the column of daily revenue.
//.rolling(window=3, min_periods=1) → creates a moving window of 3 rows.
//For each day, it looks at the current day and the previous 2 days.
//.mean() → calculates the average for that window.
//daily_revenue['Forecast'] = ... → stores it in a new column called Forecast.

        daily_revenue['Forecast'] = daily_revenue['Revenue'].rolling(window=3, min_periods=1).mean()

        # Step 4: Plots actual vs forecast using seaborn line plots, saves to base64 and renders forecast.html with the image.
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=daily_revenue, x='Date', y='Revenue', label='Actual Revenue')
        sns.lineplot(data=daily_revenue, x='Date', y='Forecast', label='Forecast (3-day MA)')
        plt.title('Revenue Forecast')
        plt.xlabel('Date')
        plt.ylabel('Revenue')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Step 5: Convert to base64 image
        img = io.BytesIO()
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        forecast_plot = base64.b64encode(img.read()).decode('utf8')

        return render_template('forecast.html', forecast_plot=forecast_plot)
    else:
        return 'Required columns "Date" and "Revenue" not found in CSV'

@app.route('/segment')
def segment():
    if 'csv_file' not in session:
        return redirect(url_for('dashboard'))

    df = pd.read_csv(session['csv_file'])             //df now contains all rows and columns from the uploaded file.

    if 'Customer Email' in df.columns and 'Revenue' in df.columns:
        # Step 1: Group revenue per customer
        customer_data = df.groupby('Customer Email')['Revenue'].sum().reset_index()                                   //Aggregates total revenue per customer.combine all rows for the same customer.
        customer_data.rename(columns={'Customer Email': 'CustomerEmail', 'Revenue': 'TotalRevenue'}, inplace=True)

        # Step 2: KMeans clustering
        //KMeans is a machine learning algorithm that groups data into clusters.
//Here,it groups customers into 3 segments based on TotalRevenue.
//Each customer is assigned a Segment number (0, 1, or 2) depending on their spending.  
            
        kmeans = KMeans(n_clusters=3, random_state=0)
        customer_data['Segment'] = kmeans.fit_predict(customer_data[['TotalRevenue']])

        # Step 3: Convert to dictionary for HTML rendering
        data_dict = customer_data.to_dict(orient='records')

        return render_template('segment.html', customer_data=data_dict)
    else:
        return 'Required columns "Customer Email" and "Revenue" not found in CSV'



if __name__ == '__main__':         //Only run the Flask server if this script is executed directly.Start the server in debug mode so you can see errors and auto-reload changes.You can now open a browser at http://127.0.0.1:5000/ to see your web app.
    app.run(debug=True)          //Runs Flask dev server in debug mode (auto reload and detailed errors).
                                //Important: debug=True should be turned off in production since it can expose code and give remote users an interactive debugger.
