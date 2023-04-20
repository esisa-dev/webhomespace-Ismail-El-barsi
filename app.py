from flask import Flask, render_template, request, url_for, abort, make_response,redirect
import os
import hashlib


app = Flask(__name__)
users = {
    'user': hashlib.sha256('1234'.encode()).hexdigest()
}

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if username in users and users[username] == hashed_password:
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
        if username in users:
            error_msg = "Username already taken"
            return render_template('create_user.html', error=error_msg)
        else:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            users[username] = hashed_password
            return redirect(url_for('login'))
    else:
        return render_template('create_user.html')

@app.route("/home")
def home():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    path = os.path.expanduser('~')
    files = [f for f in os.listdir(path) if not f.startswith('.')]

    num_dirs = sum(os.path.isdir(os.path.join(path, f)) for f in files)
    num_txt_files = sum(f.endswith('.txt') for f in files)

    elements = []
    for file in files:
        isdir = os.path.isdir(os.path.join(path, file))
        if isdir:
            link = url_for('subfolder', path=os.path.relpath(os.path.join(path, file), os.path.expanduser('~')))
            elements.append((file, isdir, link))
        elif file.endswith('.txt'):
            link = url_for('show_file', path=os.path.relpath(os.path.join(path, file), os.path.expanduser('~')), filename=file)
            elements.append((file, isdir, link))
        else:
            elements.append((file, isdir, None))

    return render_template('home.html', elements=elements, folder=path, num_dirs=num_dirs, num_txt_files=num_txt_files)

@app.route('/<path:path>/')
def subfolder(path):
    path = os.path.join(os.path.expanduser('~'), path)
    try:
        files = [f for f in os.listdir(path) if not f.startswith('.')] 
    except FileNotFoundError:
        abort(404)

    num_dirs = sum(os.path.isdir(os.path.join(path, f)) for f in files)
    num_txt_files = sum([1 for f in files if f.endswith('.txt')])

    elements = []
    for file in files:
        isdir = os.path.isdir(os.path.join(path, file))
        if isdir:
            link = url_for('subfolder', path=os.path.relpath(os.path.join(path, file), os.path.expanduser('~')))
            elements.append((file, isdir, link))
        elif file.endswith('.txt'):
            link = url_for('show_file', path=os.path.relpath(os.path.join(path, file), os.path.expanduser('~')), filename=file)
            elements.append((file, isdir, link))
        else:
            elements.append((file, isdir, None))

    return render_template('home.html', elements=elements, folder=path, num_dirs=num_dirs, num_txt_files=num_txt_files)

@app.route('/file/<path:path>/')
def show_file(path):
    path = os.path.join(os.path.expanduser('~'), path)
    try:
        with open(path, 'r') as f:
            content = f.read()
    except Exception as e:
        return f"Error: {e}"
    return render_template('file.html', content=content)

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
    

