from flask import Flask, render_template, redirect, url_for, send_from_directory, flash, send_file
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, login_manager, users_collection, pdfs_collection, socketio
from forms import LoginForm, UploadForm
from models import User
import os
from bson.objectid import ObjectId
from datetime import datetime

predefined_users = {
    "saude": "senha1",
    "esportes": "senha2",
    "cuidados": "senha3",
    "entretenimento": "senha4",
    "criativo": "senha5",
    "admin": "admin"
}

def add_pdf(title, description, filename, cover_image, publish_date):
    pdf = {
        'title': title,
        'description': description,
        'filename': filename,
        'cover_image': cover_image,
        'publish_date': publish_date,
    }
    pdfs_collection.insert_one(pdf)

for username, password in predefined_users.items():
    if not users_collection.find_one({"username": username}):
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({"username": username, "password": hashed_password})

@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data['username'], str(user_data['_id']))
    return None

@app.route('/')
def index():
    current_time = datetime.now()
    
    if current_user.is_authenticated:
        pdf_files = list(pdfs_collection.find())
    else:
        pdf_files = list(pdfs_collection.find({
            'publish_date': {'$lte': current_time}
        }))
    
    return render_template('index.html', pdf_files=pdf_files)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            user_obj = User(user['username'], str(user['_id']))
            login_user(user_obj)
            flash('Bem-vindo!')
            return redirect(url_for('upload'))
        else:
            flash('Nome de usuário ou senha incorretos!')
    return render_template('login.html', form=form)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        cover_image = form.cover_image.data
        pdf_file = form.file.data
        publish_date = form.publish_date.data

        cover_filename = secure_filename(cover_image.filename) if cover_image else ''
        pdf_filename = secure_filename(pdf_file.filename)
        if cover_image:
            cover_image.save(os.path.join(app.config['UPLOAD_FOLDER_COVER'], cover_filename))
        pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))

        pdf_data = {
            'title': title,
            'description': description,
            'cover_image': cover_filename,
            'filename': pdf_filename,
            'publish_date': publish_date,
            'uploaded_by': current_user.username,
            'views': 0,
        }

        result = pdfs_collection.insert_one(pdf_data)

        flash('Upload bem-sucedido! A revista será publicada em {}'.format(pdf_data['publish_date']))
        return redirect(url_for('index'))
    return render_template('upload.html', form=form)

@app.route('/toggle_visibility/<pdf_id>', methods=['POST'])
@login_required
def toggle_visibility(pdf_id):
    pdf = pdfs_collection.find_one({"_id": ObjectId(pdf_id)})
    if not pdf:
        flash('PDF não encontrado!', 'danger')
        return redirect(url_for('index'))
    
    flash('Visibilidade alterada com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/uploads/cover/<filename>')
def uploaded_cover_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_COVER'], filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/edit/<string:pdf_id>', methods=['GET', 'POST'])
@login_required
def edit_pdf(pdf_id):
    pdf = pdfs_collection.find_one({"_id": ObjectId(pdf_id)})
    if not pdf:
        flash('PDF não encontrado!', 'danger')
        return redirect(url_for('index'))
    
    form = UploadForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        publish_date = form.publish_date.data
        cover_image = form.cover_image.data
        pdf_file = form.file.data

        if cover_image:
            cover_filename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join(app.config['UPLOAD_FOLDER_COVER'], cover_filename))
            pdfs_collection.update_one({"_id": ObjectId(pdf_id)}, {"$set": {"cover_image": cover_filename}})
        else:
            cover_filename = pdf['cover_image']

        if pdf_file:
            pdf_filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))
            pdfs_collection.update_one({"_id": ObjectId(pdf_id)}, {"$set": {"filename": pdf_filename}})
        else:
            pdf_filename = pdf['filename']

        pdfs_collection.update_one({"_id": ObjectId(pdf_id)}, {"$set": {
            "title": title,
            "description": description,
            "publish_date": publish_date,
            "cover_image": cover_filename,
            "filename": pdf_filename
        }})

        flash('PDF atualizado com sucesso!', 'success')
        return redirect(url_for('index'))
    
    form.title.data = pdf['title']
    form.description.data = pdf['description']
    form.publish_date.data = pdf['publish_date']
    form.cover_image.data = pdf['cover_image']
    form.file.data = pdf['filename']

    return render_template('edit.html', form=form, pdf=pdf)

@app.route('/remove/<pdf_id>', methods=['POST'])
@login_required
def remove_pdf(pdf_id):
    pdf = pdfs_collection.find_one_and_delete({'_id': ObjectId(pdf_id)})
    if pdf:
        flash('Revista removida com sucesso.')
    else:
        flash('Revista não encontrada.')
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout bem-sucedido!')
    return redirect(url_for('index'))

@app.route('/control')
@login_required
def control():
    pdf_files = list(pdfs_collection.find({}))
    return render_template('control.html', pdf_files=pdf_files)

@app.route('/view/<string:pdf_id>', methods=['GET'])
def view_pdf(pdf_id):
    pdf = pdfs_collection.find_one({"_id": ObjectId(pdf_id)})
    if not pdf:
        flash('PDF não encontrado!', 'danger')
        return redirect(url_for('index'))

    pdfs_collection.update_one({"_id": ObjectId(pdf_id)}, {"$inc": {"views": 1}})
    socketio.emit('update_views', {'pdf_id': pdf_id, 'views': pdf['views'] + 1}, to='*')

    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], pdf['filename']), as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True)