from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pickle
import numpy as np
import os
import zipfile

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Unzip model.zip if model.sav is not already extracted
if not os.path.exists('model.sav'):
    if os.path.exists('model.zip'):
        with zipfile.ZipFile('model.zip', 'r') as zip_ref:
            zip_ref.extractall()

# Load the trained model
model = pickle.load(open('model.sav', 'rb'))

# Route: Home page
@app.route('/')
def home():
    return render_template('home.html')

# Route: Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('signup.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

# Route: Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('signup.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            return redirect(url_for('predict'))
        else:
            return "Invalid credentials. Please try again."
    return render_template('login.html')

# Route: Prediction page
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            features = [float(x) for x in request.form.values()]
            features = np.array(features).reshape(1, -1)
            prediction = model.predict(features)
            result = 'Heart Disease Detected' if prediction[0] == 1 else 'No Heart Disease'
            return render_template('result.html', prediction=result)
        except Exception as e:
            return f"Error occurred: {str(e)}"
    
    return render_template('predict.html')

# Route: Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Run the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
