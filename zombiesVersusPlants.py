from cmu_graphics import *
import math
import random
import copy

class Plant:
    def __init__(self, row, col, plantType):
        self.row = row
        self.col = col
        self.type = plantType
        if plantType == 'sunflower':
            self.health = 100
        elif plantType == 'peashooter':
            self.health = 100
        else:
            self.health = 300
        self.maxHealth = self.health

    def isAlive(self):
        return self.health > 0

def onAppStart(app):
    app.mode = 'menu'
    app.width = 900
    app.height = 650
    app.rows = 5
    app.cols = 9
    app.cellWidth = 59
    app.cellHeight = 71
    app.boardLeft = 175
    app.boardTop = 145
    app.boardWidth = app.cols * app.cellWidth
    app.boardHeight = app.rows * app.cellHeight
    app.board = [[None] * app.cols for _ in range(app.rows)]
    app.plants = ['sunflower', 'peashooter', 'wallnut']
    app.plantCount = 0
    app.plantSpawnNum = 60
    app.plantImages = {
        'sunflower': [f'sunFlower/sunFlower_{i:02d}.png' for i in range(36)],
        'peashooter': [f'peaShooter/peaShooter_{i:02d}.png' for i in range(77)],
        'wallnut': [f'wallNut/wallNut_{i:02d}.png' for i in range(44)],
    }
    app.plantImageCount = {
        'sunflower': 36,
        'peashooter': 77,
        'wallnut': 44,
    }
    app.plantImage = 0
    app.paused = False
    app.gameOver = False
    app.showGrid = False


def redrawAll(app):
    if app.mode == 'menu':
        drawImage('menu.jpg', 0, 0, width=app.width, height=app.height)
        drawRect(350, 565, 200, 70, fill='brown', border='black', borderWidth=6)
        drawLabel('Start', 450, 600, size=36, fill='white', bold=True)
        return
    drawImage("garden.jpg", 0, 0)
    drawLabel('Zombies vs Plants', app.width//2, 40, size=40, fill='darkgreen', bold=True)
    drawBoard(app)
    drawPlants(app)
    if app.paused:
        drawRect(0,0,app.width,app.height,fill = "black",opacity = 60)
        drawLabel('Paused', app.width//2, app.height//2, size=50, fill='white', bold=True)

def drawBoard(app):
    if app.showGrid:
        for row in range(app.rows + 1):
            y = app.boardTop + row * app.cellHeight
            drawLine(app.boardLeft, y, app.boardLeft + app.boardWidth, y, fill='darkGreen', lineWidth=1)
        for col in range(app.cols + 1):
            x = app.boardLeft + col * app.cellWidth
            drawLine(x, app.boardTop, x, app.boardTop + app.boardHeight, fill='darkGreen', lineWidth=1)

def drawPlants(app):
    for row in range(app.rows):
        for col in range(app.cols):
            plant = app.board[row][col]
            if plant:
                x = app.boardLeft + col * app.cellWidth + app.cellWidth // 2
                y = app.boardTop + row * app.cellHeight + app.cellHeight // 2
                plantType = plant.type
                imageCount = app.plantImageCount[plantType]
                imageIndex = app.plantImage % imageCount
                imageUrl = app.plantImages[plantType][imageIndex]
                drawImage(imageUrl, x, y, align='center', width=app.cellWidth, height=app.cellHeight)

def onMousePress(app, x, y):
    if app.mode == 'menu':
        if 350 <= x <= 550 and 565 <= y <= 635:
            app.mode = 'game'
            app.paused = False

def onKeyPress(app, key):
    if key == 'p':
        app.paused = not app.paused
    if key == 'r':
        app.mode = 'menu'
        app.paused = False
    if key == 's':
        app.showGrid = not app.showGrid

def spawnPlant(app):
    empty = [(r, c) for r in range(app.rows) for c in range(app.cols) if app.board[r][c] is None]
    if not empty:
        return
    plantWeights = {'sunflower': 0.2, 'peashooter': 0.6, 'wallnut': 0.2}
    plantType = random.choices(list(plantWeights.keys()), weights=list(plantWeights.values()))[0]
    if plantType == 'sunflower':
        valid = [(r, c) for (r, c) in empty if c in (0, 1)]
        if not valid:
            return
        row, col = random.choice(valid)
    elif plantType == 'wallnut':
        valid = []
        for row in range(app.rows):
            for col in range(app.cols):
                if app.board[row][col] is None: 
                    hasPlantBehind = False
                    for checkCol in range(col + 1, app.cols):
                        if app.board[row][checkCol] is not None:
                            hasPlantBehind = True
                            break
                    if hasPlantBehind:
                        valid.append((row, col))
        if not valid:
            return
        row, col = random.choice(valid)
    else:
        row, col = random.choice(empty)
    plant = Plant(row, col, plantType)
    app.board[row][col] = plant

def onStep(app):
    if app.paused or app.mode == 'menu':
        return
    app.plantCount += 1
    if app.plantCount >= app.plantSpawnNum:
        app.plantCount = 0
        spawnPlant(app)
    app.plantImage = (app.plantImage + 1) % max(app.plantImageCount.values())

def main():
    runApp(width=900, height=650)

if __name__ == '__main__':
    main() 