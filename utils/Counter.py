# Declaração de Bibliotecas
import cv2
import numpy as np
import Vehicle
import time

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
	
	# Filtro Limiar Com Binarização Otsu
	_,th = cv2.threshold(img, 0, 1, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	
	# Remove Ruido aleatorio
	for i in range(1,maskSize):
		img = img*np.roll(th, i, axis=1)
	cv2.imshow("Remocao de Ruido aleatorio", img)
   
	# Filtro da mediana
	img = cv2.medianBlur(img,maskSize)
	cv2.imshow("Filtro da mediana", img)
	
	# Binariza a Imagem Final
	_,th = cv2.threshold(img,1,255,cv2.THRESH_BINARY)
	cv2.imshow("Binariza a Imagem Final", th)
	img = th
	
	# Preenchimento de Falhas
	for i in range(1,maskSize):
		img = np.clip(img+np.roll(th,-i,axis=0),0,255)
	cv2.imshow("Preenchimento de Falhas", img)
	
	# Retorna o Frame
	return np.uint8(img)

# Função Principal
def main():
	# Variáveis de Contagem
	cnt_total   = 0
	cnt_pequeno = 0
	cnt_medio   = 0
	cnt_grande  = 0

	# Criando o objeto de VideoCapture
	video = cv2.VideoCapture('data/5.avi')

	# Variáveis de Informação do Vídeo
	img_width = int(video.get(3))
	img_height = int(video.get(4))

	frameArea = img_height*img_width
	areaTH = frameArea / 300

	print("########### VIDEO ###########")
	print("Dimensoes: {0}x{1}".format(img_width, img_height))
	print("Area Total: {0}".format(frameArea))
	print('Area de Threshold: {0}'.format(areaTH))
	print()

	# Linhas de Limite para Contagem
	line_left 		= int(7  * (img_width/100))
	line_left_limit = int(8 * (img_width/100))

	line_right 		 = int(55 * (img_width/100))
	line_right_limit = int(80 * (img_width/100))

	line_right_color = (255, 0,   0)
	line_left_color  = (  0, 0, 255)
	
	print("###### LINHAS DE LIMITE ######")
	print("Linha de Passagem (Direita): {0} - {1}".format(line_right, line_right_limit))
	print("Linha de Passagem (Esquerda): {0} - {1}".format(line_left, line_left_limit))
	print()

	# Create the background subtractor
	rfmg2 = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

	# Variables
	font = cv2.FONT_HERSHEY_SIMPLEX
	vehicles = []
	max_p_age = 5
	pid = 1
	frame_id = 0

	########################
	## CONTAGEM POR FRAME ##
	########################
	while(video.isOpened()):
		#read a frame
		ret, frame = video.read()
		
		# If de matar o frame
		if not ret:
			break;

		frame_id += 1	

		###################
		## PREPROCESSING ##
		###################
		gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		cv2.imshow("Gray - Original", gray_image)
		
		mask = preProc(gray_image, 11, rfmg2)
		
		##################
		## FIND CONTOUR ##
		##################
		_, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

		for cnt in contours:
			cv2.drawContours(mask, cnt, -1, (0, 255, 0), 3, 8)

			area = cv2.contourArea(cnt)
			if area > areaTH and area < 20000:
				################
				#   TRACKING   #
				################
				M = cv2.moments(cnt)
				
				cx = int(M['m10']/M['m00'])
				cy = int(M['m01']/M['m00'])
				
				x, y, w, h = cv2.boundingRect(cnt)

				new = True
				for i in vehicles:
					if abs(x - i.x) <= w and abs(y - i.y) <= h:
						new = False
						i.updateCoords(cx, cy)
						
						if i.going_DOWN(line_right, line_right_limit):
							if(w >= 100):
								if(h >= 70):
									print("{2} - CARRO GRANDE MAH | LARGURA: {0} | ALTURA: {1}".format(w, h, frame_id))
									cnt_grande +=1
								else:
									print("{2} - CARRO MEDIO MAH* | LARGURA: {0} | ALTURA: {1}".format(w/2, h, frame_id))
									print("{2} - CARRO MEDIO MAH* | LARGURA: {0} | ALTURA: {1}".format(w/2, h, frame_id))
									cnt_medio +=2
									
							elif(w >= 50):
								print("{2} - CARRO MEDIO MAH | LARGURA: {0} | ALTURA: {1}".format(w, h, frame_id))
								cnt_medio +=1

							elif(w >= 20):
								print("{2} - MOTINHA MAH | LARGURA: {0} | ALTURA: {1}".format(w, h, frame_id))
								cnt_pequeno +=1

							if(w >= 20):
								roi = gray_image[y:y+h, x:x+w]
								cv2.imshow('Region of Interest', roi)

								cnt_total += 1
						break

					if i.state == '1' and i.x > line_right:
						i.setDone()

					if i.timedOut():
						index = vehicles.index(i)
						vehicles.pop(index)
						del i

				if new == True:
					p = Vehicle.MyVehicle(pid, cx, cy, max_p_age)
					vehicles.append(p)
					pid += 1

				##################
				##   DRAWING    ##
				##################
				cv2.circle(gray_image,(cx, cy), 4, (0,0,255), -1)
				cv2.rectangle(gray_image, (x,y), (x+w,y+h), (0,255,0), 2)

		###############
		##   IMAGE   ##
		###############
		str_up 		= 'total: ' + str(cnt_total)
		str_down 	= 'pequeno:' + str(cnt_pequeno)
		str_medio 	= 'medio:' + str(cnt_medio)
		str_grande 	= 'grande:' + str(cnt_grande)
		
		frame = cv2.line(gray_image, (line_right, 0), (line_right, img_height), (255, 0, 0), 1)
		frame = cv2.line(gray_image, (line_right_limit, 0), (line_right_limit, img_height), (255, 0, 0), 1)

		cv2.putText(frame, str_up, (10,30),font,1,(255,255,255),2,cv2.LINE_AA)
		cv2.putText(frame, str_up, (10,30),font,1,(0,0,255),1,cv2.LINE_AA)
		cv2.putText(frame, str_down, (10,55),font,1,(255,255,255),2,cv2.LINE_AA)
		cv2.putText(frame, str_down, (10,55),font,1,(0,0,255),1,cv2.LINE_AA)
		cv2.putText(frame, str_medio, (10,80),font,1,(255,255,255),2,cv2.LINE_AA)
		cv2.putText(frame, str_medio, (10,80),font,1,(0,0,255),1,cv2.LINE_AA)
		cv2.putText(frame, str_grande, (10,105),font,1,(255,255,255),2,cv2.LINE_AA)
		cv2.putText(frame, str_grande, (10,105),font,1,(0,0,255),1,cv2.LINE_AA)
		
		cv2.imshow('Frame', cv2.resize(gray_image, (400, 300)))

		# Pausa e Verificação da Tecla de Saída (ESC ou Q)
		k = cv2.waitKey(10) & 0xff
		if k == 27:
			break

	# Finalizaçã do Processo de Renderização
	video.release()
	cv2.destroyAllWindows()

	print("########### RESULTADO FINAL ###########")
	print("Total: {0}".format(cnt_total))
	print("Grandes: {0}".format(cnt_grande))
	print("Médios: {0}".format(cnt_medio))
	print("Pequenos: {0}".format(cnt_pequeno))


main()