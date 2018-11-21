from ... import settings

def allowed_file_format(filename):
	"""Verifica se o formato do arquivo é permitido"""
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS
