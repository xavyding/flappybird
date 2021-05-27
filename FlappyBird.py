
from scripts.main import Game
from scripts.AI_MC_onpolicy import AI, SCALE_FACTOR, ACTION_COOLDOWN


# Qt5
from PyQt5.QtCore import *

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# from PyQt5.QtMultimedia import *

import numpy as np

# from PyQt4.QtCore import *
# from PyQt4.QtGui import *

WINDOW_SIZE_X = 1600
WINDOW_SIZE_Y = 900
OBSTACLE_GAP = 280
OBSTACLE_GAPX = 600
OBSTACLE_WIDTH = 165 

BIRD_X = 300
BIRD_SIZE = 60
BIRD_SIZEX = BIRD_SIZE + 0.3*BIRD_SIZE


class GameScene(QGraphicsScene):
    #setPos --> top left coner
    def __init__(self):
        super().__init__()
        #/ game
        self.G = Game(
            window_size_x = WINDOW_SIZE_X, 
            window_size_y = WINDOW_SIZE_Y, 
            obstacle_gap_x = OBSTACLE_GAPX, 
            obstacle_gap_y = OBSTACLE_GAP, 
            obstacle_width = OBSTACLE_WIDTH, 
            bird_x = BIRD_X, 
            bird_size_x = BIRD_SIZEX, 
            bird_size_y = BIRD_SIZE
        )

        #/ player action
        self.player_action = 0

        #/ config
        self.ai_mode = False
        self.auto_retry = False

        #/ background
        self.setSceneRect(0,0,self.G.window_size_x,self.G.window_size_y)
        # self.setBackgroundBrush(QColor(0,100,230))
        bg = QGraphicsPixmapItem()
        bg.setPixmap(QPixmap('utils/bg.png'))
        self.addItem(bg)

        #/ bird
        self.bo_png = QPixmap('utils/birdo.png').scaled(QSize(self.G.bird_size_x,self.G.bird_size_y))
        self.bx_png = QPixmap('utils/birdx.png').scaled(QSize(self.G.bird_size_x,self.G.bird_size_y))
        self.Bird = self.addPixmap(self.bo_png)
        self.Bird.setPos(self.G.bird_x,self.G.B.pos)
        # self.Bird.setPos(0,0)
        
        
        #/ obstacles
        self.Obstacle_top = []
        self.Obstacle_bot = []
        for i in range(len(self.G.O)):
            self.Obstacle_top.append(self.addPixmap(QPixmap('utils/obs_top.png')))
            self.Obstacle_bot.append(self.addPixmap(QPixmap('utils/obs_bot.png')))
            self.Obstacle_top[i].setPos(self.G.O[i].x + WINDOW_SIZE_X, self.G.O[i].pos - 1000)
            self.Obstacle_bot[i].setPos(self.G.O[i].x + WINDOW_SIZE_X, self.G.O[i].pos + self.G.obstacle_gap_y)


        #/ score
        self.Score = self.addText("")
        self.Score.setFont(QFont ("Helvetica", 20))
        self.Attempt = self.addText("")
        self.Attempt.setFont(QFont ("Helvetica", 20))



        self.RIP = self.addText("PRESS \nENTER \nTO START")
        self.RIP.setFont(QFont ("Helvetica", 150))

        #/ AI
        self.ai = AI()
        try: self.ai.load_data()
        except: pass
        self.cooldown = 0

        # self.d2g = self.G.window_size_y - self.G.bird_size_y - self.G.B.pos
        # self.d2o = self.G.window_size_x
        # self.oh = self.G.O[0].pos + self.G.obstacle_gap_y
        self.d2g = self.G.B.pos
        self.d2o = self.G.O[self.G.IOI].x
        self.oh = self.G.O[self.G.IOI].pos
        # self.ai.set_train_data(self.d2g, self.d2o, self.oh, self.B.vel)
    
    def reset(self):
        #/ Game
        self.G.reset()

        #/ bird
        self.Bird.setPixmap(self.bo_png)
        self.Bird.setPos(self.G.bird_x,self.G.B.pos)
        self.Bird.setRotation(0)

        #/ obstacle
        for i in range(len(self.G.O)):
            self.Obstacle_top[i].setPos(self.G.O[i].x, self.G.O[i].pos - 1000)
            self.Obstacle_bot[i].setPos(self.G.O[i].x, self.G.O[i].pos + self.G.obstacle_gap_y)

        #/ score
        self.Score.setPlainText("Score: " + str(int(self.G.S.point)))
        self.Attempt.setPlainText("Attempt: " + str(int(self.G.S.attempt)))
        self.Score.setPos(20,30)
        self.Attempt.setPos(20,0)
        

        #/ message
        self.RIP.setPlainText("")
        self.RIP.setPos((self.G.window_size_x-450)/2,(self.G.window_size_y-150)/2)

        #/ AI
        if self.ai_mode:
            pass

    def run(self):

        #/ Game
        # self.G.run()
        observer, time, alive, flapped = self.G.run(self.player_action)
        self.player_action = 0
        # print(observer, points, flapped)

        #/ AI
        if self.ai_mode:
            if self.cooldown >= ACTION_COOLDOWN:
                state = [
                    int(observer[0]/SCALE_FACTOR),
                    int(observer[1]*2 + 20),
                    int(observer[2]/SCALE_FACTOR),
                    int(observer[3]/SCALE_FACTOR)
                ]
                self.player_action = self.ai.prediction(state)
                self.cooldown = 0
            else: self.cooldown += 1


        #/ bird     
        self.Bird.setPos(self.G.bird_x,self.G.B.pos)
        self.Bird.setRotation(np.max([0,self.G.B.vel])*2)


        #/ obstacle
        for i in range(len(self.G.O)):
            self.Obstacle_top[i].setPos(self.G.O[i].x, self.G.O[i].pos - 1000)
            self.Obstacle_bot[i].setPos(self.G.O[i].x, self.G.O[i].pos + self.G.obstacle_gap_y)


        #/ score
        self.Score.setPlainText("Score: " + str(int(self.G.S.point)))

        
        #/ check
        if not alive:
            self.timer.stop()
            self.Bird.setPixmap(self.bx_png)
            self.RIP.setPlainText("R.I.P")

            if self.ai_mode:
                None

            if self.auto_retry:
                self.reset()
                self.timer = QTimer()
                self.timer.timeout.connect(self.run)
                self.timer.start(10)
    
    def AiEvent(self):
        pass

    
    def keyPressEvent(self, event):
        touche = event.key()

        #/ flap
        if touche == Qt.Key_Space:
            # self.G.event()
            self.player_action = 1

        #/ start/restart
        if touche == Qt.Key_Enter or touche == Qt.Key_Return:
            self.timer = QTimer()
            self.timer.timeout.connect(self.run)
            self.timer.start(10)
            self.reset()

        if touche == Qt.Key_Backspace:
            self.auto_retry = True
            self.ai_mode = True
            self.timer = QTimer()
            self.timer.timeout.connect(self.run)
            self.timer.start(10)
            self.reset()
        
        # if touche == Qt.Key_Escape:
        #     self.__init__()

























##############################################################################
class GameView(QGraphicsView):
    def __init__(self):
        super(GameView,self).__init__()
        scene = GameScene()
        self.setScene(scene)
        


class UI(QMainWindow):
    def __init__(self):
        super(UI,self).__init__()
        self.game = GameView()
        self.setWindowTitle("FlappyBird Y") 

        mainwidget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.game)
        mainwidget.setLayout(layout)
        self.setCentralWidget(mainwidget)
        self.setFixedSize(WINDOW_SIZE_X+20,WINDOW_SIZE_Y+20)


if __name__ == '__main__' :
    import sys
    app = QApplication(sys.argv)
    mainwindow = UI()
    # mainwindow.showFullScreen()
    mainwindow.show()
    app.exec()









