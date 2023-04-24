from flask import Flask, render_template, request, url_for, abort, make_response, redirect,session
import os
import subprocess
import spwd
import crypt
from info  import get_all_info

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route('/')
def index():
    return render_template('login.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            hashed_password = spwd.getspnam(username).sp_pwd
        except KeyError:
            error_msg = "Invalid username or password"
            return render_template('login.html', error=error_msg)
        if hashed_password == crypt.crypt(password, hashed_password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error_msg = "Invalid username or password"
            return render_template('login.html', error=error_msg)
    else:
        return render_template('login.html')


@app.route("/create_user", methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            subprocess.check_output(['id', '-u', username])
            error_msg = "Username already taken"
            return render_template('create_user.html', error=error_msg)
        except subprocess.CalledProcessError:
            command = f"useradd -m -s /bin/bash {username}"
            os.system(command)
            command = f"echo '{username}:{password}' | chpasswd"
            os.system(command)
            return redirect(url_for('login'))
    else:
        return render_template('create_user.html')



@app.route("/home")
def home():
    username = session.get('username', None)
    if not username:
        return redirect(url_for('login'))

    path = os.path.expanduser(f"~{username}")

    elements, num_dirs, num_txt_files, total_size = get_all_info(path)

    return render_template('home.html', username=username, elements=elements, num_dirs=num_dirs, num_txt_files=num_txt_files, total_size=total_size)


@app.route('/<path:path>/')
def subfolder(path):
    username = session.get('username')
    path = os.path.join(os.path.expanduser(f"~{username}"), path)
    try:
        elements, num_dirs, num_txt_files, total_size = get_all_info(path)
    except FileNotFoundError:
        abort(404)

    return render_template('home.html', elements=elements, folder=path, num_dirs=num_dirs, num_txt_files=num_txt_files, total_size=total_size)


@app.route('/file/<path:path>/')
def show_file(path):
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    path = os.path.join(os.path.expanduser(f"~{username}"), path)
    try:
        with open(path, 'r') as f:
            content = f.read()
    except Exception as e:
        return f"Error: {e}"
    return render_template('file.html', content=content)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
