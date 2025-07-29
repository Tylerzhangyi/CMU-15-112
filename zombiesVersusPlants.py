from cmu_graphics import *
import math
import random
import copy

'''
----------------------------------------------------------------------------------------------------------------
All the picture resources are from https://terraria.wiki.gg/ and https://plantsvszombies.fandom.com/wiki/Wiki
----------------------------------------------------------------------------------------------------------------
'''

class Mage:
    def __init__(self):
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
    def __init__(self, row, col, type):
        self.row = row
        self.col = col
        self.type = type
        if type == 'sunflower':
            self.health = 100
        elif type == 'peashooter':
            self.health = 100
        else:
            self.health = 300
        self.maxHealth = self.health

    def alive(self):
        return self.health > 0

class Zombie:
    def __init__(self, x, y, row, type):
        self.x = x
        self.y = y
        self.row = row
        self.type = type
        self.state = 'walking'
        if type == 'zombie':
            self.health = 100
            self.speed = 0.75
            self.damage = 1
        elif type == 'giantZombie':
            self.health = 700
            self.speed = 0.45
            self.damage = 3
        else:
            self.health = 100
            self.speed = 0.75
            self.damage = 1  
        self.maxHealth = self.health

    def alive(self):
        return self.health > 0

class Mower:
    def __init__(self, app, row):
        self.x = app.boardLeft - 40
        self.y = app.boardTop + row * app.cellHeight + app.cellHeight // 2
        self.row = row
        self.active = True
        self.moving = False
        self.index = 0

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
    app.zombieCost = {'zombie': 100, 'giantZombie': 350}
    app.zombiePoints = 1500
    app.bullets = []
    app.score = 0
    app.plantTimer = 0
    app.plantRate = 60
    app.plantCount = 0
    app.plantSpawnNum = 60
    app.plantImages = {
        'sunflower': [f'sunFlower/sunFlower_{i:02d}.png' for i in range(36)],
        'peashooter': [f'peaShooter/peaShooter_{i:02d}.png' for i in range(77)],
        'wallnut': [f'wallNut/wallNut_{i:02d}.png' for i in range(44)],
    }
    app.plantIndex = {
        'sunflower': 0,
        'peashooter': 0,
        'wallnut': 0
    }
    app.zombieWalkImages = [f'zombieWalking/zombieWalking_{i:02d}.png' for i in range(46)]
    app.zombieEatImages = [f'zombieEating/zombieEating_{i:02d}.png' for i in range(40)]
    app.giantWalkImages = [f'giantZombieWalking/giantZombie_{i:03d}.png' for i in range(161)]
    app.giantEatImages = [f'giantZombieEating/giantZombie_{i:02d}.png' for i in range(38)]
    app.zombieIndex = {
        'zombie': {'walking': 0, 'eating': 0},
        'giantZombie': {'walking': 0, 'eating': 0}
    }
    app.paused = False
    app.gameOver = False
    app.showGrid = False
    app.showHealth = False
    app.mowerImages = [f'lawnmover/lawnmover_{i:02d}.png' for i in range(8)]
    app.mowers = [Mower(app, r) for r in range(app.rows)]
    app.mage = Mage()

def drawMenu(app):
    drawImage('menu.jpg', 0, 0, width=app.width, height=app.height)
    drawRect(450, 600, 300, 70, fill='brown', border='black', borderWidth=6,align='center')
    drawLabel('Start', 450, 600, size=36, fill='white', bold=True,)
    drawRect(450, 520, 300, 70, fill='brown', border='black', borderWidth=6,align='center')
    drawLabel('Instruction', 450, 520, size=36, fill='white', bold=True)

def drawInstruction(app):
    drawRect(0, 0, app.width, app.height, fill='white')
    drawRect(350, 565, 200, 70, fill='brown', border='black', borderWidth=6)
    drawLabel('Back', 450, 600, size=36, fill='white', bold=True)
    drawLabel('Use ← and → to select a zombie', app.width//2, 100, size=20, fill='black', bold=True)
    drawLabel('Use ↑ and ↓ to move the dark mage', app.width//2, 140, size=20, fill='black', bold=True)
    drawLabel('Press Enter to summon a zombie', app.width//2, 180, size=20, fill='black', bold=True)
    drawLabel('Press P to pause the game', app.width//2, 220, size=20, fill='black', bold=True)
    drawLabel('Press S to show the grid', app.width//2, 260, size=20, fill='black', bold=True)
    drawLabel('Press H to show the health bars', app.width//2, 300, size=20, fill='black', bold=True)
    drawLabel('Press R to restart the game', app.width//2, 340, size=20, fill='black', bold=True)

def drawGame(app):
    drawImage("garden.jpg", 0, 0)
    drawLabel('Zombies vs Plants', app.width//2, 40, size=40, fill='darkgreen', bold=True)
    drawZombieSelector(app)
    drawLabel(f'Zombie Points: {app.zombiePoints}', app.width//2, 580, size=20, fill='black',bold=True)
  
    drawBoard(app)
    drawMowers(app)
    drawPlants(app)
    drawBullets(app)
    drawZombies(app)
    
    if app.mage.summoning:
        summonFrame = (app.mage.summonTimer * len(app.mage.summonImages)) // 60
        if summonFrame >= len(app.mage.summonImages):
            app.mage.summoning = False
            app.mage.summonTimer = 0
        else:
            drawImage(app.mage.summonImages[summonFrame], app.mage.x, app.mage.y, align='center', width=100, height=100)
    else:
        drawImage(app.mage.images[app.mage.index], app.mage.x, app.mage.y, align='center', width=80, height=80)
    
    if app.gameOver:
        drawRect(0, 0, app.width, app.height, fill='white', opacity=80)
        drawLabel('You Win!', app.width//2, app.height//2-30, size=40, bold=True, fill='green')
        drawLabel(f'Final Score: {app.score}', app.width//2, app.height//2+10, size=28, fill='black')
        drawLabel('Press R to Restart', app.width//2, app.height//2+50, size=20, fill='black')
    elif app.paused:
        drawRect(0,0,app.width,app.height,fill = "black",opacity = 60)
        drawLabel('Paused', app.width//2, app.height//2, size=50, fill='white', bold=True)
 
def redrawAll(app):
    if app.mode == 'menu':
        drawMenu(app)
    elif app.mode == 'instruction':
        drawInstruction(app)
    elif app.mode == 'game':
        drawGame(app)   

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
            img = app.zombieWalkImages[0]
        else:
            img = app.giantWalkImages[0]

        drawImage(img, x + 15, y + 15, align='center', width=50, height=50)
        drawRect(x - 5, y - 5, 50, 50, border=color, borderWidth=3, fill=None)
        drawLabel(f'{ztype}-{app.zombieCost[ztype]}', x + 15, y + 65, size=12, fill='black')

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
                imageIndex = app.plantIndex[plantType]
                imageUrl = app.plantImages[plantType][imageIndex]
                drawImage(imageUrl, x, y, align='center', width=app.cellWidth, height=app.cellHeight)
                if app.showHealth:
                    healthPercent = plant.health / plant.maxHealth
                    drawRect(x - 30, y - 40, 60 * healthPercent, 7, fill='red')
                    drawRect(x - 30, y - 40, 60, 7, fill=None, border='black')

def drawBullets(app):
    for bullet in app.bullets:
        drawImage('resource/pea.webp', bullet['x'], bullet['y'], align='center', width=20, height=20)

def drawZombies(app):
    for zombie in app.zombies:
        x, y = zombie.x, zombie.y
        ztype = zombie.type
        if ztype == 'giantZombie':
            if zombie.state == 'walking':
                imageIndex = app.zombieIndex['giantZombie']['walking']
                image = app.giantWalkImages[imageIndex]
                drawImage(image, x, y - 20, align='center', width=app.cellWidth + 120, height=app.cellHeight + 100)
            else:
                imageIndex = app.zombieIndex['giantZombie']['eating']
                image = app.giantEatImages[imageIndex]
                drawImage(image, x, y - 50, align='center', width=app.cellWidth + 140, height=app.cellHeight + 120)
        else:
            if zombie.state == 'walking':
                imageIndex = app.zombieIndex['zombie']['walking']
                image = app.zombieWalkImages[imageIndex]
                drawImage(image, x, y, align='center', width=app.cellWidth + 60, height=app.cellHeight + 20)
            else:
                imageIndex = app.zombieIndex['zombie']['eating']
                image = app.zombieEatImages[imageIndex]
                drawImage(image, x, y, align='center', width=app.cellWidth, height=app.cellHeight)
        if app.showHealth:
            healthPercent = zombie.health / zombie.maxHealth
            drawRect(x - 25, y - 55, 50 * healthPercent, 7, fill='red')
            drawRect(x - 25, y - 55, 50, 7, fill=None, border='black')

def drawMowers(app):
    for mower in app.mowers:
        if mower.active:
            imageUrl = app.mowerImages[mower.index]
            drawImage(imageUrl, mower.x, mower.y, align='center', width=50, height=40)

def onMousePress(app, x, y):
    if app.mode == 'menu':
        onMousePressMenu(app, x, y)
    elif app.mode == 'instruction':
        onMousePressInstruction(app, x, y)
    elif app.mode == 'game':
        onMousePressGame(app, x, y)

def onMousePressMenu(app, x, y):
    if 300 <= x <= 600 and 565 <= y <= 635:
        app.mode = 'game'
        app.paused = False
    elif 300 <= x <= 600 and 485 <= y <= 555:
        app.mode = 'instruction'

def onMousePressInstruction(app, x, y):
    if 350 <= x <= 550 and 565 <= y <= 635:
        app.mode = 'menu'

def onMousePressGame(app, x, y):
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
    
    mageX = app.mage.x
    mageY = app.mage.y
    if abs(x - mageX) < 40 and abs(y - mageY) < 40:
        ztype = app.zombieType
        zcost = app.zombieCost.get(ztype, 50)
        if app.zombiePoints >= zcost:
            zombie = Zombie(mageX, mageY, app.mage.row, ztype)
            app.zombies.append(zombie)
            app.zombiePoints -= zcost
        return
    
    rightColX = app.boardLeft + app.boardWidth
    if x > rightColX and app.boardTop <= y < app.boardTop + app.boardHeight:
        row = int((y - app.boardTop) // app.cellHeight)
        col = app.cols - 1
        if 0 <= row < app.rows:
            ztype = app.zombieType
            zcost = app.zombieCost.get(ztype, 50)
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
        app.showHealth = not app.showHealth
    if key == 'left':
        currentIndex = app.zombieTypes.index(app.zombieType)
        app.zombieType = app.zombieTypes[(currentIndex - 1) % len(app.zombieTypes)]
    elif key == 'right':
        currentIndex = app.zombieTypes.index(app.zombieType)
        app.zombieType = app.zombieTypes[(currentIndex + 1) % len(app.zombieTypes)]
    elif key == 'up':
        app.mage.targetY -= app.cellHeight
        if app.mage.targetY < app.boardTop + app.cellHeight // 2:
            app.mage.targetY = app.boardTop + app.cellHeight // 2
    elif key == 'down':
        app.mage.targetY += app.cellHeight
        if app.mage.targetY > app.boardTop + app.boardHeight - app.cellHeight // 2:
            app.mage.targetY = app.boardTop + app.boardHeight - app.cellHeight // 2
    elif key == 'enter':
        ztype = app.zombieType
        zcost = app.zombieCost.get(ztype, 50)
        if app.zombiePoints >= zcost:
            app.mage.summoning = True
            app.mage.summonTimer = 0
            zombie = Zombie(app.mage.x, app.mage.y, app.mage.row, ztype)
            app.zombies.append(zombie)
            app.zombiePoints -= zcost

def spawnPlant(app):
    emptyPs = [(row, col) for row in range(app.rows) for col in range(app.cols) if app.board[row][col] is None]
    
    if emptyPs:
        plantTypes = {'sunflower': 0.2,'peashooter': 0.6, 'wallnut': 0.2}
        selectedPlantType = random.choices(list(plantTypes.keys()), weights=list(plantTypes.values()))[0]
        print(selectedPlantType)
        
        if selectedPlantType == 'sunflower':
            validPs = [(row, col) for (row, col) in emptyPs if col in (0, 1)]
            if validPs:
                row, col = random.choice(validPs)
                newPlant = Plant(row, col, selectedPlantType)
                app.board[row][col] = newPlant
                
        elif selectedPlantType == 'wallnut':
            validPs = []
            for row, col in emptyPs:
                hasPlantBehind = False
                for checkCol in range(col + 1, app.cols):
                    plantBehind = app.board[row][checkCol]
                    if plantBehind is not None and plantBehind.type != 'wallnut':
                        hasPlantBehind = True
                        break
                if hasPlantBehind:
                    validPs.append((row, col))
            
            if validPs:
                row, col = random.choice(validPs)
                newPlant = Plant(row, col, selectedPlantType)
                app.board[row][col] = newPlant
                
        else:
            row, col = random.choice(emptyPs)
            newPlant = Plant(row, col, selectedPlantType)
            app.board[row][col] = newPlant

def onStep(app):
    if app.mode == 'game':
        onStepGame(app)
    elif app.mode == 'instruction':
        onStepInstruction(app)

def onStepInstruction(app):
    pass

def onStepGame(app):
    if app.paused:
        return
    app.mage.timer += 1
    if app.mage.timer >= app.mage.speed:
        app.mage.timer = 0
        if not app.mage.summoning:
            app.mage.index = (app.mage.index + 1) % len(app.mage.images)
    if app.mage.summoning:
        app.mage.summonTimer += 1
    if app.mage.y < app.mage.targetY:
        app.mage.y += app.mage.moveSpeed
    elif app.mage.y > app.mage.targetY:
        app.mage.y -= app.mage.moveSpeed
    app.mage.row = int((app.mage.y - app.boardTop) // app.cellHeight)
    if app.mage.row < 0:
        app.mage.row = 0
    elif app.mage.row >= app.rows:
        app.mage.row = app.rows - 1
    app.plantCount += 1
    if app.plantCount >= app.plantSpawnNum:
        app.plantCount = 0
        spawnPlant(app)

    app.plantIndex['sunflower'] = (app.plantIndex['sunflower'] + 1) % 36
    app.plantIndex['peashooter'] = (app.plantIndex['peashooter'] + 1) % 77
    app.plantIndex['wallnut'] = (app.plantIndex['wallnut'] + 1) % 44
    app.zombieIndex['zombie']['walking'] = (app.zombieIndex['zombie']['walking'] + 1) % 46
    app.zombieIndex['zombie']['eating'] = (app.zombieIndex['zombie']['eating'] + 1) % 40
    app.zombieIndex['giantZombie']['walking'] = (app.zombieIndex['giantZombie']['walking'] + 1) % 161
    app.zombieIndex['giantZombie']['eating'] = (app.zombieIndex['giantZombie']['eating'] + 1) % 38
   
    app.plantTimer += 1

    if app.plantTimer >= app.plantRate:
        app.plantTimer = 0
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
    for mower in app.mowers:
        if mower.moving and mower.active:
            mower.x += 5
            mower.index = (mower.index + 1) % len(app.mowerImages)
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
                        plant.health -= zombie.damage
                        zombie.speed = 0
                        zombie.state = 'eating'
                        attacked = True
                        if plant.health <= 0:
                            app.board[row][col] = None
                            app.zombiePoints += 120
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
    app.zombiePoints = 1500
    app.board = [[None] * app.cols for _ in range(app.rows)]
    app.bullets = []
    app.zombies = []
    app.plantCount = 0
    app.plantTimer = 0
    app.plantIndex = {
        'sunflower': 0,
        'peashooter': 0,
        'wallnut': 0
    }
    app.zombieIndex = {
        'zombie': {'walking': 0, 'eating': 0},
        'giantZombie': {'walking': 0, 'eating': 0}
    }
    app.showHealth = False
    app.mowers = [Mower(app, r) for r in range(app.rows)]
    app.mage = Mage()

def main():
    runApp(width=900, height=650)

if __name__ == '__main__':
    main() 