import os
from collections import OrderedDict
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
			# Define variáveis para o nome do vídeo e o número da pasta onde será colocado
			filename = "video" + secure_filename(file.filename)[-4:]
			numVideos = len(next(os.walk(upload_folder))[1])

			# Define variáveis para o caminho absoluto e relativo à pasta onde os vídeos estão
			folder = "{0}{1:02d}{2}".format(upload_folder, numVideos, settings.slash)
			folder_relative = "static/data/{0:02d}/".format(numVideos)

			# Cria a pasta para armazenar o vídeo e salva-o nela
			os.makedirs(folder)
			file.save(folder + filename)

			# Executa a função de contagem para o vídeo em questão e extrai as informações
			# do vídeo e da contagem
			video_info, counting_info = counter(folder, filename)

			# Insere nas informações do vídeo o nome e extensão, e ordena as chaves
			video_info["1_Nome"] = secure_filename(file.filename)[:-4]
			video_info["2_Formato"] = filename[-4:]
			video_info = OrderedDict(sorted(video_info.items()))

			# Renderiza o template da página 'statistics.html' passando essas informações
			return render_template('statistics.html', 
									videopath=folder_relative, videoinfo=video_info, countinginfo=counting_info)

	return render_template('home.html')