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
    _,th = cv2.threshold(img,0,1,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    cv2.imshow("Filtro Limiar Com Binarizacao Otsu", np.uint8(th*255))
    img = np.uint8(th*255)
    
    # Remove Ruido aleatorio
    for i in range(1,maskSize):
        img = img*np.roll(th,i,axis=1)
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

def main():
    cnt_down = 0
    cnt_pequeno = 0
    cnt_medio = 0
    cnt_grande = 0

    cap = cv2.VideoCapture('../data/5.avi')

    w = cap.get(3)
    h = cap.get(4)
    frameArea = h*w
    areaTH = frameArea/200
    print('Area Threshold', areaTH)

    # Input/Output Lines
    line_up = int(7*(w/10))
    line_down = 65*(w/100)

    up_limit = int(1*(w/10))
    down_limit = int(9*(w/10))

    print("Red line y:", str(line_down))
    print("Blue line y:", str(line_up))
    
    line_down_color = (255,0,0)
    line_up_color = (0,0,255)
    
    pt1 = [1, 0]
    pt2 = [1, 0]
    pts_L1 = np.array([pt1,pt2], np.int32)
    pts_L1 = pts_L1.reshape((-1,1,2))
    pt3 = [line_up, 0]
    pt4 = [line_up, w]
    pts_L2 = np.array([pt3,pt4], np.int32)
    pts_L2 = pts_L2.reshape((-1,1,2))

    pt5 = [line_down, 0]
    pt6 = [line_down, w]
    pts_L3 = np.array([pt5,pt6], np.int32)
    pts_L3 = pts_L3.reshape((-1,1,2))
    pt7 = [1, 0]
    pt8 = [1, 0]
    pts_L4 = np.array([pt7,pt8], np.int32)
    pts_L4 = pts_L4.reshape((-1,1,2))

    #Create the background subtractor
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    rfmg2 = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

    #Variables
    font = cv2.FONT_HERSHEY_SIMPLEX
    vehicles = []
    max_p_age = 5
    pid = 1

    while(cap.isOpened()):
        #read a frame
        ret, frame = cap.read()
        
        # If de matar o frame
        if not ret:
            break;
            
        ###################
        ## PREPROCESSING ##
        ###################
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Gray - Original", gray_image)
        mask = preProc(gray_image, 11, rfmg2)
        
        ##################
        ## FIND CONTOUR ##
        ##################
        _, contours0, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

        for cnt in contours0:
            cv2.drawContours(mask, cnt, -1, (0, 255, 0), 3, 8)

            area = cv2.contourArea(cnt) #Calcula a área de contorno
            if area > areaTH and area < 20000:
                ################
                #   TRACKING   #
                ################
                M = cv2.moments(cnt) # Calcula os momentos do array
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                x,y,w,h = cv2.boundingRect(cnt)

                new = True
                for i in vehicles:
                    if abs(x - i.x) <= w and abs(y - i.y) <= h:
                        new = False
                        i.updateCoords(cx,cy)
                        
                        if i.going_DOWN(line_down, line_up):
                            #print("A LARGURA EH:",w)
                            if(w > 95):
                                print("CARRO GRANDE MAH")
                                cnt_grande +=1
                            elif(w<70):
                                print("MOTINHA MAH")
                                cnt_pequeno +=1
                            else:
                                print("CARRO MEDIO MAH")
                                cnt_medio +=1
                      
                            roi = mask[y:y+h, x:x+w]
                            cv2.imshow('Region of Interest', roi)

                            cnt_down += 1
                        break

                    if i.state == '1':
                        if i.dir == 'down' and i.y > down_limit:
                            i.setDone()
                        elif i.dir == 'up' and i.y < up_limit:
                            i.setDone()

                    if i.timedOut():
                        # Remove from the list person
                        index = vehicles.index(i)
                        vehicles.pop(index)
                        del i

                if new == True:
                    p = Vehicle.MyVehicle(pid,cx,cy, max_p_age)
                    vehicles.append(p)
                    pid += 1

                ##################
                ##   DRAWING    ##
                ##################
                cv2.circle(gray_image,(cx,cy), 5, (0,0,255), -1)
                img = cv2.rectangle(gray_image, (x,y), (x+w,y+h), (0,255,0), 2)
                #cv2.drawContours(frame, cnt, -1, (0,255,0), 3)
                #cv2.imshow('Image', cv2.resize(img, (400, 300)))

        ###############
        ##   IMAGE   ##
        ###############
        str_up = 'direita: ' + str(cnt_down)
        str_down = 'pequeno:' + str(cnt_pequeno)
        str_medio = 'medio:' + str(cnt_medio)
        str_grande = 'grande:' + str(cnt_grande)
        
        frame = cv2.polylines(gray_image, [pts_L1], False, line_down_color, thickness=2)
        frame = cv2.polylines(gray_image, [pts_L2], False, line_up_color, thickness=2)
        frame = cv2.polylines(gray_image, [pts_L3], False, (255,255,255), thickness=1)
        frame = cv2.polylines(gray_image, [pts_L4], False, (255,255,255), thickness=1)
        
        cv2.putText(frame, str_up, (10,30),font,1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(frame, str_up, (10,30),font,1,(0,0,255),1,cv2.LINE_AA)
        cv2.putText(frame, str_down, (10,55),font,1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(frame, str_down, (10,55),font,1,(0,0,255),1,cv2.LINE_AA)
        cv2.putText(frame, str_medio, (10,80),font,1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(frame, str_medio, (10,80),font,1,(0,0,255),1,cv2.LINE_AA)
        cv2.putText(frame, str_grande, (10,105),font,1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(frame, str_grande, (10,105),font,1,(0,0,255),1,cv2.LINE_AA)
        cv2.imshow('Frame', cv2.resize(gray_image, (400, 300)))

        #Abort and exit with 'Q' or ESC
        k = cv2.waitKey(10) & 0xff
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

main()