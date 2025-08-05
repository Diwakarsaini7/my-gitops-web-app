from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)


db_config = {
    'host': os.getenv('DB_HOST', 'mysql-service'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'itemsdb')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def init_db():
    """Initialize database and create table if not exists"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()

@app.route('/')
def index():
    """Display all items"""
    connection = get_db_connection()
    items = []
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM items ORDER BY created_at DESC")
        items = cursor.fetchall()
        cursor.close()
        connection.close()
    
    return render_template('index.html', items=items)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    """Add new item to database"""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO items (name, description) VALUES (%s, %s)",
                (name, description)
            )
            connection.commit()
            cursor.close()
            connection.close()
            
        return redirect(url_for('index'))
    
    return render_template('add_item.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'version': '1.0.0'}

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
