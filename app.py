from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pickle
import numpy as np
import os
import zipfile

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# === Step 1: Extract model.zip if model.sav not found ===
if not os.path.exists('model.sav'):
    if os.path.exists('model.zip'):
        with zipfile.ZipFile('model.zip', 'r') as zip_ref:
            zip_ref.extractall()
    else:
        raise FileNotFoundError("model.zip not found!")

# === Step 2: Load model ===
model = pickle.load(open('model.sav', 'rb'))

# === Home route ===
@app.route('/')
def home():
    return render_template('home.html')

# === Signup route ===
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('signup.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

# === Login route ===
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
    return render_template('signin.html')

# === Predict route ===
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
            return render_template('prediction.html', prediction=result)
        except Exception as e:
            return f"Error occurred: {str(e)}"

    return render_template('prediction.html')

# === Logout route ===
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# === Main runner ===
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Dynamic port for Render
    app.run(host='0.0.0.0', port=port)
