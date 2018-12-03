# Declaração de Bibliotecas
import cv2
import numpy as np
from vehicle import Vehicle
import time
import json

# Função para posicionar cada janela do OpenCV
def moveAllWindows():
	cv2.namedWindow("Img - Original")
	cv2.moveWindow("Img - Original", 40,30)

	cv2.namedWindow("Equalizacao de Histograma")
	cv2.moveWindow("Equalizacao de Histograma", 340,30)

	cv2.namedWindow("Remocao de Fundo")
	cv2.moveWindow("Remocao de Fundo", 640,30)

	cv2.namedWindow("Filtro Limiar Com Binarizacao")
	cv2.moveWindow("Filtro Limiar Com Binarizacao", 940,30)

	cv2.namedWindow("Remocao de Ruido aleatorio")
	cv2.moveWindow("Remocao de Ruido aleatorio", 1240,30)

	cv2.namedWindow("Filtro da Media")
	cv2.moveWindow("Filtro da Media", 40,330)

	cv2.namedWindow("Filtro da Mediana")
	cv2.moveWindow("Filtro da Mediana", 340,330)

	cv2.namedWindow("Binariza a Imagem Final")
	cv2.moveWindow("Binariza a Imagem Final", 640,330)

	cv2.namedWindow("Preenchimento de Falhas")
	cv2.moveWindow("Preenchimento de Falhas", 940, 330)


def preProc (img, maskSize, backgroundSubtractor):
	"""
	Parametros da Função
	Img:                  Imagem em escala de cinza
	maskSize:             Tamanho(IMPAR) da mascara para filtro da mediana e rolagem
	backgroundSubtractor: cv2.createBackgroundSubtractorMOG2()
	"""
	cv2.imshow("Img - Original", img)
	
	#Equalização de Histograma
	img = cv2.equalizeHist(img)
	cv2.imshow("Equalizacao de Histograma", img)
	
	# Remoção de Fundo
	img = backgroundSubtractor.apply(img)
	cv2.imshow("Remocao de Fundo", img)
	
	# Filtro Limiar Com Binarização
	img = np.uint8(img*255)
	_,th = cv2.threshold(img, 127, 255, cv2.THRESH_TOZERO)
	cv2.imshow("Filtro Limiar Com Binarizacao", np.uint8(th*255))

	# Remove Ruido aleatorio
	for i in range(1,maskSize):
		img = img*np.roll(th, i, axis=1)
	cv2.imshow("Remocao de Ruido aleatorio", img)

	# Filtro da media para religar contours desconectados
	img = cv2.GaussianBlur(th, (maskSize, maskSize), 0) 
	cv2.imshow("Filtro da Media", img)

	# Filtro da mediana
	img = cv2.medianBlur(img, maskSize)
	cv2.imshow("Filtro da Mediana", img)
	
	# Binariza a Imagem Final
	_,th = cv2.threshold(img,45,255,cv2.THRESH_BINARY)
	cv2.imshow("Binariza a Imagem Final", th)
	img = th
	
	# Preenchimento de Falhas
	for i in range(1,maskSize):
		img = np.clip(img+np.roll(th,-i,axis=0),0,255)
	cv2.imshow("Preenchimento de Falhas", img)

	# Retorna o Frame
	return np.uint8(img)

# Função Principal
def counter(filepath):
	# Variáveis de Contagem
	cnt_min 	 = {"time": "", "total": 0, "pequeno": 0, "medio": 0, "grande": 0}
	cnt_min_rows = []

	cnt_total 	 = {"total": 0, "pequeno": 0, "medio": 0, "grande": 0}

	# Criando o objeto de VideoCapture
	video = cv2.VideoCapture(filepath)

	# Variáveis de Informação do Vídeo
	img_width = int(video.get(3))
	img_height = int(video.get(4))

	fps = int(video.get(5))

	frameArea = img_height*img_width
	areaTH = frameArea / 175

	print("########### VIDEO ###########")
	print("Dimensoes: {0}x{1}".format(img_width, img_height))
	print("Frames p/ Segundo: {0}".format(fps))
	print("Area Total: {0}".format(frameArea))
	print('Area de Threshold: {0}'.format(areaTH))
	print()

	# Linhas de Limite para Contagem
	line_left 		= int(30  * (img_width/100))
	line_right 		= int(95 * (img_width/100))
	line_up			= int(5  * (img_height/100))
	line_down		= int(60  * (img_height/100))

	line_center 	= int(line_left + (50 * ((line_right - line_left)/100)))
	
	print("###### LINHAS DE LIMITE ######")
	print("Região de Interesse (Linha Esquerda): {0}".format(line_left))
	print("Região de Interesse (Linha Cima): {0}".format(line_up))
	print("Região de Interesse (Linha Direita): {0}".format(line_right))
	print("Região de Interesse (Linha Baixo): {0}".format(line_down))
	
	print("Região de Interesse (Linha Central): {0}".format(line_center))
	print()

	# Define o Codec e Objeto de Escrita de Vídeo
	fourcc = cv2.VideoWriter_fourcc(*'MP4V')
	out = cv2.VideoWriter('data/output.mp4', fourcc, 30.0, (img_width, img_height), 0)

	# Cria o objeto do extrator de fundo
	rfmg2 = cv2.createBackgroundSubtractorMOG2()

	# Variáveis auxiliares dos processamentos
	font = cv2.FONT_HERSHEY_SIMPLEX
	vehicles = []
	max_p_age = 5000
	pid = 1
	frame_id = 0
	lastTime = -1

	# Chama função para posicionar as janelas do OpenCV
	moveAllWindows()

	# Seleciona o frame inicial do vídeo
	# 220, 15100, 3800
	video.set(1, 1)

	########################
	## CONTAGEM POR FRAME ##
	########################
	while(video.isOpened()):
		# Obtém um frame do arquivo de vídeo
		ret, frame = video.read()
		
		# Verifica se o frame em questão é o último do vídeo
		if not ret:
			break;

		# Atualiza contador de frames e o segundo do vídeo
		frame_id += 1	
		frame_time = frame_id // fps

		###################
		## PREPROCESSING ##
		###################
		# Converte a imagem para preto e branco e realiza pré-processamento
		gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		mask = preProc(gray_image, 11, rfmg2)
		
		##################
		## FIND CONTOUR ##
		##################
		# Extrai todos os Contours da imagem
		_, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

		# Para cada contour, iremos buscar um objeto de veículo que mais se assemelha ao contour
		# e verificamos se ele cruzou a linha central.
		for cnt in contours:

			# Calculamos a área do Contour para só considerar contours de tamanho adequado
			area = cv2.contourArea(cnt)
			if area > areaTH and area < 20000:
				################
				#   TRACKING   #
				################
				# Calculamos e exibimos o retângulo de segmentação desse contour
				M = cv2.moments(cnt)
				
				cx = int(M['m10']/M['m00'])
				cy = int(M['m01']/M['m00'])

				x, y, w, h = cv2.boundingRect(cnt)
				
				roi = gray_image[y:y+h, x:x+w]
				cv2.imshow('Region of Interest', roi)
	
				# Realizamos a busca por algum objeto de Vehicle que possua propriedades (posição e tamanho)
				# semelhante aos do contour que está sendo analisado
				new = True
				for i in vehicles:
					if abs(x - i.x) <= w and abs(y - i.y) <= h:
						new = False

						# if(cx <= i.x):
						# 	i.state = '1'

						# Atualizamos as coordenadas do objeto com base nas coordenadas do Contour
						i.updateCoords(cx, cy)
						
						# Verificamos se o objeto cruzou a linha, e então incluimos na contagem adequada
						if i.crossed_line(line_center, line_center+10):
							if(w >= 95):
								if(h >= 60):
									print("{2} - CARRO GRANDE | LARGURA: {0} | ALTURA: {1}".format(w, h, frame_id))
									cnt_total["grande"] += 1
									cnt_min["grande"] += 1

								else:
									print("{2} - CARRO MEDIO* | LARGURA: {0} | ALTURA: {1}".format(w/2, h, frame_id))
									print("{2} - CARRO MEDIO* | LARGURA: {0} | ALTURA: {1}".format(w/2, h, frame_id))
									cnt_total["medio"] += 2
									cnt_total["total"] += 1

									cnt_min["medio"] += 2
									cnt_min["total"] += 1
									
							elif(w >= 50):
								print("{2} - CARRO MEDIO | LARGURA: {0} | ALTURA: {1}".format(w, h, frame_id))
								cnt_total["medio"] += 1
								cnt_min["medio"] += 1

							elif(w >= 20):
								print("{2} - MOTINHA | LARGURA: {0} | ALTURA: {1}".format(w, h, frame_id))
								cnt_total["pequeno"] += 1
								cnt_min["pequeno"] += 1

							if(w >= 20):
								roi = gray_image[y:y+h, x:x+w]
								cv2.imshow('Region of Interest 2', roi)

								cv2.imwrite("utils/tmp/roi_"+str(frame_id)+".png", roi)

								cnt_total["total"] += 1
								cnt_min["total"] += 1
						break

					# Caso o veículo possua estado '1' (cruzou a linha de chegada), apagamos esse objeto da lista
					# (Eĺe não poderá ser contado novamente e nem nos interessa).
					if i.state == '1' and i.x > line_center:
						i.setDone()
						index = vehicles.index(i)
						vehicles.pop(index)
						del i

				# Se nenhum objeto de Vehicle foi encontrado no passo anterior, criamos um novo objeto para
				# mantermos esse novo contour em observação.
				if new == True and cx >= line_left and cx <= line_right and cy <= line_down and cy >= line_up:
					p = Vehicle(pid, cx, cy, max_p_age)
					vehicles.append(p)
					pid += 1

				##################
				##   DRAWING    ##
				##################
				# Desenhamos o bounding-box sobre os contours identiicados
				cv2.circle(gray_image,(cx, cy), 4, (0,0,255), -1)
				cv2.rectangle(gray_image, (x,y), (x+w,y+h), (0,255,0), 2)

		###############
		##   IMAGE   ##
		###############
		# Imprimimos um texto na imagem de exibição para mostrar a contagem em tempo-real
		str_up 		= 'total: ' + str(cnt_total["total"])
		str_down 	= 'pequeno:' + str(cnt_total["pequeno"])
		str_medio 	= 'medio:' + str(cnt_total["medio"])
		str_grande 	= 'grande:' + str(cnt_total["grande"])
		
		# Incluimos algumas linhas de limites para analisar o vídeo
		frame = cv2.line(gray_image, (line_right, 0), (line_right, img_height), (255, 0, 0), 1)
		frame = cv2.line(gray_image, (line_left, 0), (line_left, img_height), (255, 0, 0), 1)
		frame = cv2.line(gray_image, (0, line_up), (img_width, line_up), (255, 0, 0), 1)
		frame = cv2.line(gray_image, (0, line_down), (img_width, line_down), (255, 0, 0), 1)

		frame = cv2.line(gray_image, (line_center, 0), (line_center, img_height), (255, 0, 0), 2)

		cv2.putText(frame, str_up, (10,30),font,1,(255,255,255),2,cv2.LINE_AA)
		cv2.putText(frame, str_up, (10,30),font,1,(0,0,255),1,cv2.LINE_AA)
		cv2.putText(frame, str_down, (10,55),font,1,(255,255,255),2,cv2.LINE_AA)
		cv2.putText(frame, str_down, (10,55),font,1,(0,0,255),1,cv2.LINE_AA)
		cv2.putText(frame, str_medio, (10,80),font,1,(255,255,255),2,cv2.LINE_AA)
		cv2.putText(frame, str_medio, (10,80),font,1,(0,0,255),1,cv2.LINE_AA)
		cv2.putText(frame, str_grande, (10,105),font,1,(255,255,255),2,cv2.LINE_AA)
		cv2.putText(frame, str_grande, (10,105),font,1,(0,0,255),1,cv2.LINE_AA)
		
		# Exibimos o frame atual da contagem na janela
		cv2.imshow('Frame', cv2.resize(gray_image, (400, 300)))

		# Salva a imagem em um arquivo
		if(frame_time % 30 == 0 and frame_time != lastTime):
			lastTime = frame_time

			cnt_min["time"] = "{0:02d}:{1:02d}".format(frame_time // 60, frame_time % 60)
			cnt_min_rows.append(cnt_min)

			cnt_min = {"total": 0, "pequeno": 0, "medio": 0, "grande": 0}

		out.write(gray_image)

		# Pausa e Verificação da Tecla de Saída (ESC ou Q)
		k = cv2.waitKey(1) & 0xff
		if k == 27:
			break

	# Finalização do Processo de Renderização
	video.release()
	out.release()
	cv2.destroyAllWindows()

	print("########### RESULTADO FINAL ###########")
	print("Total: {0}".format(cnt_total["total"]))
	print("Grandes: {0}".format(cnt_total["grande"]))
	print("Médios: {0}".format(cnt_total["medio"]))
	print("Pequenos: {0}".format(cnt_total["pequeno"]))

	# Salva os dados de contagem 
	countingData = {"total": cnt_total, "timeseries": cnt_min_rows}
	with open('data/counting.json', 'w') as fp:
		json.dump(countingData, fp, indent=4)

counter("data/5.avi")