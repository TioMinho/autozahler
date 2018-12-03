# Declaração de Bibliotecas
import cv2
import numpy as np
import Vehicle
import time

def hist_match(source, template):
    oldshape = source.shape
    source = source.ravel()
    template = template.ravel()

    s_values, bin_idx, s_counts = np.unique(source, return_inverse=True,
                                            return_counts=True)
    t_values, t_counts = np.unique(template, return_counts=True)

    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]
    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]

    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)

    return interp_t_values[bin_idx].reshape(oldshape)

def histMatch(img, mask):
    oldshape = img.shape
    img = img.ravel()
    mask = mask.ravel()
    s_values, bin_idx, s_counts = np.unique(img, return_inverse=True,
                                            return_counts=True)

    t_values, t_counts = np.unique(mask, return_counts=True)

    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]

    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]

    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)
    img = interp_t_values[bin_idx].reshape(oldshape)

    return img

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

	cv2.namedWindow("Dilatação")
	cv2.moveWindow("Dilatação", 1240, 330)


def preProc (img, maskSize, backgroundSubtractor, template):
	"""
	Parametros da Função
	Img:                  Imagem em escala de cinza
	maskSize:             Tamanho(IMPAR) da mascara para filtro da mediana e rolagem
	backgroundSubtractor: cv2.createBackgroundSubtractorMOG2()
	"""
	cv2.imshow("Img - Original", img)
	
	#Equalização de Histograma
	# clahe = cv2.createCLAHE(clipLimit=10, tileGridSize=(maskSize, maskSize))
	# img = clahe.apply(img)
	img = cv2.equalizeHist(img)
	# img = histMatch(img, template)
	cv2.imshow("Equalizacao de Histograma", img)
	
	# Remoção de Fundo
	img = backgroundSubtractor.apply(img)
	cv2.imshow("Remocao de Fundo", img)
	
	# Filtro Limiar Com Binarização
	# _,th = cv2.threshold(img, 0, 1, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	# cv2.imshow("Filtro Limiar Com Binarizacao", np.uint8(th*255))
	# img = np.uint8(th*255)

	img = np.uint8(img*255)
	_,th = cv2.threshold(img, 127, 255, cv2.THRESH_TOZERO)
	cv2.imshow("Filtro Limiar Com Binarizacao", np.uint8(th*255))

	# Remove Ruido aleatorio
	for i in range(1,maskSize):
		img = img*np.roll(th, i, axis=1)
	cv2.imshow("Remocao de Ruido aleatorio", img)

	# Filtro da media para religar contours desconectados
	img = cv2.GaussianBlur(th, (maskSize, maskSize), 1) 
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
	
	# Dilatação para preencher buracos
	# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
	# img = cv2.dilate(img, kernel, iterations=1)
	# cv2.imshow("Dilatação", img)

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

	# Criando template de especificação de histograma
	template1 = cv2.imread('data/Template1.png', 0)
	template2 = cv2.imread('data/Template2.png', 0)

	# Variáveis de Informação do Vídeo
	img_width = int(video.get(3))
	img_height = int(video.get(4))

	frameArea = img_height*img_width
	areaTH = frameArea / 175

	print("########### VIDEO ###########")
	print("Dimensoes: {0}x{1}".format(img_width, img_height))
	print("Area Total: {0}".format(frameArea))
	print('Area de Threshold: {0}'.format(areaTH))
	print()

	# Linhas de Limite para Contagem
	line_left 		= int(36  * (img_width/100))
	line_right 		= int(90 * (img_width/100))
	line_up			= int(10  * (img_height/100))
	line_down		= int(60  * (img_height/100))

	line_center 	= int(line_left + (65 * ((line_right - line_left)/100)))

	line_right_color = (255, 0,   0)
	line_left_color  = (  0, 0, 255)
	
	print("###### LINHAS DE LIMITE ######")
	print("Linha de Passagem (Esquerda): {0}".format(line_left))
	print("Linha de Passagem (Direita): {0}".format(line_right))
	print()

	# Create the background subtractor
	rfmg2 = cv2.createBackgroundSubtractorMOG2()

	# Variables
	font = cv2.FONT_HERSHEY_SIMPLEX
	vehicles = []
	max_p_age = 5
	pid = 1
	frame_id = 0

	moveAllWindows()

	# 200, 15100 
	video.set(1, 1)

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
		mask = preProc(gray_image, 11, rfmg2, template2)
		
		##################
		## FIND CONTOUR ##
		##################
		_, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

		for cnt in contours:
			# cv2.drawContours(mask, cnt, -1, (0, 255, 0), 3, 8)

			area = cv2.contourArea(cnt)
			if area > areaTH and area < 20000:
				################
				#   TRACKING   #
				################
				M = cv2.moments(cnt)
				
				cx = int(M['m10']/M['m00'])
				cy = int(M['m01']/M['m00'])
				
				x, y, w, h = cv2.boundingRect(cnt)
				
				roi = gray_image[y:y+h, x:x+w]
				cv2.imshow('Region of Interest', roi)
	
				new = True
				for i in vehicles:
					if abs(x - i.x) <= w and abs(y - i.y) <= h:
						new = False
						i.updateCoords(cx, cy)
						
						if i.crossed_line(line_center, line_center+10):
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
								cv2.imshow('Region of Interest 2', roi)

								cv2.imwrite("utils/tmp/roi_"+str(frame_id)+".png", roi)

								cnt_total += 1
						break

					if i.state == '1' and i.x > line_left:
						i.setDone()

					if i.timedOut():
						index = vehicles.index(i)
						vehicles.pop(index)
						del i

				if new == True and cx >= line_left:
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
		
		# frame = cv2.line(gray_image, (line_right, 0), (line_right, img_height), (255, 0, 0), 1)
		# frame = cv2.line(gray_image, (line_left, 0), (line_left, img_height), (255, 0, 0), 1)
		# frame = cv2.line(gray_image, (0, line_up), (img_width, line_up), (255, 0, 0), 1)
		# frame = cv2.line(gray_image, (0, line_down), (img_width, line_down), (255, 0, 0), 1)

		frame = cv2.line(gray_image, (line_center, 0), (line_center, img_height), (255, 0, 0), 2)

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
		k = cv2.waitKey(1) & 0xff
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