from cmu_graphics import *
import random
import math

class Plant:
    def __init__(self, row, col, health, plant_type):
        self.row = row
        self.col = col
        self.health = health
        self.maxHealth = health
        self.type = plant_type

    def is_alive(self):
        return self.health > 0

class Sunflower(Plant):
    def __init__(self, row, col):
        super().__init__(row, col, 100, 'sunflower')

class Peashooter(Plant):
    def __init__(self, row, col):
        super().__init__(row, col, 100, 'peashooter')

class Wallnut(Plant):
    def __init__(self, row, col):
        super().__init__(row, col, 300, 'wallnut')

class Zombie:
    def __init__(self, x, y, row, health, speed, zombie_type):
        self.x = x
        self.y = y
        self.row = row
        self.health = health
        self.maxHealth = health
        self.speed = speed
        self.state = 'walking'
        self.type = zombie_type

    def is_alive(self):
        return self.health > 0

class NormalZombie(Zombie):
    def __init__(self, x, y, row):
        super().__init__(x, y, row, 100, 0.5, 'zombie')

class GiantZombie(Zombie):
    def __init__(self, x, y, row):
        super().__init__(x, y, row, 400, 0.25, 'giantZombie')

def onAppStart(app):
    app.mode = 'menu'
    app.width = 900
    app.height = 650
    app.gameOver = False
    app.victory = False
    app.paused = False
    app.score = 0
    app.zombiePoints = 100
    app.zombiePointTimer = 0
    app.zombiePointRate = 30
    app.wave = 1
    app.rows = 5
    app.cols = 9
    app.cellWidth = 59
    app.cellHeight = 71
    app.boardLeft = 175
    app.boardTop = 145
    app.boardWidth = app.cols * app.cellWidth
    app.boardHeight = app.rows * app.cellHeight
    app.board = [[None] * app.cols for _ in range(app.rows)]
    app.plants = {'sunflower': Sunflower, 'peashooter': Peashooter, 'wallnut': Wallnut}
    app.bullets = []
    app.zombies = []
    app.suns = []
    app.plantSpawnTimer = 0
    app.plantSpawnRate = 60
    app.zombieTypes = ['zombie', 'giantZombie']
    app.zombieType = 'zombie'
    app.zombieCostDict = {'zombie': 50, 'giantZombie': 150}
    app.zombieTimer = 0
    app.zombieSpawnRate = 99999
    app.sunTimer = 0
    app.sunSpawnRate = 99999
    app.plantAttackTimer = 0
    app.plantAttackRate = 50
    app.showGrid = False
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
    app.stepsPerSecond = 30
    app.plantImage = 0
    app.zombieWalkingImages = [f'zombieWalking/zombieWalking_{i:02d}.png' for i in range(46)]
    app.zombieEatingImages = [f'zombieEating/zombieEating_{i:02d}.png' for i in range(40)]
    app.zombieWalkingImage = 0
    app.zombieEatingImage = 0
    app.giantZombieWalkingImages = [f'giantZombieWalking/giantZombie_{i:03d}.png' for i in range(161)]
    app.giantZombieEatingImages = [f'giantZombieEating/giantZombie_{i:02d}.png' for i in range(38)]
    app.giantZombieWalkingImage = 0
    app.giantZombieEatingImage = 0

def redrawAll(app):
    if getattr(app, 'mode', 'game') == 'menu':
        drawImage('menu.jpg', 0, 0, width=app.width, height=app.height)
        drawRect(350, 565, 200, 70, fill='brown', border='black', borderWidth=6)
        drawLabel('Start', 450, 600, size=36, fill='white', bold=True)
        return
    drawLabel('Zombies vs Plants', app.width//2, 40, size=40, fill='darkgreen', bold=True)
    drawImage("garden.jpg", 0, 0)
    drawZombieSelector(app)
    informationY = 580
    drawLabel(f'Score: {app.score}', app.width//2-200, informationY, size=20, fill='black',bold=True)
    drawLabel(f'Zombie Points: {app.zombiePoints}', app.width//2, informationY, size=20, fill='black',bold=True)
    drawLabel(f'Wave: {app.wave}', app.width//2+200, informationY, size=20, fill='black',bold=True)
    drawBoard(app)
    drawPlants(app)
    drawBullets(app)
    drawZombies(app)
    if app.paused:
        drawRect(0,0,app.width,app.height,fill = "black",opacity = 60)
        drawLabel('Paused', app.width//2, app.height//2, size=50, fill='white', bold=True)
    if app.gameOver:
        drawGameOverMessage(app, victory=app.victory)

def drawZombieSelector(app):
    selectorWidth = 300
    selectorHeight = 100
    selectorLeft = (app.width - selectorWidth) // 2
    selectorTop = app.boardTop + app.boardHeight + 10
    drawRect(selectorLeft, selectorTop, selectorWidth, selectorHeight, fill='brown', border='black', borderWidth=2, opacity=75)
    zombies = app.zombieTypes
    for i, ztype in enumerate(zombies):
        x = selectorLeft + 50 + i * 120
        y = selectorTop + 20
        color = 'yellow' if app.zombieType == ztype else None
        if ztype == 'zombie':
            thumb = app.zombieWalkingImages[0]
        else:
            thumb = app.giantZombieWalkingImages[0]
        drawImage(thumb, x + 15, y + 15, align='center', width=50, height=50)
        drawRect(x - 5, y - 5, 50, 50, border=color, borderWidth=3, fill=None)
        drawLabel(ztype, x + 15, y + 65, size=14, fill='black')
        drawLabel(f'${app.zombieCostDict[ztype]}', x + 15, y + 85, size=12, fill='black')

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
                frameCount = app.plantImageCount[plantType]
                frameIndex = app.plantImage % frameCount
                imageUrl = app.plantImages[plantType][frameIndex]
                drawImage(imageUrl, x, y, align='center', width=app.cellWidth, height=app.cellHeight)
                healthPercent = plant.health / plant.maxHealth
                drawRect(x - 30, y - 40, 60 * healthPercent, 7, fill='red')
                drawRect(x - 30, y - 40, 60, 7, fill=None, border='black')

def drawBullets(app):
    for bullet in app.bullets:
        drawImage('pea.webp',bullet['x'],bullet['y'], align = 'center',width = 20,height = 20)

def drawZombies(app):
    for zombie in app.zombies:
        x, y = zombie.x, zombie.y
        ztype = getattr(zombie, 'type', 'zombie')
        if ztype == 'giantZombie':
            if zombie.state == 'walking':
                frame = app.giantZombieWalkingImages[app.giantZombieWalkingImage % len(app.giantZombieWalkingImages)]
                drawImage(frame, x, y - 20, align='center', width=app.cellWidth + 120, height=app.cellHeight + 100)
            else:
                frame = app.giantZombieEatingImages[app.giantZombieEatingImage % len(app.giantZombieEatingImages)]
                drawImage(frame, x, y - 50, align='center', width=app.cellWidth + 140, height=app.cellHeight + 120)
        else:
            if zombie.state == 'walking':
                frame = app.zombieWalkingImages[app.zombieWalkingImage]
                drawImage(frame, x, y, align='center', width=app.cellWidth + 60, height=app.cellHeight + 20)
            else:
                frame = app.zombieEatingImages[app.zombieEatingImage]
                drawImage(frame, x, y, align='center', width=app.cellWidth, height=app.cellHeight)
        healthPercent = zombie.health / zombie.maxHealth
        drawRect(x - 25, y - 55, 50 * healthPercent, 7, fill='red')
        drawRect(x - 25, y - 55, 50, 7, fill=None, border='black')

def drawGameOverMessage(app, victory=False):
    drawRect(0, 0, app.width, app.height, fill='white', opacity=80)
    if victory:
        drawLabel('You Win!', app.width//2, app.height//2-30, size=40, bold=True, fill='green')
    else:
        drawLabel('You Lose!', app.width//2, app.height//2-30, size=40, bold=True, fill='red')
    drawLabel(f'Final Score: {app.score}', app.width//2, app.height//2+10, size=28, fill='black')
    drawLabel('Press R to Restart', app.width//2, app.height//2+50, size=20, fill='black')

def onMousePress(app, x, y):
    if getattr(app, 'mode', 'game') == 'menu':
        if 350 <= x <= 550 and 565 <= y <= 635:
            app.mode = 'game'
            resetGame(app)
        return
    selectorWidth = 300
    selectorHeight = 100
    selectorLeft = (app.width - selectorWidth) // 2
    selectorTop = app.boardTop + app.boardHeight + 10
    if selectorLeft <= x <= selectorLeft+selectorWidth and selectorTop <= y <= selectorTop+selectorHeight:
        zIndex = (x - selectorLeft - 50) // 120
        zombies = app.zombieTypes
        if 0 <= zIndex < len(zombies):
            app.zombieType = zombies[zIndex]
        return
    if app.gameOver:
        return
    if app.paused:
        return
    right_col_x = app.boardLeft + app.boardWidth
    if x > right_col_x and app.boardTop <= y < app.boardTop + app.boardHeight:
        row = int((y - app.boardTop) // app.cellHeight)
        col = app.cols - 1
        if 0 <= row < app.rows:
            ztype = app.zombieType
            zcost = app.zombieCostDict.get(ztype, 50)
            if app.zombiePoints >= zcost:
                zx = app.boardLeft + col * app.cellWidth + app.cellWidth // 2
                zy = app.boardTop + row * app.cellHeight + app.cellHeight // 2
                if ztype == 'giantZombie':
                    zombie = GiantZombie(zx, zy, row)
                else:
                    zombie = NormalZombie(zx, zy, row)
                app.zombies.append(zombie)
                app.zombiePoints -= zcost

def onKeyPress(app, key):
    if app.gameOver:
        if key == 'r' or key == 'R':
            resetGame(app)
        return
    if key == 'r' or key == 'R':
        resetGame(app)
    if key == 'p' or key == 'P':
        app.paused = not app.paused
    if key == 's' or key == 'S':
        app.showGrid = not app.showGrid

def onStep(app):
    if app.gameOver or app.paused:
        return
    app.zombiePointTimer += 1
    if app.zombiePointTimer >= app.zombiePointRate:
        app.zombiePointTimer = 0
        app.zombiePoints += 10
    app.plantSpawnTimer += 1
    if app.plantSpawnTimer >= app.plantSpawnRate:
        app.plantSpawnTimer = 0
        spawnPlant(app)
    app.plantAttackTimer += 1
    if app.plantAttackTimer >= app.plantAttackRate:
        app.plantAttackTimer = 0
        plantAttack(app)
    updateBullets(app)
    updateZombies(app)
    checkCollisions(app)
    checkGameState(app)
    app.plantImage = (app.plantImage + 1) % max(app.plantImageCount.values())
    app.zombieWalkingImage = (app.zombieWalkingImage + 1) % 46
    app.zombieEatingImage = (app.zombieEatingImage + 1) % 40
    app.giantZombieWalkingImage = (app.giantZombieWalkingImage + 1) % len(app.giantZombieWalkingImages)
    app.giantZombieEatingImage = (app.giantZombieEatingImage + 1) % len(app.giantZombieEatingImages)

def spawnPlant(app):
    empty = [(r, c) for r in range(app.rows) for c in range(app.cols) if app.board[r][c] is None]
    if not empty:
        return
    plantType = random.choice(list(app.plants.keys()))
    if plantType == 'sunflower':
        valid = [(r, c) for (r, c) in empty if c in (0, 1)]
        if not valid:
            return
        row, col = random.choice(valid)
    elif plantType == 'wallnut':
        valid = []
        for row in range(app.rows):
            row_empty = [c for c in range(app.cols) if app.board[row][c] is None]
            if row_empty:
                for c in sorted(row_empty, reverse=True):
                    if all(app.board[row][cc] is None for cc in range(c+1, app.cols)):
                        valid.append((row, c))
                        break
        if not valid:
            return
        row, col = random.choice(valid)
    else:
        row, col = random.choice(empty)
    plant_class = app.plants[plantType]
    plant = plant_class(row, col)
    app.board[row][col] = plant

def plantAttack(app):
    for row in range(app.rows):
        for col in range(app.cols):
            plant = app.board[row][col]
            if plant and plant.type == 'peashooter':
                for zombie in app.zombies:
                    if zombie.row == row and zombie.x > app.boardLeft + col * app.cellWidth:
                        bulletX = app.boardLeft + col * app.cellWidth + app.cellWidth // 2
                        bulletY = app.boardTop + row * app.cellHeight + app.cellHeight // 2
                        app.bullets.append({
                            'x': bulletX,
                            'y': bulletY,
                            'row': row,
                            'damage': 25
                        })
                        break

def updateBullets(app):
    for bullet in app.bullets[:]:
        bullet['x'] += 4
        if bullet['x'] > app.boardLeft + app.boardWidth + 60:
            app.bullets.remove(bullet)

def updateZombies(app):
    for zombie in app.zombies[:]:
        zombie.x -= zombie.speed
        if zombie.x < app.boardLeft - 60:
            app.gameOver = True

def checkCollisions(app):
    for bullet in app.bullets[:]:
        for zombie in app.zombies[:]:
            if (abs(bullet['x'] - zombie.x) < 25 and abs(bullet['y'] - zombie.y) < 35):
                zombie.health -= bullet['damage']
                if bullet in app.bullets:
                    app.bullets.remove(bullet)
                if zombie.health <= 0:
                    app.zombies.remove(zombie)
                    app.score += 10
                break
    for zombie in app.zombies[:]:
        attacked = False
        for row in range(app.rows):
            for col in range(app.cols):
                plant = app.board[row][col]
                if plant and zombie.row == row:
                    plantX = app.boardLeft + col * app.cellWidth + app.cellWidth // 2
                    if abs(zombie.x - plantX) < 40:
                        plant.health -= 1
                        zombie.speed = 0
                        zombie.state = 'eating'
                        attacked = True
                        if plant.health <= 0:
                            app.board[row][col] = None
                            app.zombiePoints += 20
                        break
            if attacked:
                break
        if not attacked:
            zombie.speed = 0.5
            zombie.state = 'walking'

def checkGameState(app):
    for zombie in app.zombies:
        if zombie.x < app.boardLeft - 60:
            app.gameOver = True
            app.victory = True
            return

def resetGame(app):
    app.gameOver = False
    app.victory = False
    app.paused = False
    app.score = 0
    app.zombiePoints = 100
    app.zombiePointTimer = 0
    app.wave = 1
    app.board = [[None] * app.cols for _ in range(app.rows)]
    app.bullets = []
    app.zombies = []
    app.suns = []
    app.plantSpawnTimer = 0
    app.plantAttackTimer = 0
    app.plantImage = 0
    app.zombieWalkingImage = 0
    app.zombieEatingImage = 0
    app.giantZombieWalkingImage = 0
    app.giantZombieEatingImage = 0

def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def main():
    runApp(width=900, height=650)

if __name__ == '__main__':
    main() 