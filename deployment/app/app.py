from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3
from werkzeug.exceptions import abort
import requests
import re

def get_db_connection():
    conn = sqlite3.connect('data/database.db')
    # return connection that has attribute row_factory with a dictionary of rows from database.db
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts where id = ?', (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

app = Flask(__name__)
app.config['SECRET_KEY'] = '1956cbb54eaf4c08beadf943e797b152'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/library')
def library():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('library.html', posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/generate', methods=('GET', 'POST'))
def generate():
    generated = {'title':"", 'body':""}
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        preview = predict(title, content)
        generated['title'] = preview[0]
        generated['body']  = preview[1]
        return render_template('create.html', current_generation = generated)
    return render_template('create.html', current_generation = generated)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (request.form['title'], request.form['content']))
        conn.commit()
        conn.close()
        return redirect('/library')
    else:
        return render_template('create.html')
    
def process(response):
    response = re.sub(pattern = "<\|startoftext\|>.*<\|body\|>",
                      repl    = "",
                      string  = response)
    response = re.sub(pattern = "<\|endoftext\|>",
                      repl    = "",
                      string  = response).strip()
    return response

def predict(title, content):
    url = "http://torchserve-mar:8080/predictions/my_model"

    headers = {'Content-Type': 'text/plain'}
    payload = "<|startoftext|>" + title + "<|body|>" + content
    payload = payload.encode('utf-8-sig')
    response = requests.request('POST', url, headers=headers, data=payload).text
    response = process(response)
    
    prediction = [title, response]
    return prediction

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)