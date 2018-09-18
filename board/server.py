from flask import Flask, request, render_template, g, redirect, url_for, session, escape
import sqlite3
import hashlib

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

def board_write_db(usr_id, b_title, b_data):
    sql = "insert into board (b_writer, b_title, b_data) values ('%s','%s','%s')" % (usr_id, b_title, b_data)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def board_list_db():
    sql = "select idx, b_title, b_writer, dt from board"
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res

def board_view_db(board_idx):
    sql = "select b_title, b_writer, b_data, dt from board where idx = '%s'" % (board_idx)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res

def join_db(usr_id, usr_pw, usr_mail):
    h_usr_pw = hashlib.sha224(usr_pw).hexdigest()
    sql = "insert into usr_table (usr_id, usr_pw, usr_mail) values ('%s', '%s', '%s')" % (usr_id, h_usr_pw, usr_mail)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def login_check(usr_id, usr_pw):
    h_usr_pw = hashlib.sha224(usr_pw).hexdigest()
    sql = "select * from usr_table where usr_id = '%s' AND usr_pw = '%s'" % (usr_id, h_usr_pw)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res

def usredit_db(usr_id, usr_pw, usr_mail):
    h_usr_pw = hashlib.sha224(usr_pw).hexdigest()
    sql = "update usr_table SET usr_pw = '%s' , usr_mail = '%s' where usr_id = '%s'" % (h_usr_pw, usr_mail, usr_id)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def usr_mail_find_db(usr_id):
    sql = "select usr_mail from usr_table where usr_id= '%s'"%(usr_id)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if 'usr_id' in session:
            res = "Hi %s~" % (escape(session['usr_id']))
            return render_template('index.html',data = res)
        else:
            return render_template('index.html')
    else:
        return redirect(url_for('index'))
    return ''

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
            return render_template('join.html')
    else:
        req_id = request.form.get('usr_id')
        req_pw = request.form.get('usr_pw')
        req_mail = request.form.get('usr_mail')
        join_db(req_id, req_pw, req_mail)
        session['usr_id'] = req_id
        return redirect(url_for('index'))
    return ''

@app.route('/logout', methods=['GET', 'POST'])
def session_delete():
    session.pop('usr_id', None)
    return redirect(url_for('index'))

@app.route('/useredit', methods=['GET', 'POST'])
def useredit():
    if request.method == 'GET':
        if 'usr_id' in session:
            usr_id = escape(session['usr_id'])
            res = (usr_mail_find_db(usr_id)[0][0],usr_id)
            return render_template('useredit.html', data=res)
        else:
            return redirect(url_for('index'))
    else:
        if 'usr_id' in session:
            req_pw = request.form.get('usr_pw')
            req_mail = request.form.get('usr_mail')
            res = usredit_db(escape(session['usr_id']),req_pw, req_mail)
            return redirect(url_for('index'))
        else:
            return "Error"
        return ''

@app.route('/board', methods=['GET'])
def board():
    if 'usr_id' in session:
        res = board_list_db()
        print res
        return render_template('board.html',data=res)
    else:
        return redirect(url_for('index'))
    return ''

@app.route('/board/<board_idx>')
def board_view(board_idx):
    if 'usr_id' in session:
        res = board_view_db(board_idx)
        print res
        return render_template('board_view.html',data=res)
    else:
        return redirect(url_for('index'))
    return ''

@app.route('/board_write', methods=['GET', 'POST'])
def board_write():
    if request.method == 'GET':
        if 'usr_id' in session:
            res = escape(session['usr_id'])
            return render_template('board_write.html',data=res)
        else:
            return redirect(url_for('index'))
    else:
        req_title = request.form.get('b_title')
        req_data = request.form.get('b_data')
        res = board_write_db(escape(session['usr_id']),req_title, req_data)
        return redirect(url_for('board'))
    return ''

if __name__ == '__main__':
    app.secret_key = 'wlqdprkrhtlqEk'
    app.run(debug=True, port=8989, host='0.0.0.0')
