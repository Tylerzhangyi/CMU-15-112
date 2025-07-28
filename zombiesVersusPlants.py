from cmu_graphics import *
import math
import random
import copy




class darkMage:
    def __init__(self):
        self.power = 100
        self.x = 800
        self.y = 145 + 71 // 2
        self.targetY = self.y
        self.row = 0
        self.images = [f'darkMage/frame_{i}_delay-0.09s.png' for i in range(5)]
        self.summonImages = [f'summon/frame_{i:02d}_delay-0.1s.png' for i in range(28)]
        self.index = 0
        self.timer = 0
        self.speed = 5
        self.moveSpeed = 3
        self.summoning = False
        self.summonTimer = 0



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

class Zombie:
    def __init__(self, x, y, row, zombieType):
        self.x = x
        self.y = y
        self.row = row
        self.type = zombieType
        self.state = 'walking'

        if zombieType == 'zombie':
            self.health = 100
            self.speed = 0.5
        elif zombieType == 'giantZombie':
            self.health = 400
            self.speed = 0.25
        else:
            self.health = 100
            self.speed = 0.5
            
        self.maxHealth = self.health

    def isAlive(self):
        return self.health > 0

class Lawnmower:
    def __init__(self, app, row):
        self.x = app.boardLeft - 40
        self.y = app.boardTop + row * app.cellHeight + app.cellHeight // 2
        self.row = row
        self.active = True
        self.moving = False
        self.imageIndex = 0

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
    app.zombies = []
    app.zombieTypes = ['zombie', 'giantZombie']
    app.zombieType = 'zombie'
    app.zombieCostDict = {'zombie': 50, 'giantZombie': 150}
    app.zombiePoints = 100
    app.zombiePointTimer = 0
    app.zombiePointRate = 30
    app.bullets = []
    app.score = 0
    app.plantAttackTimer = 0
    app.plantAttackRate = 60
    app.plantCount = 0
    app.plantSpawnNum = 60
    app.plantImages = {
        'sunflower': [f'sunFlower/sunFlower_{i:02d}.png' for i in range(36)],
        'peashooter': [f'peaShooter/peaShooter_{i:02d}.png' for i in range(77)],
        'wallnut': [f'wallNut/wallNut_{i:02d}.png' for i in range(44)],
    }

    app.plantImageIndex = {
        'sunflower': 0,
        'peashooter': 0,
        'wallnut': 0
    }
    app.zombieWalkingImages = [f'zombieWalking/zombieWalking_{i:02d}.png' for i in range(46)]
    app.zombieEatingImages = [f'zombieEating/zombieEating_{i:02d}.png' for i in range(40)]
    app.giantZombieWalkingImages = [f'giantZombieWalking/giantZombie_{i:03d}.png' for i in range(161)]
    app.giantZombieEatingImages = [f'giantZombieEating/giantZombie_{i:02d}.png' for i in range(38)]
    app.zombieImageIndex = {
        'zombie': {'walking': 0, 'eating': 0},
        'giantZombie': {'walking': 0, 'eating': 0}
    }
    app.paused = False
    app.gameOver = False
    app.showGrid = False
    app.showHealthBars = False
    app.lawnmowerImages = [f'lawnmover/lawnmover_{i:02d}.png' for i in range(8)]
    app.lawnmowers = [Lawnmower(app, r) for r in range(app.rows)]
    app.darkMage = darkMage()

def redrawAll(app):
    if app.mode == 'menu':
        drawImage('menu.jpg', 0, 0, width=app.width, height=app.height)
        drawRect(350, 565, 200, 70, fill='brown', border='black', borderWidth=6)
        drawLabel('Start', 450, 600, size=36, fill='white', bold=True)
        return
    drawImage("garden.jpg", 0, 0)
    drawLabel('Zombies vs Plants', app.width//2, 40, size=40, fill='darkgreen', bold=True)
    drawZombieSelector(app)
    drawLabel(f'Zombie Points: {app.zombiePoints}', app.width//2, 580, size=20, fill='black',bold=True)
  
    drawBoard(app)
    drawLawnmowers(app)
    drawPlants(app)
    drawBullets(app)
    drawZombies(app)
    
    if app.darkMage.summoning:
        summonFrame = (app.darkMage.summonTimer * len(app.darkMage.summonImages)) // 60
        if summonFrame >= len(app.darkMage.summonImages):
            app.darkMage.summoning = False
            app.darkMage.summonTimer = 0
        else:
            drawImage(app.darkMage.summonImages[summonFrame], app.darkMage.x, app.darkMage.y, align='center', width=100, height=100)
    else:
        drawImage(app.darkMage.images[app.darkMage.index], app.darkMage.x, app.darkMage.y, align='center', width=80, height=80)
    
    if app.gameOver:
        drawRect(0, 0, app.width, app.height, fill='white', opacity=80)
        drawLabel('You Win!', app.width//2, app.height//2-30, size=40, bold=True, fill='green')
        drawLabel(f'Final Score: {app.score}', app.width//2, app.height//2+10, size=28, fill='black')
        drawLabel('Press R to Restart', app.width//2, app.height//2+50, size=20, fill='black')
    elif app.paused:
        drawRect(0,0,app.width,app.height,fill = "black",opacity = 60)
        drawLabel('Paused', app.width//2, app.height//2, size=50, fill='white', bold=True)
    
def drawZombieSelector(app):
    selectorWidth = 300
    selectorHeight = 100
    selectorLeft = 0
    selectorTop = 549
    drawRect(selectorLeft, selectorTop, selectorWidth, selectorHeight, fill='brown', border='black', borderWidth=2, opacity=75)
    zombies = app.zombieTypes

    for i in range(len(zombies)):
        ztype = zombies[i]
        x = selectorLeft + 50 + i * 120
        y = selectorTop + 20
        color = 'yellow' if app.zombieType == ztype else None

        if ztype == 'zombie':
            img = app.zombieWalkingImages[0]
        else:
            img = app.giantZombieWalkingImages[0]

        drawImage(img, x + 15, y + 15, align='center', width=50, height=50)
        drawRect(x - 5, y - 5, 50, 50, border=color, borderWidth=3, fill=None)
        drawLabel(ztype, x + 15, y + 65, size=14, fill='black')
        drawLabel(f'{app.zombieCostDict[ztype]}', x + 15, y + 85, size=12, fill='black')

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
                imageIndex = app.plantImageIndex[plantType]
                imageUrl = app.plantImages[plantType][imageIndex]
                drawImage(imageUrl, x, y, align='center', width=app.cellWidth, height=app.cellHeight)
                if app.showHealthBars:
                    healthPercent = plant.health / plant.maxHealth
                    drawRect(x - 30, y - 40, 60 * healthPercent, 7, fill='red')
                    drawRect(x - 30, y - 40, 60, 7, fill=None, border='black')

def drawBullets(app):
    for bullet in app.bullets:
        drawImage('resource/pea.webp', bullet['x'], bullet['y'], align='center', width=20, height=20)

def drawZombies(app):
    for zombie in app.zombies:
        x, y = zombie.x, zombie.y
        ztype = getattr(zombie, 'type', 'zombie')
        if ztype == 'giantZombie':
            if zombie.state == 'walking':
                imageIndex = app.zombieImageIndex['giantZombie']['walking']
                image = app.giantZombieWalkingImages[imageIndex]
                drawImage(image, x, y - 20, align='center', width=app.cellWidth + 120, height=app.cellHeight + 100)
            else:
                imageIndex = app.zombieImageIndex['giantZombie']['eating']
                image = app.giantZombieEatingImages[imageIndex]
                drawImage(image, x, y - 50, align='center', width=app.cellWidth + 140, height=app.cellHeight + 120)
        else:
            if zombie.state == 'walking':
                imageIndex = app.zombieImageIndex['zombie']['walking']
                image = app.zombieWalkingImages[imageIndex]
                drawImage(image, x, y, align='center', width=app.cellWidth + 60, height=app.cellHeight + 20)
            else:
                imageIndex = app.zombieImageIndex['zombie']['eating']
                image = app.zombieEatingImages[imageIndex]
                drawImage(image, x, y, align='center', width=app.cellWidth, height=app.cellHeight)
        if app.showHealthBars:
            healthPercent = zombie.health / zombie.maxHealth
            drawRect(x - 25, y - 55, 50 * healthPercent, 7, fill='red')
            drawRect(x - 25, y - 55, 50, 7, fill=None, border='black')

def drawLawnmowers(app):
    for mower in app.lawnmowers:
        if mower.active:
            imageUrl = app.lawnmowerImages[mower.imageIndex]
            drawImage(imageUrl, mower.x, mower.y, align='center', width=50, height=40)

def onMousePress(app, x, y):
    if app.mode == 'menu':
        if 350 <= x <= 550 and 565 <= y <= 635:
            app.mode = 'game'
            app.paused = False
        return
    selectorWidth = 300
    selectorHeight = 100
    selectorLeft = 0
    selectorTop = 549
    if selectorLeft <= x <= selectorLeft + selectorWidth and selectorTop <= y <= selectorTop + selectorHeight:
        zIndex = (x - selectorLeft - 50) // 120
        zombies = app.zombieTypes
        if 0 <= zIndex < len(zombies):
            app.zombieType = zombies[zIndex]
        return
    if app.gameOver:
        return
    if app.paused:
        return
    
    darkMageX = app.darkMage.x
    darkMageY = app.darkMage.y
    if abs(x - darkMageX) < 40 and abs(y - darkMageY) < 40:
        ztype = app.zombieType
        zcost = app.zombieCostDict.get(ztype, 50)
        if app.zombiePoints >= zcost:
            zombie = Zombie(darkMageX, darkMageY, app.darkMage.row, ztype)
            app.zombies.append(zombie)
            app.zombiePoints -= zcost
        return
    
    rightColX = app.boardLeft + app.boardWidth
    if x > rightColX and app.boardTop <= y < app.boardTop + app.boardHeight:
        row = int((y - app.boardTop) // app.cellHeight)
        col = app.cols - 1
        if 0 <= row < app.rows:
            ztype = app.zombieType
            zcost = app.zombieCostDict.get(ztype, 50)
            if app.zombiePoints >= zcost:
                zx = app.boardLeft + col * app.cellWidth + app.cellWidth // 2
                zy = app.boardTop + row * app.cellHeight + app.cellHeight // 2
                zombie = Zombie(zx, zy, row, ztype)
                app.zombies.append(zombie)
                app.zombiePoints -= zcost

def onKeyPress(app, key):
    if key == 'r' or key == 'R':
        app.mode = 'menu'
        resetGame(app)
    if key == 'p' or key == 'P':
        app.paused = not app.paused
    if key == 's' or key == 'S':
        app.showGrid = not app.showGrid
    if key == 'h' or key == 'H':
        app.showHealthBars = not app.showHealthBars
    if key == 'left':
        currentIndex = app.zombieTypes.index(app.zombieType)
        app.zombieType = app.zombieTypes[(currentIndex - 1) % len(app.zombieTypes)]
    elif key == 'right':
        currentIndex = app.zombieTypes.index(app.zombieType)
        app.zombieType = app.zombieTypes[(currentIndex + 1) % len(app.zombieTypes)]
    elif key == 'up':
        app.darkMage.targetY -= app.cellHeight
        if app.darkMage.targetY < app.boardTop + app.cellHeight // 2:
            app.darkMage.targetY = app.boardTop + app.cellHeight // 2
    elif key == 'down':
        app.darkMage.targetY += app.cellHeight
        if app.darkMage.targetY > app.boardTop + app.boardHeight - app.cellHeight // 2:
            app.darkMage.targetY = app.boardTop + app.boardHeight - app.cellHeight // 2
    elif key == 'enter':
        ztype = app.zombieType
        zcost = app.zombieCostDict.get(ztype, 50)
        if app.zombiePoints >= zcost:
            app.darkMage.summoning = True
            app.darkMage.summonTimer = 0
            zombie = Zombie(app.darkMage.x, app.darkMage.y, app.darkMage.row, ztype)
            app.zombies.append(zombie)
            app.zombiePoints -= zcost

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
    
    app.darkMage.timer += 1
    if app.darkMage.timer >= app.darkMage.speed:
        app.darkMage.timer = 0
        if not app.darkMage.summoning:
            app.darkMage.index = (app.darkMage.index + 1) % len(app.darkMage.images)
    
    if app.darkMage.summoning:
        app.darkMage.summonTimer += 1
    
    if abs(app.darkMage.y - app.darkMage.targetY) > 1:
        if app.darkMage.y < app.darkMage.targetY:
            app.darkMage.y += app.darkMage.moveSpeed
        elif app.darkMage.y > app.darkMage.targetY:
            app.darkMage.y -= app.darkMage.moveSpeed
    
    app.darkMage.row = int((app.darkMage.y - app.boardTop) // app.cellHeight)
    if app.darkMage.row < 0:
        app.darkMage.row = 0
    elif app.darkMage.row >= app.rows:
        app.darkMage.row = app.rows - 1

    app.zombiePointTimer += 1
    if app.zombiePointTimer >= app.zombiePointRate:
        app.zombiePointTimer = 0
        app.zombiePoints += 10
    app.plantCount += 1
    if app.plantCount >= app.plantSpawnNum:
        app.plantCount = 0
        spawnPlant(app)
    app.plantImageIndex['sunflower'] = (app.plantImageIndex['sunflower'] + 1) % 36
    app.plantImageIndex['peashooter'] = (app.plantImageIndex['peashooter'] + 1) % 77
    app.plantImageIndex['wallnut'] = (app.plantImageIndex['wallnut'] + 1) % 44
    app.zombieImageIndex['zombie']['walking'] = (app.zombieImageIndex['zombie']['walking'] + 1) % 46
    app.zombieImageIndex['zombie']['eating'] = (app.zombieImageIndex['zombie']['eating'] + 1) % 40
    app.zombieImageIndex['giantZombie']['walking'] = (app.zombieImageIndex['giantZombie']['walking'] + 1) % 161
    app.zombieImageIndex['giantZombie']['eating'] = (app.zombieImageIndex['giantZombie']['eating'] + 1) % 38
    app.plantAttackTimer += 1
    if app.plantAttackTimer >= app.plantAttackRate:
        app.plantAttackTimer = 0
        plantAttack(app)
    updateGame(app)
    checkCollisions(app)
    checkGameState(app)

def updateGame(app):
    for bullet in app.bullets[:]:
        bullet['x'] += 4
        if bullet['x'] > app.boardLeft + app.boardWidth + 60:
            app.bullets.remove(bullet)
    for zombie in app.zombies[:]:
        zombie.x -= zombie.speed
        if zombie.x < app.boardLeft - 60:
            app.gameOver = True
    for mower in app.lawnmowers:
        if mower.moving and mower.active:
            mower.x += 5
            mower.imageIndex = (mower.imageIndex + 1) % len(app.lawnmowerImages)
            app.zombies = [z for z in app.zombies if z.row != mower.row or z.x > mower.x + 30]
            if mower.x > app.boardLeft + app.boardWidth:
                mower.active = False
        else:
            for z in app.zombies:
                if z.row == mower.row and z.x < app.boardLeft + 10:
                    mower.moving = True
                    break

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
            if zombie.type == 'zombie':
                zombie.speed = 0.5
            else:
                zombie.speed = 0.25
            zombie.state = 'walking'

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

def checkGameState(app):
    for zombie in app.zombies:
        if zombie.x < app.boardLeft - 60:
            app.gameOver = True
            return

def resetGame(app):
    app.gameOver = False
    app.paused = False
    app.score = 0
    app.zombiePoints = 100
    app.zombiePointTimer = 0
    app.board = [[None] * app.cols for _ in range(app.rows)]
    app.bullets = []
    app.zombies = []
    app.plantCount = 0
    app.plantAttackTimer = 0
    app.plantImageIndex = {
        'sunflower': 0,
        'peashooter': 0,
        'wallnut': 0
    }
    app.zombieImageIndex = {
        'zombie': {'walking': 0, 'eating': 0},
        'giantZombie': {'walking': 0, 'eating': 0}
    }
    app.showHealthBars = False
    app.lawnmowers = [Lawnmower(app, r) for r in range(app.rows)]
    app.darkMage = darkMage()









def main():
    runApp(width=900, height=650)

if __name__ == '__main__':
    main() 