import os
from ... import settings

from . import upload

app = Flask(settings.application_name)

app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER

#Bloco de associação de paths com suas respectivas paginas/funções

@app.route('/', methods=['GET', 'POST'])
upload.file()

@app.route('/upload_successful')
def upload_successful():
	return 'upload_successful'

#Fim fo bloco de associação de paths