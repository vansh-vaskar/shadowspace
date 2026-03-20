from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# create database and table if not exists
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            category TEXT,
            likes INTEGER DEFAULT 0,
            mood TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, content, category, likes, mood FROM posts ORDER BY likes DESC")
    posts = cursor.fetchall()

    # fetch comments
    comments = {}
    for post in posts:
        cursor.execute("SELECT content FROM comments WHERE post_id = ?", (post[0],))
        comments[post[0]] = cursor.fetchall()

    conn.close()

    return render_template('index.html', posts=posts, comments=comments)

@app.route('/add', methods=['POST'])
def add_post():
    content = request.form['content']
    category = request.form['category']

    content_lower = content.lower()

    if any(word in content_lower for word in ['happy', 'love', 'great', 'excited']):
        mood = 'Positive 😊'
    elif any(word in content_lower for word in ['sad', 'tired', 'depressed', 'angry']):
        mood = 'Negative 😔'
    else:
        mood = 'Neutral 😐'

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (content, category, likes, mood) VALUES (?, ?, ?, ?)",
        (content, category, 0, mood)
    )
    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/like/<int:post_id>')
def like(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))

    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    content = request.form['comment']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO comments (post_id, content) VALUES (?, ?)",
        (post_id, content)
    )

    conn.commit()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()