from __future__ import print_function
from __future__ import division
import cv2 as cv
import argparse

contrast_max = 254
brigthness_max = 254
title_window = 'Image Pre-processing transformations'
trackbars_window='Trackbars'

def callback(x):
   apply_brightness_contrast()

def incicciottisci(img, kernelsize=3, shape=cv.MORPH_ELLIPSE):
    kernel=cv.getStructuringElement(shape,(kernelsize,kernelsize))
    opening = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)
    closing = cv.morphologyEx(opening, cv.MORPH_CLOSE, kernel)
    dilation = cv.dilate(opening,kernel,iterations = 1)
    return (255-dilation)

def apply_brightness_contrast():
    # Poi si potranno usare i valori standard di opencv ma provando le cose su GIMP per avere una sorta di continuita' ho trovato una funzione che fa uguale
    brightness=cv.getTrackbarPos(brightness_tb,trackbars_window)-127 # Aggiusto per come visto su GIMP
    contrast=cv.getTrackbarPos(contrast_tb,trackbars_window)-127    # Aggiusto per come visto su GIMP
    invert=cv.getTrackbarPos(invert_tb,trackbars_window)
    threshold=cv.getTrackbarPos(threshold_tb,trackbars_window)
    threshold_active=cv.getTrackbarPos(threshold_on_off,trackbars_window)
    cic=cv.getTrackbarPos(cic_radius,trackbars_window)
    blur=cv.getTrackbarPos(blur_radius,trackbars_window)
    cic_shape=cv.getTrackbarPos(cic_radius,trackbars_window)
    for_tesseract=cv.getTrackbarPos(tesseract_tb,trackbars_window)
    if cic_shape==0:
        shape=cv.MORPH_ELLIPSE
    elif cic_shape==1:
        shape=cv.MORPH_CROSS
    else:
        shape=cv.MORPH_RECT
    if invert and not for_tesseract:    # Tesseract vuole il testo nero su bianco
        input_img=(255-img)
        threshold_type=cv.THRESH_BINARY_INV
    else:
        input_img=img.copy()
        threshold_type=cv.THRESH_BINARY
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow
        
        buf = cv.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()
    
    if contrast != 0:
        f = 131*(contrast + 127)/(127*(131-contrast))
        alpha_c = f
        gamma_c = 127*(1-f)
        
        buf = cv.addWeighted(buf, alpha_c, buf, 0, gamma_c)
    
    if for_tesseract:
        if threshold_active:
            blur_otsu = cv.GaussianBlur(buf,(7,7),0)
            _,buf = cv.threshold(blur_otsu,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
            #buf=cv.adaptiveThreshold(buf,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,17,2)
            #buf=cv.adaptiveThreshold(buf,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,17,2)
        if cic!=0:
            buf=incicciottisci(255-buf,cic*2+1,shape=shape)
        if blur!=0:
            buf= cv.blur(buf,(blur*2+1,blur*2+1))
    else:
        if blur!=0:
            buf= cv.blur(buf,(blur*2+1,blur*2+1))
        if cic!=0:
            if not threshold_active and invert:
                buf=255-incicciottisci(buf,cic*2+1,shape=shape)
            else:
                buf=incicciottisci(255-buf,cic*2+1,shape=shape)
        if threshold_active:
            _,buf=cv.threshold(buf,threshold, 255, threshold_type)
    cv.imshow(title_window,buf)
    

parser = argparse.ArgumentParser(description='Controlling pre-processing in real time')
parser.add_argument('--image', help='Path to the input image.', default='E:/tesiComputerVision/SALF/verifiche_lotto/buoni_jpg/Img5.jpg')
args = parser.parse_args()

## [load]
# Read images ( both have to be of the same size and type )
img = cv.imread(args.image,0)
## [load]
if img is None:
    print('Could not open or find the image: ', args.image)
    exit(0)
#img = cv.equalizeHist(img)
#height, width = img.shape[:2]
#if height==2056 and width==2464:
#    img = cv.resize(img, (821,685))

## [window]
cv.namedWindow(title_window,cv.WINDOW_AUTOSIZE)
cv.namedWindow(trackbars_window,cv.WINDOW_AUTOSIZE)
## [window]

## [create_trackbar]
contrast_tb = 'Contrast'
brightness_tb = 'Brightness'
invert_tb='Invert'
threshold_tb='Threshold'
threshold_on_off='Thr On/Off'
cic_radius='CIC kernel'
cic_shape='CIC shape'
blur_radius='Blur size'
tesseract_tb='Tesseract'
cv.createTrackbar(contrast_tb, trackbars_window , 127, contrast_max, callback)
cv.createTrackbar(brightness_tb, trackbars_window , 127, brigthness_max, callback)
cv.createTrackbar(invert_tb, trackbars_window , 0, 1, callback)
cv.createTrackbar(threshold_tb, trackbars_window , 0, 255, callback)
cv.createTrackbar(threshold_on_off, trackbars_window , 0, 1, callback)
cv.createTrackbar(cic_radius, trackbars_window , 0, 5, callback)
cv.createTrackbar(cic_shape, trackbars_window , 0, 2, callback)
cv.createTrackbar(blur_radius, trackbars_window , 0, 5, callback)
cv.createTrackbar(tesseract_tb, trackbars_window , 0, 1, callback)
## [create_trackbar]

# Show some stuff
apply_brightness_contrast()
# Wait until user press some key
cv.waitKey()