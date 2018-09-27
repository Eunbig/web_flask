from flask import Flask, request, render_template, g, redirect, url_for, session, escape
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3
import hashlib
import os
import random

DATABASE = './db/usr.db'
app = Flask(__name__, static_folder='uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

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

def fetch_db(sql):
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res

def commit_db(sql):
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def board_write_db(usr_id, b_title, b_data, file_name, file_path):
    sql = "insert into board (b_writer, b_title, b_data, b_filename, b_filepath) values ('%s', '%s','%s','%s','%s')" % (usr_id, b_title, b_data, file_name, file_path)
    return commit_db(sql)

def board_list_db():
    sql = "select idx, b_title, b_writer, dt from board"
    return fetch_db(sql)

def board_view_db(board_idx):
    sql = "select idx, b_title, b_writer, b_data, b_filename, b_filepath, dt from board where idx = '%s'" % (board_idx)
    return fetch_db(sql)

def board_edit_info_db(board_idx, usr_id):
    sql = "select idx, b_title, b_writer, b_data, b_filename, b_filepath from board where idx = '%s' and b_writer = '%s'" % (board_idx, usr_id)
    return fetch_db(sql)

def board_edit_db(board_idx, b_title, b_data, file_name, file_path):
    if file_name:
        sql = "update board SET b_title = '%s', b_data = '%s', b_filename = '%s', b_filepath = '%s', dt = current_timestamp where idx = '%s'" % (b_title, b_data, file_name, file_path, board_idx)
    else:
        sql = "update board SET b_title = '%s', b_data = '%s', dt = current_timestamp where idx = '%s'" % (b_title, b_data, board_idx)
    return commit_db(sql)

def board_delete_db(board_idx):
    sql = "delete from board where idx = '%s'" % (board_idx)
    return commit_db(sql)

def board_delete_reply_db(board_idx):
    sql = "delete from board_reply where board_idx = '%s'" % (board_idx)
    return commit_db(sql)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def board_reply_right_chk(r_writer, r_idx):
    sql = "select * from board_reply where idx = '%s' AND rep_writer = '%s'" % (r_idx, r_writer)
    return fetch_db(sql)

def board_reply_edit_db(rep_idx,rep_data):
    sql = "update board_reply SET rep_data = '%s', dt = current_timestamp where idx = '%s'" % (rep_data, rep_idx)
    return commit_db(sql)

def board_reply_write_db(rep_writer, board_idx, rep_data):
    sql = "insert into board_reply (rep_writer, board_idx, rep_data) values ('%s', '%s', '%s')" %(rep_writer, board_idx, rep_data)
    return commit_db(sql)

def board_reply_view_db(board_idx):
    sql = "select * from board_reply where board_idx = '%s'" % (board_idx)
    return fetch_db(sql)

def board_reply_delete_db(rep_idx):
    sql = "delete from board_reply where idx = '%s'" % (rep_idx)
    return commit_db(sql)

def join_db(usr_id, usr_pw, usr_mail, usr_phone):
    h_usr_pw = hashlib.sha224(usr_pw).hexdigest()
    sql = "insert into usr_table (usr_id, usr_pw, usr_mail, usr_phone) values ('%s', '%s', '%s', '%s')" % (usr_id, h_usr_pw, usr_mail, usr_phone)
    return commit_db(sql)

def login_check(usr_id, usr_pw):
    h_usr_pw = hashlib.sha224(usr_pw).hexdigest()
    sql = "select * from usr_table where usr_id = '%s' AND usr_pw = '%s'" % (usr_id, h_usr_pw)
    return fetch_db(sql)

def usredit_db(usr_id, usr_pw, usr_mail, usr_phone):
    h_usr_pw = hashlib.sha224(usr_pw).hexdigest()
    sql = "update usr_table SET usr_pw = '%s' , usr_mail = '%s', usr_phone= '%s' where usr_id = '%s'" % (h_usr_pw, usr_mail,usr_phone, usr_id)
    return commit_db(sql)

def usr_info_find_db(usr_id):
    sql = "select usr_mail, usr_phone from usr_table where usr_id= '%s'"%(usr_id)
    return fetch_db(sql)

def script_alert(msg):
    script_msg = "<script>alert('%s');history.back()</script>" % (msg)
    return script_msg

def test_chk():
    sql = "select * from usr_table where usr_id = 'guest'"
    return fetch_db(sql)

def create_test_data():
    join_db(usr_id='guest', usr_pw='guest', usr_mail='guest@guest.test', usr_phone='1577-1577')
    board_write_db(usr_id='guest', b_title='Test title', b_data='Test Content', file_name='', file_path='')
    return ''

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory='uploads', filename=filename)

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

@app.route('/guest' , methods=['GET'])
def make_guest():
    if test_chk():
        return "Test account is already exist!"
    else:
        create_test_data()
        return "Test ID/PW is 'guest' <br><button type='button' onclick=location.href='/'>Home</button>"
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
        req_phone = request.form.get('usr_phone')
        join_db(req_id, req_pw, req_mail, req_phone)
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
            res = (usr_info_find_db(usr_id),usr_id)
            return render_template('useredit.html', data=res)
        else:
            return redirect(url_for('index'))
    else:
        if 'usr_id' in session:
            req_pw = request.form.get('usr_pw')
            req_mail = request.form.get('usr_mail')
            req_phone = request.form.get('usr_phone')
            res = usredit_db(escape(session['usr_id']),req_pw, req_mail, req_phone)
            return redirect(url_for('index'))
        else:
            return "Error"
        return ''

@app.route('/board', methods=['GET'])
def board():
    if 'usr_id' in session:
        res = board_list_db()
        return render_template('board.html',data=res)
    else:
        return redirect(url_for('index'))
    return ''

@app.route('/board/<board_idx>', methods=['GET', 'POST'])
def board_view(board_idx):
    if request.method == 'GET':
        if 'usr_id' in session:
            res = board_view_db(board_idx)
            if res[0]['b_writer'] == escape(session['usr_id']):
                b_right = 'true'
            else:
                b_right = 'false'
            r_data = board_reply_view_db(board_idx)
            return render_template('board_view.html',data=res,b_right=b_right,r_data=r_data,usr=escape(session['usr_id']))
        else:
            return redirect(url_for('index'))
        return ''
    else:
        if 'r_edit' in request.form:
            req_data = request.form.get('r_data')
            req_idx = request.form.get('r_idx')
            if board_reply_right_chk(escape(session['usr_id']), req_idx):
                res = board_reply_edit_db(req_idx,req_data)
            else:
                return script_alert("You are not writer")
        elif 'r_write' in request.form:
            req_data = request.form.get('r_data')
            res = board_reply_write_db(escape(session['usr_id']),board_idx,req_data)
            return redirect(url_for('board_view', board_idx=board_idx))
        elif 'r_del' in request.form:
            req_idx = request.form.get('r_idx')
            if board_reply_right_chk(escape(session['usr_id']),req_idx):
                res = board_reply_delete_db(req_idx)
                return redirect(url_for('board_view', board_idx=board_idx))
            else:
                return script_alert("You are not writer")
        else:
            return script_alert("something wrong...")
        return redirect(url_for('board_view',board_idx=board_idx))
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
        if 'b_file' in request.files:
            req_file = request.files['b_file']
            if allowed_file(req_file.filename):
                file_name = "Secure_"+secure_filename(req_file.filename)
                h_file_name = hashlib.md5(file_name+str(datetime.now().second)).hexdigest()
                file_path = './uploads/' + h_file_name + "." + file_name.rsplit('.')[-1]
                req_file.save(file_path)
            else:
                return script_alert("Not good extension")
        else:
            file_name = ''
            file_path = ''
        res = board_write_db(escape(session['usr_id']),req_title, req_data, file_name, file_path)
        return redirect(url_for('board'))
    return ''

@app.route('/board_edit/<board_idx>', methods=['GET', 'POST'])
def board_edit(board_idx):
    if request.method == 'GET':
        if 'usr_id' in session:
            res = board_edit_info_db(board_idx, escape(session['usr_id']))
            if res:
                return render_template('board_edit.html', data=res)
            else:
                return script_alert("You are not Writer")
        else:
            return script_alert("You should log in")
    else:
        req_title = request.form.get('b_title')
        req_data = request.form.get('b_data')
        if 'b_file' in request.files:
            req_file = request.files['b_file']
            if allowed_file(req_file.filename):
                file_name = secure_filename(req_file.filename)
                if file_name == None:
                    file_name = str(datetime.now())
                h_file_name = hashlib.md5(file_name+str(datetime.now().second)).hexdigest()
                file_path = './uploads/' + h_file_name + "." + file_name.rsplit('.')[-1]
                req_file.save(file_path)
            else:
                return script_alert("Not good extension")
            res = board_edit_db(board_idx, req_title, req_data, file_name, file_path)
        else:
            res = board_edit_db(board_idx, req_title, req_data, '', '')
        return redirect(url_for('board'))
    return ''

@app.route('/board_delete/<board_idx>', methods=['GET'])
def board_delete(board_idx):
    if 'usr_id' in session:
        res = board_edit_info_db(board_idx, escape(session['usr_id']))
        if res:
            board_delete_db(board_idx)
            board_delete_reply_db(board_idx)
            return redirect(url_for('board'))
        else:
            return script_alert("Only Writer can delete")
    else:
        return redirect(url_for('index'))
    return ''

if __name__ == '__main__':
    #init_db()
    app.secret_key = 'wlqdprkrhtlqEk'
    app.run(debug=True, port=8989, host='0.0.0.0')
