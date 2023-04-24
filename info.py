from flask import url_for
import os
from datetime import datetime
def get_all_info(path):
    files = [f for f in os.listdir(path) if not f.startswith('.')]
    num_dirs = sum(os.path.isdir(os.path.join(path, f)) for f in files)
    num_txt_files = sum(f.endswith('.txt') for f in files)
    total_size = round(sum(os.path.getsize(os.path.join(path, f)) for f in files) / (1024 * 1024), 0)
    elements = []
    for file in files:
        isdir = os.path.isdir(os.path.join(path, file))
        if isdir:
            link = url_for('subfolder', path=os.path.relpath(os.path.join(path, file), path))
            unmdate = os.path.getmtime(os.path.join(path, file))
            moddate = datetime.fromtimestamp(unmdate).strftime('%Y-%m-%d')
            size = sum(os.path.getsize(os.path.join(path, file, f)) for f in os.listdir(os.path.join(path, file)) if not f.startswith('.'))
            size = round(size / (1024 * 1024), 2)
            elements.append((file, isdir, link, moddate, size))
        elif file.endswith('.txt'):
            link = url_for('show_file', path=os.path.relpath(os.path.join(path, file), path), filename=file)
            unmdate = os.path.getmtime(os.path.join(path, file))
            moddate = datetime.fromtimestamp(unmdate).strftime('%Y-%m-%d')
            size = os.path.getsize(os.path.join(path, file))
            elements.append((file, isdir, link, moddate, size))
        else:
            unmdate = os.path.getmtime(os.path.join(path, file))
            moddate = datetime.fromtimestamp(unmdate).strftime('%Y-%m-%d')
            size = os.path.getsize(os.path.join(path, file))
            size = round(size / (1024 * 1024), 2)
            elements.append((file, isdir, moddate, size))

    return elements, num_dirs, num_txt_files, total_size