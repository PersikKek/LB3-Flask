from flask import Flask, render_template, current_app, g
import random
from datetime import datetime
import pytz
import psycopg2
import psycopg2.extras
from flask.cli import with_appcontext
import click

### Make the flask app
app = Flask(__name__)

### Routes
@app.route("/dump")
def dump_entries():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date')
    rows = cursor.fetchall()
    output = ""
    for r in rows:
        debug(str(dict(r)))
        output += str(dict(r))
        output += "\n"
    return "<pre>" + output + "</pre>"

@app.route("/")
def hello_world():
    return "Hello, world!"  # Whatever is returned from the function is sent to the browser and displayed.

@app.route("/time")
def get_time():
    now = datetime.now().astimezone(pytz.timezone("Europe/Kiev"))
    timestring = now.strftime("%Y-%m-%d %H:%M:%S")  # format the time as a easy-to-read string
    beginning = "<html><body><h1>The time is: "
    ending = "</h1></body></html>"
    return render_template("time.html", timestring=timestring)

@app.route("/random")
def pick_word():
    random_list = ['Жигадло', 'Олександр', 'КІД-22']
    random_word = random.choice(random_list)
    return render_template("random.html", word=random_word)

@app.route("/browse")
def browse():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date')
    rowlist = cursor.fetchall()
    return render_template('browse.html', entries=rowlist)

# Database handling 
def connect_db():
    debug("Connecting to DB.")
    conn = psycopg2.connect(host="localhost", user="postgres", password="3355", dbname="Flask_db", 
        cursor_factory=psycopg2.extras.DictCursor)
    return conn

def get_db():
    if "db" not in g:
        g.db = connect_db()
    return g.db

@app.cli.command("initdb")
def init_db():
    """Clear existing data and create new tables."""
    conn = get_db()
    cur = conn.cursor()
    with current_app.open_resource("schema.sql") as file: # open the file
        alltext = file.read() # read all the text
        cur.execute(alltext) # execute all the SQL in the file
    conn.commit()
    print("Initialized the database.")

@app.cli.command('populate')
def populate_db():
    conn = get_db()
    cur = conn.cursor()
    with current_app.open_resource("populate.sql") as file: 
        alltext = file.read() 
        cur.execute(alltext) 
    conn.commit()
    print("Populated.")

@app.teardown_appcontext
def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()
        debug("Closing DB")

def debug(s):
    if app.config['DEBUG']:
        print(s)

### Start flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)