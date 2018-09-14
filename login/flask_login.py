from flask import Flask, request, render_template, g, redirect, url_for, session, escape
import sqlite3
import hashlib

DATABASE = './db/usr.db'
app = Flask(__name__)

def init_db():
    with app.app_context():
        db = get_db()
        print db
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db .row_factory = sqlite3.Row
    return db

def join_db(usr_id, usr_pw, usr_mail):
    h_usr_pw = hashlib.sha224(usr_pw).hexdigest()
    sql = "insert into usr_table (usr_id, usr_pw, usr_mail) values ('%s', '%s', '%s')" % (usr_id, h_usr_pw, usr_mail)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def show_allusr():
    sql = "select * from usr_table"
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res

def find_usrmail(usr_id):
    sql = "select (usr_mail) from usr_table where usr_id = '%s'" % (usr_id)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    if res:
        return res[0]
    else:
        return ''

def login_check(usr_id, usr_pw):
    h_usr_pw = hashlib.sha224(usr_pw).hexdigest()
    sql = "select * from usr_table where usr_id = '%s' AND usr_pw = '%s'" % (usr_id, h_usr_pw)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res

def modify_db(usr_id, usr_pw, usr_mail):
    h_usr_pw = hashlib.sha224(usr_pw).hexdigest()
    sql = "update usr_table SET usr_pw = '%s' , usr_mail = '%s' where usr_id = '%s'" % (h_usr_pw, usr_mail, usr_id)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

@app.route('/')
def index():
    if 'usr_id' in session:
        data = find_usrmail(escape(session['usr_id']))
        res = ()
        res = (data['usr_mail'],escape(session['usr_id']))
        return render_template('index.html',data = res)
    else:
        return render_template('index.html',data = '')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        if 'usr_id' in session:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    else:
        req_id = request.form.get('usr_id')
        req_pw = request.form.get('usr_pw')
        chk = login_check(req_id, req_pw)
        print chk
        if chk:
            session['usr_id'] = req_id
        return redirect(url_for('login'))
    return ''

@app.route('/join', methods=['GET','POST'])
def join():
    if request.method == 'GET':
        if 'usr_id' in session:
            return redirect(url_for('index'))
        else:
            data = show_allusr()
            return render_template('join.html', usrdata=data)
    else:
        req_id = request.form.get('usr_id')
        req_pw = request.form.get('usr_pw')
        req_mail = request.form.get('usr_mail')
        join_db(req_id, req_pw, req_mail)
        session['usr_id'] = req_id
        return redirect(url_for('index'))
    return ''

@app.route('/delete', methods=['GET', 'POST'])
def session_delete():
    session.pop('usr_id', None)
    return redirect(url_for('index'))

@app.route('/secret', methods=['GET'])
def secret():
    if 'usr_id' in session:
        return "ohhhhhh... you find me %s" % escape(session['usr_id'])
    else:
        return redirect(url_for('index'))
    return ''

@app.route('/modify', methods=['GET', 'POST'])
def modify():
    if request.method == 'GET':
        if 'usr_id' in session:
            data = find_usrmail(escape(session['usr_id']))
            res = ()
            res = (data['usr_mail'], escape(session['usr_id']))
            return render_template('modify.html', data=res)
        else:
            return redirect(url_for('index'))
    else:
        if 'usr_id' in session:
            req_pw = request.form.get('usr_pw')
            req_mail = request.form.get('usr_mail')
            res = modify_db(escape(session['usr_id']),req_pw, req_mail)
            return redirect(url_for('index'))
        else:
            return "Error"
    return ''

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=True , port=11000, host='0.0.0.0')
