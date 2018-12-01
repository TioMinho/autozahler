import sys

slash = '/'
if sys.platform == 'win32': slash = '\\'

application_name = 'autozahler'
version = '0.1.0'

UPLOAD_FOLDER = __file__[:-11] + '{}data{}'.format(slash, slash)
ALLOWED_EXTENSIONS = set(['txt', 'avi', 'mp4', 'webm'])