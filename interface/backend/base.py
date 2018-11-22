from flask import Flask

from ... import settings
from . import upload, statistics

app = Flask(settings.application_name)

app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER

#Bloco de associação de paths com suas respectivas paginas/funções

@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
	return upload.file(settings.UPLOAD_FOLDER)

@app.route('/statistics')
def final_page():
	return statistics.page()

#Fim fo bloco de associação de paths