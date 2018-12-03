import os
from flask import flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

from . import util
from ...utils.counter import counter 

def file(upload_folder):
	'''código retirado de http://flask.pocoo.org/docs/1.0/patterns/fileuploads/'''
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		
		if file and util.allowed_file_format(file.filename):
			filename = "video" + secure_filename(file.filename)[-4:]
			file.save(os.path.join(upload_folder, filename))

			counter(upload_folder, filename)

			return render_template('statistics.html', videopath=os.path.join(upload_folder, "output.mp4"))

	return render_template('home.html')