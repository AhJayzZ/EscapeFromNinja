import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from .Ui_files.Ui_mainWindow import Ui_mainWindow

from vlc import Instance
import playsound
import cv2
import random

HURT_SOUND = 'UI/sound/hurt.wav'
BGM_PATH = 'UI/sound/bgm.mp3'
MAIN_CHARACTER_IMAGE = cv2.imread('UI/images/mainCharacter.jpg')
NINJA_IMAGE = cv2.imread('UI/images/ninja.png')

MOVING_TRIGGER = 300
RESPAWN_TIME_INIT = 1000
RESPAWN_TIME_MIN = 200
TIME_AMOUNT = 10
MOVE_AMOUNT = 20
NINJA_MAX = 300
DETECTED_DISTANCE = 60
EDGE_DISTANCE = 60
DAMAGE = 5

class MainPage(QMainWindow,Ui_mainWindow):
    def __init__(self):
        super(MainPage,self).__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowTitle('Escape From Ninja')
        self.setWindowIcon(QIcon('UI/images/title_icon.png'))
        self.setStyleSheet("background-color:black")
        self.initialize()
        self.createMainCharacter()
        self.playBGM()

    def initialize(self):
        self.ninja = []
        self.ninjaCount = 0
        self.aliveTime = 0
        self.respawnTime = RESPAWN_TIME_INIT

        self.aliveTimer = QTimer(timeout=self.aliveTimeCount)
        self.aliveTimer.start(1000)
        self.movingTimer = QTimer(timeout=self.randomMoving)
        self.movingTimer.start(MOVING_TRIGGER)
        self.respawnTimer = QTimer(timeout=self.respawnNinja)
        self.respawnTimer.start(self.respawnTime)

    def imageToPixmap(self,image):
        convertedImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = convertedImage.shape[:2]
        return QPixmap.fromImage(QImage(convertedImage, width, height, QImage.Format_RGB888))

    def createMainCharacter(self):
        self.mainCharacterLabel.setScaledContents(True)
        self.mainCharacterLabel.setPixmap(self.imageToPixmap(MAIN_CHARACTER_IMAGE))
    
    def respawnNinja(self):
        if self.ninjaCount < NINJA_MAX:
            if self.respawnTime > RESPAWN_TIME_MIN :
                self.respawnTime -= TIME_AMOUNT
            self.ninjaCount += 1
            self.createNinja()

    def createNinja(self):
        x = random.randint(0,self.width()-EDGE_DISTANCE)
        y = random.randint(0,self.height()-EDGE_DISTANCE)
        self.ninja.append(QLabel(self.centralwidget))
        self.ninja[self.ninjaCount-1].setScaledContents(True)
        self.ninja[self.ninjaCount-1].setGeometry(QRect(x,y,60,60))
        self.ninja[self.ninjaCount-1].setPixmap(self.imageToPixmap(NINJA_IMAGE))
        self.ninja[self.ninjaCount-1].show()
        self.respawnTimer.start(self.respawnTime)

    def playBGM(self):
        playInstance = Instance('--loop')
        self.player = playInstance.media_player_new()
        self.player.set_media(playInstance.media_new(BGM_PATH))
        self.player.play()

    def aliveTimeCount(self):
        self.aliveTime += 1
        self.noticeLabel.setText('存活時間(s): '+str(self.aliveTime)+' 忍者數量: '+str(self.ninjaCount)+' 重生時間(ms): '+str(self.respawnTime))

    def approaching(self,mover,target):
        moverPos = mover.pos()
        targetPos = target.pos()
        if moverPos.x() <= targetPos.x():
            mover.move(mover.pos().x()+MOVE_AMOUNT,mover.pos().y())
        if moverPos.x() >= targetPos.x():
            mover.move(mover.pos().x()-MOVE_AMOUNT,mover.pos().y())
        if moverPos.y() <= targetPos.y():
            mover.move(mover.pos().x(),mover.pos().y()+MOVE_AMOUNT)
        if moverPos.y() >= targetPos.y():
            mover.move(mover.pos().x(),mover.pos().y()-MOVE_AMOUNT)

        if (abs(moverPos.x() - targetPos.x()) < DETECTED_DISTANCE and 
            abs(moverPos.y() - targetPos.y()) < DETECTED_DISTANCE):
            self.minusHP()

    def minusHP(self):
        self.healthBar.setValue(self.healthBar.value() - DAMAGE)
        playsound.playsound(HURT_SOUND)
        if self.healthBar.value() == 0:
            self.respawnTimer.stop()
            self.movingTimer.stop()
            QMessageBox(icon=QMessageBox.Information,
                            windowTitle='Game Over',
                            text='Game Over 重來吧~').exec_()
        sys.exit
    

    def randomMoving(self):
        self.randomMover = random.randint(0,NINJA_MAX-1)
        for index in range(self.randomMover):
            try:
                self.approaching(self.ninja[index],self.mainCharacterLabel)
            except:
                pass

    def keyPressEvent(self,event):
        pos = self.mainCharacterLabel.pos()
        # Up
        if ((event.key() == Qt.Key_Up or event.key() == Qt.Key_W) and 
            (pos.y() - MOVE_AMOUNT > 0)) :
            self.mainCharacterLabel.move(pos.x(),pos.y()-MOVE_AMOUNT)
        # Down
        if ((event.key() == Qt.Key_Down or event.key() == Qt.Key_S) and 
            (pos.y() + MOVE_AMOUNT < self.height()-DETECTED_DISTANCE)):
            self.mainCharacterLabel.move(pos.x(),pos.y()+MOVE_AMOUNT)
        # Left
        if ((event.key() == Qt.Key_Left or event.key() == Qt.Key_A) and 
            (pos.x() - MOVE_AMOUNT > 0)) :
            self.mainCharacterLabel.move(pos.x()-MOVE_AMOUNT,pos.y())
        # Right
        if ((event.key() == Qt.Key_Right or event.key() == Qt.Key_D) and 
            (pos.x() + MOVE_AMOUNT < self.width()-DETECTED_DISTANCE)):
            self.mainCharacterLabel.move(pos.x()+MOVE_AMOUNT,pos.y())