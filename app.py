# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash, render_template_string

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, category, text from entries order by id desc')
    category_col = db.execute('SELECT DISTINCT category FROM entries')
    categories = category_col.fetchall()
    entries = cur.fetchall()
    # created a seperate variable for the HTML so that the category filter can filter all without change
    return render_template('show_entries.html', entries=entries, categories=categories)


@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('insert into entries (title, category, text) values (?, ?, ?)',
               [request.form['title'], request.form['category'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

# filter the posts to what we specify
@app.route('/filter', methods=['POST'])
def show_filter():
    # variable to get the category we want, not needed but neater
    f_category = request.form.get('categories')
    db = get_db()
    # get all categories for filter
    category = db.execute('SELECT DISTINCT category FROM entries')
    categories = category.fetchall()
    if f_category != 'Home':
        # filter the posts to have the categories wanted be the only posts shown
        filtered = db.execute(f"SELECT DISTINCT * FROM entries WHERE category='{f_category}' ORDER BY id DESC")
        entries = filtered.fetchall()
        return render_template('show_entries.html', entries=entries, categories=categories)
    else:
        cur = db.execute('select title, category, text from entries order by id desc')
        entries = cur.fetchall()
        return render_template('show_entries.html', entries=entries, categories=categories)

