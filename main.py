from flask import Flask, request, redirect, jsonify, render_template
import mysql.connector
import hashlib
import base64
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load variables from .env
load_dotenv()

# Database Configuration
DB_CONGIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONGIG)


#Function to generate  a Short URL
def generate_short_url(long_url):
    hash_object = hashlib.sha256(long_url.encode())
    short_hash = base64.urlsafe_b64encode(hash_object.digest())[:6].decode()
    print(hash_object.digest())
    return short_hash

# Serve the HTML form
@app.route('/')
def home():
    return render_template('index.html')

# Handle URL Shortening
@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.form.get('long_url')
    if not long_url:
        return "Invalid URL", 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if URL Exists
    cursor.execute("SELECT short_url FROM shortner WHERE long_url = %s", (long_url,))
    existing_entry = cursor.fetchone()
    if existing_entry:
        conn.close()
        return render_template('shorten.html', 
    link=f'{request.host_url}{existing_entry["short_url"]}', 
    text=f'https://url/{existing_entry["short_url"]}'
)

    
    short_url = generate_short_url(long_url)
    cursor.execute("INSERT INTO shortner (long_url, short_url) VALUES (%s, %s)", (long_url, short_url))
    conn.commit()
    conn.close()

    return render_template('shorten.html', text=f'{request.host_url}{short_url}') 

# Redirect shortened URLs
@app.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if URL Exists
    cursor.execute("SELECT long_url FROM shortner WHERE short_url = %s", (short_url,))
    entry = cursor.fetchone()
    if entry:
        cursor.execute("UPDATE shortner SET clicks = clicks + 1 WHERE short_url = %s", (short_url,))
        conn.commit()
        conn.close()
        return redirect(entry['long_url'])
    conn.close()
    return "Error: URL not found", 404

# Run the Flask Application
if __name__ == '__main__':
    app.run(debug=True)