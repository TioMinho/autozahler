import os
from flask import flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

from . import util
from ... import settings
from ...utils.counter import counter 

def file(upload_folder):
	'''código retirado de http://flask.pocoo.org/docs/1.0/patterns/fileuploads/'''
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		
		file = request.files['file']
		
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		
		if file and util.allowed_file_format(file.filename):
			filename = "video" + secure_filename(file.filename)[-4:]
			numVideos = len(next(os.walk(upload_folder))[1])

			folder = "{0}{1:02d}{2}".format(upload_folder, numVideos, settings.slash)
			folder_relative = "static/data/{0:02d}/".format(numVideos)

			os.makedirs(folder)
			file.save(folder + filename)

			counter(folder, filename)

			return render_template('statistics.html', videopath=folder_relative)

	return render_template('home.html')