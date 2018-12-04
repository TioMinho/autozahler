from flask import render_template

def page():
	# Insere nas informações do vídeo o nome e extensão, e ordena as chaves
	video_info = {}
	video_info["1_Nome"] = "aaaa"
	video_info["2_Formato"] = "aaaaa"
	video_info["3_Resolução"] = "aaaa"
	video_info["4_Duração"] = "aaaa"
	video_info["5_Taxa de Quadros"] = "aaaa"
	video_info["6_Profundidade de Cores"] = "aaaa"

	counting_info = {"media": [0, 0, 0], "pico": [0, 0, 0], "results": [12, 7, 15]}

	# Renderiza o template da página 'statistics.html' passando essas informações
	return render_template('statistics.html', 
							videopath="/static/data/00/", videoinfo=video_info, countinginfo=counting_info)