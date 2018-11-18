import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from ... import settings

app = Flask(settings.application_name)

app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
	'''código retirado de http://flask.pocoo.org/docs/1.0/patterns/fileuploads/'''
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit an empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			print(__file__)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('uploaded_file',
									filename=filename))
	return '''
	<!doctype html>
	<title>Upload new File</title>
	<h1>Upload new File</h1>
	<form method=post enctype=multipart/form-data>
	  <input type=file name=file>
	  <input type=submit value=Upload>
	</form>
	'''

@app.route('/uploaded_file')
def uploaded_file():
	return 'Uploaded'

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS
