import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Configure root logger
logging.basicConfig(level=logging.DEBUG)

# Create handlers for STDERR and STDOUT
stderr_handler = logging.StreamHandler(sys.stderr)
stdout_handler = logging.StreamHandler(sys.stdout)

# Create formatters for the handlers
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

# Set the formatter for each handler
stderr_handler.setFormatter(formatter)
stdout_handler.setFormatter(formatter)

# Create loggers
stderr_logger = logging.getLogger('stderr_logger')
stdout_logger = logging.getLogger('stdout_logger')

# Set the log level for each logger
stderr_logger.setLevel(logging.ERROR)
stdout_logger.setLevel(logging.INFO)

# Add the handlers to the loggers
stderr_logger.addHandler(stderr_handler)
stdout_logger.addHandler(stdout_handler)

connection_count = 0

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        stderr_logger.error('404: No article')
        return render_template('404.html'), 404
    else:
      stdout_logger.info(f'Article {post["title"]}')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    stdout_logger.info('About page')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            stdout_logger.info(f'Article Created: {title}')

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def status():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response

@app.route('/metrics')
def metrics():
    global connection_count
    connection = get_db_connection()
    n_posts = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    # Get the total amount of connections to the database
    connection.close()

    response = app.response_class(
            response=json.dumps({
                "status": "success",
                "code": 0,
                "data": {"db_connection_count": connection_count, "post_count": n_posts}}),
            status=200,
            mimetype='application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111')
