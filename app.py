from flask import Flask, render_template, request, url_for, abort, make_response, redirect
import os
import subprocess
import spwd
import crypt
import shutil
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
            resp = make_response(redirect(url_for('home')))
            resp.set_cookie('username', username)
            return resp
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
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    
    path = os.path.expanduser(f"~{username}")

    files = [f for f in os.listdir(path) if not f.startswith('.')]

    num_dirs = sum(os.path.isdir(os.path.join(path, f)) for f in files)
    num_txt_files = sum(f.endswith('.txt') for f in files)
    total_size = round(sum(os.path.getsize(os.path.join(path, f)) for f in files) / (1024 * 1024), 0)
    elements = []
    for file in files:
        isdir = os.path.isdir(os.path.join(path, file))
        if isdir:
            link = url_for('subfolder', path=os.path.relpath(os.path.join(path, file), path))
            elements.append((file, isdir, link))
        elif file.endswith('.txt'):
            link = url_for('show_file', path=os.path.relpath(os.path.join(path, file), path), filename=file)
            elements.append((file, isdir, link))
        else:
            elements.append((file, isdir, None))

    return render_template('home.html', elements=elements, folder=path, num_dirs=num_dirs, num_txt_files=num_txt_files, total_size=total_size)


@app.route('/<path:path>/')
def subfolder(path):
    username = request.cookies.get('username')
    path = os.path.join(os.path.expanduser(f"~{username}"), path)
    try:
        files = [f for f in os.listdir(path) if not f.startswith('.')] 
    except FileNotFoundError:
        abort(404)

    num_dirs = sum(os.path.isdir(os.path.join(path, f)) for f in files)
    num_txt_files = sum([1 for f in files if f.endswith('.txt')])
    total_size = round(sum(os.path.getsize(os.path.join(path, f)) for f in files) / (1024 * 1024), 0)

    elements = []
    for file in files:
        isdir = os.path.isdir(os.path.join(path, file))
        if isdir:
            link = url_for('subfolder', path=os.path.relpath(os.path.join(path, file), path))
            elements.append((file, isdir, link))
        elif file.endswith('.txt'):
            link = url_for('show_file', path=os.path.relpath(os.path.join(path, file), path), filename=file)
            elements.append((file, isdir, link))
        else:
            elements.append((file, isdir, None))

    return render_template('home.html', elements=elements, folder=path, num_dirs=num_dirs, num_txt_files=num_txt_files, total_size=total_size)

@app.route('/file/<path:path>/')
def show_file(path):
    username = request.cookies.get('username')
    path = os.path.join(os.path.expanduser(f"~{username}"), path)
    try:
        with open(path, 'r') as f:
            content = f.read()
    except Exception as e:
        return f"Error: {e}"
    return render_template('file.html', content=content)

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('username')
    return resp



if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
    

