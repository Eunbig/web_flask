from flask import Flask, request, url_for, session,escape, g, redirect, render_template
import sqlite3

DATABASE = './db/usr.db'
app = Flask(__name__)

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db .row_factory = sqlite3.Row
    return db

def join_db(usr_id, usr_pw):
    sql = "insert into usr_table (usr_id, usr_pw) values  ('%s', '%s')" % (usr_id, usr_pw)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def login_check(usr_id, usr_pw):
    sql = "select * from usr_table where usr_id = '%s' AND usr_pw = '%s'" %(usr_id, usr_pw)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if 'usr_id' in session:
            return """Hello %s <br> <a href='/logout'>Logout</a>""" % escape(session['usr_id'])
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')
    return ''

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'GET':
        if 'usr_id' in session:
            return redirect(url_for('index'))
        else:
            return render_template('join.html')
    else:
        req_id = request.form.get('usr_id')
        req_pw = request.form.get('usr_pw')
        join_db(req_id, req_pw)
        session['usr_id'] = req_id
        return redirect(url_for('index'))
    return ''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'usr_id' in session:
            return redirect(url_for('index'))
        else:
            return render_template('login.html', data="fail")
    else:
        req_id = request.form.get('usr_id')
        req_pw = request.form.get('usr_pw')
        chk = login_check(req_id, req_pw)
        if chk:
            session['usr_id'] = req_id
            return redirect(url_for('index'))
        else:
            return render_template('login.html', data='fail')
    return ''

@app.route('/login_chk', methods=['GET','POST'])
def login_chk():
    if request.method == 'POST':
        req_id = request.form.get('usr_id')
        req_pw = request.form.get('usr_pw')
        print req_id, req_pw
        chk = login_check(req_id, req_pw)
        print chk
        if chk:
            return 'true'
        else:
            return 'false'

@app.route('/logout')
def logout():
    session.pop('usr_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'rkskekfkakqktk'
    app.run(debug=True, port=8989, host='0.0.0.0')





