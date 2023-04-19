from flask import Flask, render_template, request, url_for, abort
import os


app = Flask(__name__)

@app.route("/")
def home():
    path = os.path.expanduser('~') 
    files = [f for f in os.listdir(path) if not f.startswith('.')]  
    elements = []
    for file in files:
        isdir = os.path.isdir(os.path.join(path, file))
        if isdir:
            link = url_for('subfolder', path=os.path.relpath(os.path.join(path, file), os.path.expanduser('~')))
            elements.append((file, isdir, link))
        else:
            elements.append((file, isdir, None))
    return render_template('home.html', elements=elements, folder=path)

@app.route('/<path:path>/')
def subfolder(path):
    path = os.path.join(os.path.expanduser('~'), path)
    try:
        files = [f for f in os.listdir(path) if not f.startswith('.')]  
    except FileNotFoundError:
        abort(404)
    elements = []
    for file in files:
        isdir = os.path.isdir(os.path.join(path, file))
        if isdir:
            link = url_for('subfolder', path=os.path.relpath(os.path.join(path, file), os.path.expanduser('~')))
            elements.append((file, isdir, link))
        else:
            elements.append((file, isdir, None))
    return render_template('home.html', elements=elements)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090, debug=True)
    

