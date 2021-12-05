import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from .Ui_files.Ui_mainWindow import Ui_mainWindow

from pygame import mixer
import playsound
import cv2
import random

HURT_SOUND = 'UI/sound/hurt.wav'
BGM_PATH = 'UI/sound/bgm.mp3'
MAIN_CHARACTER_IMAGE = cv2.imread('UI/images/mainCharacter.jpg')
NINJA_IMAGE = cv2.imread('UI/images/ninja.png')
DISAPPEAR_IMAGE = cv2.imread('UI/images/disappear.png')

MOVING_TRIGGER = 200
TELEPORT_TRIGGER = 2000
RESPAWN_TIME_INIT = 1000
RESPAWN_TIME_MIN = 200
TIME_AMOUNT = 10
MOVE_AMOUNT = 20
NINJA_MAX = 200
DETECTED_DISTANCE = 50
EDGE_DISTANCE = 60
DAMAGE = 5

class MainPage(QMainWindow,Ui_mainWindow):
    """
    Main Page
    """
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
        """
        intializing all setting
        """
        self.ninja = []
        self.ninjaCount = 0
        self.aliveTime = 0
        self.respawnTime = RESPAWN_TIME_INIT

        self.aliveTimer = QTimer(timeout=self.aliveTimeCount)
        self.aliveTimer.start(1000)
        self.movingTimer = QTimer(timeout=self.randomMoving)
        self.movingTimer.start(MOVING_TRIGGER)
        self.teleportTimer = QTimer(timeout=self.randomTeleport)
        self.teleportTimer.start(TELEPORT_TRIGGER)
        self.respawnTimer = QTimer(timeout=self.respawnNinja)
        self.respawnTimer.start(self.respawnTime)

    def imageToPixmap(self,image):
        """
        covert image to PyQt Pixmap
        """
        convertedImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = convertedImage.shape[:2]
        return QPixmap.fromImage(QImage(convertedImage, width, height, QImage.Format_RGB888))

    def createMainCharacter(self):
        """
        create main character
        """
        self.mainCharacterLabel.setScaledContents(True)
        self.mainCharacterLabel.setPixmap(self.imageToPixmap(MAIN_CHARACTER_IMAGE))
    
    def respawnNinja(self):
        """
        respawn ninja check and change configuration
        """
        if self.ninjaCount < NINJA_MAX:
            if self.respawnTime > RESPAWN_TIME_MIN :
                self.respawnTime -= TIME_AMOUNT
            self.ninjaCount += 1
            self.createNinja()
    
    def generateRandomXY(self):
        """
        generate random x,y points
        """
        x = random.randint(0,self.width()-EDGE_DISTANCE)
        y = random.randint(0,self.height()-EDGE_DISTANCE)
        return x,y

    def createNinja(self):
        """
        create a new ninjaLabel and set pixmap
        """
        x,y = self.generateRandomXY()
        self.ninja.append(QLabel(self.centralwidget))
        self.ninja[self.ninjaCount-1].setScaledContents(True)
        self.ninja[self.ninjaCount-1].setGeometry(QRect(x,y,60,60))
        self.ninja[self.ninjaCount-1].setPixmap(self.imageToPixmap(NINJA_IMAGE))
        self.ninja[self.ninjaCount-1].show()
        self.respawnTimer.start(self.respawnTime)

    def playBGM(self):
        """
        play BGM
        """
        mixer.init()
        mixer.music.load(BGM_PATH)
        mixer.music.play(-1)

    def aliveTimeCount(self):
        """
        counting alive time
        """
        self.aliveTime += 1
        self.noticeLabel.setText('存活時間(s): '+str(self.aliveTime)+' 忍者數量: '+str(self.ninjaCount)+' 重生時間(ms): '+str(self.respawnTime))

    def approaching(self,mover,target):
        """
        mover approaching target
        """
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
        """
        change health bar value and check health value
        """
        self.callHurtSound()
        self.healthBar.setValue(self.healthBar.value() - DAMAGE)
        if self.healthBar.value() <= 0:
            self.aliveTimer.stop()
            self.respawnTimer.stop()
            self.movingTimer.stop()
            self.teleportTimer.stop()
            self.gameOver()
    
    def callHurtSound(self):
        """
        hurt sound thread called
        """
        hurtSound_thread = hurtSound_Thread(self)
        hurtSound_thread.start()

    def gameOver(self):
        """
        game over
        """
        QMessageBox(icon=QMessageBox.Information,
                    windowTitle='Game Over',
                    text='你存活了{}秒喔~'.format(self.aliveTime)).exec_()
        sys.exit()
            
    def randomMoving(self):
        """
        pick random ninja moving
        """
        randomMover = random.randint(0,self.ninjaCount)
        for _ in range(randomMover):
            index = random.randint(0,self.ninjaCount-1)
            #self.ninja[index].setPixmap(self.imageToPixmap(NINJA_IMAGE))
            self.approaching(self.ninja[index],self.mainCharacterLabel)
    
    def randomTeleport(self):
        randomTeleporter = random.randint(0,int(self.ninjaCount/5))
        for index in range(randomTeleporter):
            x,y = self.generateRandomXY()
            self.ninja[index].move(x,y)
            # self.disappear_Thread = disappear_Thread(self,self.ninja[index])
            # self.disappear_Thread.start()
            

    def keyPressEvent(self,event):
        """
        key press event
        """
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
    

    def keyReleaseEvent(self,event):
        self.keyPressEvent(event)


# -----------------------------------------------Threading-----------------------------------------------

class hurtSound_Thread(QThread):
    """
    hurt sound thread
    """
    def __init__(self,parent):
        super().__init__(parent)
        self.hurtSound = HURT_SOUND
    
    def run(self):
        playsound.playsound(self.hurtSound)


class disappear_Thread(QThread):
    """
    main characacter attack thread(unfinished)
    """
    def __init__(self,parent,ninja):
        super().__init__(parent)
        self.mainWindow = parent
        self.ninja = ninja
    
    def run(self) -> None:
        self.ninja.setPixmap(self.loadImage())
        self.ninja.setEnabled(False)

    def loadImage(self):
        return self.mainWindow.imageToPixmap(DISAPPEAR_IMAGE)
    