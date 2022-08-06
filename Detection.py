from os import stat
from re import search
from sys import setswitchinterval
from PIL import Image
from cv2 import imshow, rectangle
import cv2 as cv #OpenCV uses BGR format
import numpy as np
import pyautogui as pag #screenshot is in RGB format
from time import time, sleep
import win32gui
import hsvfilter
import vision

import pytesseract #uses RGB format
from threading import Thread, Lock
from math import e, sqrt

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    


class Detection:
    screenshot = None
    lower_limit = np.array([60,50,50])
    upper_limit = np.array([60,255,255])
    line_color = (0, 255, 0)
    line_type = cv.LINE_4
    loop_time = time()
    originalpos = None
    tess_word = 'Attack'
    stopped = False 
    rectangles = None
    max_rectangle = None
    state = None
    base_health = '3'
    enemy_health = None
    screenshot_with_boxed_words = None
    
    
    
    
    
    def __init__(self):
        
        self.lock = Lock()
        self.state = Bot.SEARCHING


    def detect_color(self,screen_image):
        
        mask = cv.inRange(screen_image, self.lower_limit, self.upper_limit)
        bitwise_res = cv.bitwise_and(screen_image, screen_image, mask=mask) 
        contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if contours:
            rectangles = np.vstack(contours).squeeze()
            rectangles = cv.boundingRect(rectangles)
            max_rectangle = max(contours, key=cv.contourArea)
            max_rectangle = cv.boundingRect(max_rectangle)
            #print(f'{max_rectangle} max rectangle')
            return max_rectangle, rectangles
        else:
            self.detect_color(screen_image)
            #contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            #rectangles = np.vstack(contours).squeeze()
            #rectangles = cv.boundingRect(rectangles)
            #max_rectangle = max(contours, key=cv.contourArea)
            #max_rectangle = cv.boundingRect(max_rectangle)
            #print(f'{max_rectangle} + 1')
            #return max_rectangle, rectangles
            
        
    
    
    def get_screenshotHSV(self):
        
        screenshot = pag.screenshot()
        screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2HSV)
        return screenshot     
    def get_screenshotBGR(self):
        screenshot = pag.screenshot()
        screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2BGR)
        return screenshot
    def get_screenshotRGB(self):
        screenshot = pag.screenshot()
        return screenshot
    
    
    
    class Runelite_coords:
        top_left = (0,0)
        bottom_right = (1185,1015)
        size = (bottom_right[0] - top_left[0], bottom_right[1] - top_left[1] )
        
        
    class Enemy_hp_coords:
        #Runelite
        top_left = (30, 75)
        bottom_right =(150, 130)
       
        #image
        #top_left = (15,190)
        #bottom_right = (140,227)
        size = (bottom_right[0] - top_left[0], bottom_right[1] - top_left[1] )
    class Enemy_hp_coords_zoomed:
        #Runelite
        #top_left = (30, 75)
        #bottom_right =(150, 130)
        top_left = (85,105)
        bottom_right =(130, 125)
        #image
        #top_left = (15,190)
        #bottom_right = (140,227)
        size = (bottom_right[0] - top_left[0], bottom_right[1] - top_left[1] )
    
    
    class HP_coords:
        top_left = (830,570)    
        bottom_right = (860,625)
        size = (bottom_right[0] - top_left[0], bottom_right[1] - top_left[1] )
    
    class Inventory_coords:
        top_left = (860,560)
        bottom_right = (1145,955)
        size = (bottom_right[0] - top_left[0], bottom_right[1] - top_left[1] )
        
    def get_runelite_screenshot_hsv(self):
        region = (self.Runelite_coords.top_left[0],self.Runelite_coords.top_left[1],self.Runelite_coords.size[0],self.Runelite_coords.size[1])
        screenshot = pag.screenshot(region = region)
        screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2HSV)
        return screenshot
        
    def get_enemy_hp_screenshot(self):
       
        region = (self.Enemy_hp_coords.top_left[0],self.Enemy_hp_coords.top_left[1],self.Enemy_hp_coords.size[0]+10,self.Enemy_hp_coords.size[1]+10)
        screenshot = pag.screenshot(region = region)
        screenshot = np.array(screenshot)
        return screenshot
    def get_enemy_hp_screenshot_zoomed(self):
       
        region = (self.Enemy_hp_coords_zoomed.top_left[0],self.Enemy_hp_coords_zoomed.top_left[1],self.Enemy_hp_coords_zoomed.size[0]+10,self.Enemy_hp_coords_zoomed.size[1]+10)
        screenshot = pag.screenshot(region = region)
        screenshot = np.array(screenshot)
        return screenshot
    
    def get_hp_screenshot(self):
        x = 0
        region = (self.HP_coords.top_left[0]+ x,self.HP_coords.top_left[1]+ x,self.HP_coords.size[0]+ x,self.HP_coords.size[1]+ x)
        screenshot = pag.screenshot(region = region)
        screenshot = np.array(screenshot)
        return screenshot
    
    def get_inventory_screenshot(self):
        x = 0
        region = (self.Inventory_coords.top_left[0]+ x,self.Inventory_coords.top_left[1]+ x,self.Inventory_coords.size[0]+ x,self.Inventory_coords.size[1]+ x)
        screenshot = pag.screenshot(region = region)
        screenshot = np.array(screenshot)
        return screenshot
    
    
    def what_is_tess_word(self,img):
        
        #img = Image.open('attacktooltipdead.png')
        #x,y,w,h = self.Enemy_hp_coords.top_left[0],self.Enemy_hp_coords.top_left[1],self.Enemy_hp_coords.size[0],self.Enemy_hp_coords.size[1]
        #img = img.crop((x,y,x+w,y+h))
        #img = self.get_enemy_hp_screenshot()
        #img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        data = pytesseract.image_to_data(img)
        for x,b in enumerate(data.splitlines()):
            if x!=0:
                b = b.split()
                if (len(b)>11):
                    #print(b)
                    return b[11]
                    """
                
                    b = b[11].split('/')
                    #print(b)
                    if len(b)>1:
                        b = b[0]
                        if b == '0' or b == 'o':
                            return b
                    """
                    
                            
    
    

    def draw_box(self,screen_image,rectangles):
        
        x, y, w, h = rectangles
        top_left = (x, y)
        bottom_right = (x + w, y + h)
        
        rect = cv.rectangle(screen_image, top_left, bottom_right, self.line_color, lineType=self.line_type)
        return rect
        

    def click_box(self,rectangles,screenshot):
        click_word = None
        originalpos = pag.position()
        
        #x, y, w, h = rectangles
        pag.moveTo(rectangles)
        #pag.rightClick()
        sleep(0.5)
        pag.moveRel(0, 45)
        #pag.click()
        sleep(2)
        
        """
        click_word = self.verify_text(screenshot,self.tess_word)
        if not click_word:
            print("{} not found, trying again".format(self.tess_word))
            click_word = self.verify_text(screenshot,self.tess_word)
        if click_word:
            pag.moveTo(click_word)
            pag.click()
        """
            
                
            
        
    def verify_text(self,img,tess_word):
        

        boxes = pytesseract.image_to_data(img)

        for x,b in enumerate(boxes.splitlines()):
            if x!=0:
                b =b.split()
                #print(len(b))
                
                if (len(b) > 11 and b[11] == tess_word):
                    #print(b)
                    x,y,w,h,word = int(b[6]),int(b[7]),int(b[8]),int(b[9]),b[11]
                    click_word = (x + w/2, y + h/2)
                    print("found {} at {}".format(self.tess_word,click_word))
                    
                    return click_word
                
    def move_back(originalpos):
        pag.moveTo(originalpos)

    def enemy_hp_to_boxes(self,img):
        h, w, _ = img.shape # assumes color image
        # run tesseract, returning the bounding boxes
        boxes = pytesseract.image_to_boxes(img) # also include any config options you use
        # draw the bounding boxes on the image
        #print(boxes)
        for b in boxes.splitlines():
            b = b.split(' ')

            img = cv.rectangle(img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (0, 255, 0), 2)
            img = cv.putText(img, b[0], (int(b[1]), h - int(b[2])), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
        return img, boxes

    def get_enemy_health(self):
        width,height = 200,150
        enemy_health =0
        while True:
            screenshot = self.get_enemy_hp_screenshot_zoomed()
            screenshot = cv.resize(screenshot,(width,height))
        
            screenshot_with_boxed_words,b = self.enemy_hp_to_boxes(screenshot)
        
        
            for i in b.splitlines():
                i = i.split(' ')
                a = i[0]
                if a.isdigit() and a[0] < self.base_health:
                    enemy_health = a
            return enemy_health,screenshot_with_boxed_words

    def update_runeliteScreenshot(self):
        while True:
            screenshot = self.get_runelite_screenshot_hsv()
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()

    def runvScreenshot(self):

        while True:

            screenshot = self.get_screenshotHSV()
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()

    def runDetection(self):
        while True:
            self.lock.acquire()
            screenshot = self.screenshot
            self.lock.release()
            if screenshot is not None:
                rectangles,_ = self.detect_color(screenshot)
                self.lock.acquire()
                self.rectangles = rectangles
                self.lock.release()
    
    def update_enemy_health(self):
        while True:
            enemy_health,screenshot_with_boxed_words = self.get_enemy_health()
            self.lock.acquire()
            self.enemy_health = enemy_health
            self.screenshot_with_boxed_words = screenshot_with_boxed_words
            self.lock.release()
            
            
            #print(f'enemy health is {self.enemy_health} out of {self.base_health}')

   

    def start_threads(self):
        threadslist = []
        threadslist.append(Thread(target=self.update_runeliteScreenshot, args=()))
        threadslist.append(Thread(target=self.runDetection, args=()))
        threadslist.append(Thread(target=self.update_enemy_health, args=()))
        
        for thread in threadslist:
            thread.start()





class Bot:
    SEARCHING = 0
    CLICKING = 1
    ATTACK = 2
    ATTACKING = 3
    HEALING = 4

def bot():
    detect = Detection()
    detect.start_threads()

    


def main():
    detect = Detection()
    detect.start_threads()
    screenshot = None
    point = None
    enemy_health = None
    time = 0

    detect.state = Bot.SEARCHING

    
    
    while True:
        a = detect.get_enemy_hp_screenshot()
        ab = detect.what_is_tess_word(a)
        if enemy_health == 0:
            enemy_health = None
        
        if detect.state == Bot.SEARCHING:
            detect.lock.acquire()
            screenshot = detect.screenshot
            point,_ = detect.detect_color(screenshot)
            enemy_health = detect.enemy_health
            detect.lock.release()

            if point and screenshot is not None:
                detect.lock.acquire()
                detect.state = Bot.CLICKING
                detect.lock.release()
                
            

            

            print("searching")
            

        elif detect.state == Bot.CLICKING:
            
            print("clicking")
            
            if point:
                detect.click_box(point,screenshot)
                sleep(time)
                detect.lock.acquire()
                detect.state = Bot.ATTACK
                detect.lock.release()
                
                print("set to attack")
                sleep(time)
                
            else:
                print("no point")
                
                
        #need to work on getting this to recognise when i enter combat
        elif detect.state == Bot.ATTACK:
            print(f'attack now')
            if enemy_health is not None:

                if int(enemy_health) > 0:
                    detect.lock.acquire()
                    detect.state = Bot.ATTACKING
                    detect.lock.release()
                else:
                    detect.lock.acquire()
                    detect.state = Bot.SEARCHING
                    detect.lock.release()
            
                
        elif detect.state == Bot.ATTACKING:
            print(f'attacking now')
            if int(enemy_health) > 0:
                sleep(.5)
                detect.lock.acquire()
                detect.state = Bot.ATTACKING
                
                detect.lock.release()
            elif int(enemy_health) == 0:
                detect.lock.acquire()
                detect.state = Bot.SEARCHING
                detect.enemy_health = 0
                detect.lock.release()
    
"""
    enemy_health = None
    enemy_health_T = False
    while True:

        if enemy_health is None:
            print("enemy health is None")
            #print(point)
            detect.lock.acquire()
        
            #screenshot for RS and Detection
            screenshot = detect.get_runelite_screenshot_hsv()
            point,point2 = detect.detect_color(screenshot)
            detect.lock.release()

            if point and screenshot is not None:
                detect.click_box(point,screenshot)
                while enemy_health is None:
                    detect.lock.acquire()
                    enemy_health = detect.enemy_health
                    detect.lock.release()
                    if enemy_health is not None:
                        detect.state = Bot.ATTACK
        elif detect.state == Bot.ATTACK:
            if int(enemy_health) > 0:
                print(f'Enemy health: {enemy_health} out of {detect.base_health}')
                if point:
                    print(f"Found enemy at {point}")



            elif enemy_health == 0:
                enemy_health = None
                detect.state = Bot.SEARCHING
                print('enemy is dead')
"""
    
    
    
  
    



if __name__ == "__main__":
    main()
    cv.namedWindow('screenshot', cv.WINDOW_NORMAL)
    cv.moveWindow('screenshot', name.top_left[0],name.top_left[1])
    cv.resizeWindow('screenshot', name.size[0], name.size[1])
    cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
    cv.imshow('screenshot',screenshot)
    cv.waitKey(0)



    


