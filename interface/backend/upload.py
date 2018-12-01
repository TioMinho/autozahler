import os
from flask import flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

from . import util

def file(upload_folder):
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
		print(file.filename)
		if file and util.allowed_file_format(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(upload_folder, filename))
			return redirect('statistics')

	return render_template('home.html')