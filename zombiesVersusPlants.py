from cmu_graphics import *
import math
import random
import copy

'''
----------------------------------------------------------------------------------------------------------------------
    All the picture resources are from https://terraria.wiki.gg/ and https://plantsvszombies.fandom.com/wiki/Wiki
----------------------------------------------------------------------------------------------------------------------
'''

#GPT Prompt: Give me a regular expression that can add space to both side of the equal sign and can be runned in the terminal of pycharm
#python -c "import re, sys; print(re.sub(r'\s*=\s*', ' = ', sys.stdin.read()))"

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
        elif type == 'repeater':
            self.health = 100
        elif type == 'snowPeaShooter':
            self.health = 100
        elif type == 'potato':
            self.health = 999999
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
            self.speed = 0.7
            self.damage = 1
        elif type == 'giantZombie':
            self.health = 800
            self.speed = 0.5
            self.damage = 3
        elif type == 'doorZombie':
            self.health = 200
            self.speed = 0.6
            self.damage = 1
        else:
            self.health = 100
            self.speed = 0.7
            self.damage = 1
        self.slowed = False
        self.slowTimer = 0
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
    app.zombies = []
    app.zombieTypes = ['zombie', 'giantZombie', 'doorZombie']
    app.zombieType = 'zombie'
    app.zombieCost = {'zombie': 100, 'giantZombie': 600, 'doorZombie': 200}
    app.zombiePoints = 2000
    app.bullets = []
    app.plantTimer = 0
    app.plantRate = 60
    app.plantCount = 0
    app.plantSpawnNum = 120
    #Let AI to help me to solve the problem that the plant images are not showing correctly(change from i to i:02d)
    app.plantImages = {
        'sunflower': [f'sunFlower/sunFlower_{i:02d}.png' for i in range(36)],
        'peashooter': [f'peaShooter/peaShooter_{i:02d}.png' for i in range(77)],
        'wallnut': [f'wallNut/wallNut_{i:02d}.png' for i in range(44)],
        'repeater': [f'repeater/frame_{i:02d}_delay-0.03s.png' for i in range(49)],
        'snowPeaShooter': [f'snowPeaShooter/frame_{i:02d}_delay-0.07s.png' for i in range(25)],
        'potato': [f'potato/frame_{i:02d}_delay-0.03s.png' for i in range(29)],
    }
    app.plantIndex = {
        'sunflower': 0,
        'peashooter': 0,
        'wallnut': 0,
        'repeater': 0,
        'snowPeaShooter': 0,
        'potato': 0
    }
    #Let AI to help me to solve the problem that the zombie images are not showing correctly(change from i to i:02d)
    app.zombieWalkImages = [f'zombieWalking/zombieWalking_{i:02d}.png' for i in range(46)]
    app.zombieEatImages = [f'zombieEating/zombieEating_{i:02d}.png' for i in range(40)]
    app.giantWalkImages = [f'giantZombieWalking/giantZombie_{i:03d}.png' for i in range(161)]
    app.giantEatImages = [f'giantZombieEating/giantZombie_{i:02d}.png' for i in range(38)]
    app.doorZombieImage = 'resource/door.webp'
    app.zombieIndex = {
        'zombie': {'walking': 0, 'eating': 0},
        'giantZombie': {'walking': 0, 'eating': 0}
    }
    app.paused = False
    app.gameOver = False
    app.gameWon = False
    app.showGrid = False
    app.showHealth = False
    app.mowerImages = [f'lawnmover/lawnmover_{i:02d}.png' for i in range(8)]
    app.mowers = [Mower(app, r) for r in range(app.rows)]
    app.mage = Mage()
    app.commandMode = False
    app.commandString = ""

def drawMenu(app):
    drawImage('menu.jpg', 0, 0, width = app.width, height = app.height)
    drawRect(450, 600, 300, 70, fill = 'brown', border = 'black', borderWidth = 6, align = 'center')
    drawLabel('Start', 450, 600, size = 36, fill = 'white', bold = True,)
    drawRect(450, 520, 300, 70, fill = 'brown', border = 'black', borderWidth = 6, align = 'center')
    drawLabel('Instruction', 450, 520, size = 36, fill = 'white', bold = True)

def drawInstruction(app):
    x = 200
    drawRect(0, 0, app.width, app.height, fill = 'moccasin')
    drawRect(350, 565, 200, 70, fill = 'brown', border = 'black', borderWidth = 6)
    drawLabel('Instruction', 450, x - 100, size = 66, fill = 'black', bold = True)
    drawLabel('Back', 450, 600, size = 36, fill = 'white', bold = True)
    drawLabel('Use ← and → to select a zombie', app.width // 2, x, size = 20, fill = 'black', bold = True)
    drawLabel('Use ↑ and ↓ to move the dark mage', app.width // 2, x + 40, size = 20, fill = 'black', bold = True)
    drawLabel('Press Enter to summon a zombie', app.width // 2, x + 80, size = 20, fill = 'black', bold = True)
    drawLabel('Press P to pause the game', app.width // 2, x + 120, size = 20, fill = 'black', bold = True)
    drawLabel('Press S to show the grid', app.width // 2, x + 160, size = 20, fill = 'black', bold = True)
    drawLabel('Press H to show the health bars', app.width // 2, x + 200, size = 20, fill = 'black', bold = True)
    drawLabel('Press R to restart the game', app.width // 2, x + 240, size = 20, fill = 'black', bold = True)
    drawLabel('Press / to enter command mode', app.width // 2, x + 280, size = 20, fill = 'black', bold = True)

def drawGame(app):
    drawImage("garden.jpg", 0, 0)
    drawZombieSelector(app)
    drawLabel(f'Zombie Points: {app.zombiePoints}', app.width // 2 + 100, 580, size = 20, fill = 'black', bold = True)
    drawBoard(app)
    drawMowers(app)
    drawPlants(app)
    drawBullets(app)
    drawZombies(app)
    #I let AI to help me finish the summoning animation in one second
    if app.mage.summoning:
        summonFrame = (app.mage.summonTimer * len(app.mage.summonImages)) // 60
        if summonFrame >= len(app.mage.summonImages):
            app.mage.summoning = False
            app.mage.summonTimer = 0
        else:
            drawImage(app.mage.summonImages[summonFrame], app.mage.x, app.mage.y, align = 'center', width = 100, height = 100)
    else:
        drawImage(app.mage.images[app.mage.index], app.mage.x, app.mage.y, align = 'center', width = 80, height = 80)
    
    if app.commandMode:
        drawRect(430,600, app.width, app.height, fill='black', opacity=50)
        drawLabel('/' + app.commandString, 450, 620, size=16, fill='white', align='left-top')

    if app.gameOver:
        drawRect(0, 0, app.width, app.height, fill = 'white', opacity = 80)
        if app.gameWon:
            drawLabel('You Win!', app.width // 2, app.height // 2 - 30, size = 40, bold = True, fill = 'green')
        else:
            drawLabel('You Lose!', app.width // 2, app.height // 2 - 30, size = 40, bold = True, fill = 'red')
        drawLabel('Press R to Restart', app.width // 2, app.height // 2 + 50, size = 20, fill = 'black')
    elif app.paused:
        drawRect(0, 0, app.width, app.height, fill = "black", opacity = 60)
        drawLabel('Paused', app.width // 2, app.height // 2, size = 50, fill = 'white', bold = True)

def redrawAll(app):
    if app.mode == 'menu':
        drawMenu(app)
    elif app.mode == 'instruction':
        drawInstruction(app)
    elif app.mode == 'game':
        drawGame(app)   

def drawZombieSelector(app):
    drawRect(0, 549, app.width, 120, fill = 'brown', border = 'black', borderWidth = 2, opacity = 75)
    zombies = app.zombieTypes

    for i in range(len(zombies)):
        ztype = zombies[i]
        x =  50 + i * 120
        y = 569 
        color = 'yellow' if app.zombieType == ztype else None
        if ztype == 'zombie':
            img = app.zombieWalkImages[0]
        elif ztype == 'giantZombie':
            img = app.giantWalkImages[0]
        else:
            img = app.doorZombieImage

        drawImage(img, x + 15, y + 15, align = 'center', width = 50, height = 50)
        drawRect(x - 10, y - 10, 60, 60, border = color, borderWidth = 3, fill = None)
        drawLabel(f'{ztype}-{app.zombieCost[ztype]}', x + 15, y + 65, size = 12, fill = 'black')

def drawBoard(app):
    if app.showGrid:
        for row in range(app.rows + 1):
            y = app.boardTop + row * app.cellHeight
            drawLine(app.boardLeft, y, app.boardLeft + app.boardWidth, y, fill = 'darkGreen', lineWidth = 1)
        for col in range(app.cols + 1):
            x = app.boardLeft + col * app.cellWidth
            drawLine(x, app.boardTop, x, app.boardTop + app.boardHeight, fill = 'darkGreen', lineWidth = 1)

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
                drawImage(imageUrl, x, y, align = 'center', width = app.cellWidth, height = app.cellHeight)
                if app.showHealth:
                    healthPercent = plant.health / plant.maxHealth
                    drawRect(x - 30, y - 40, 60 * healthPercent, 7, fill = 'red')
                    drawRect(x - 30, y - 40, 60, 7, fill = None, border = 'black')

def drawBullets(app):
    for bullet in app.bullets:
        if bullet.get('type') == 'snow':
            drawImage('resource/SnowPea.webp', bullet['x'], bullet['y'], align = 'center', width = 20, height = 20)
        else:
            drawImage('resource/pea.webp', bullet['x'], bullet['y'], align = 'center', width = 20, height = 20)

def drawZombies(app):
    for zombie in app.zombies:
        x, y = zombie.x, zombie.y
        ztype = zombie.type
        if ztype == 'giantZombie':
            if zombie.state == 'walking':
                imageIndex = app.zombieIndex['giantZombie']['walking']
                image = app.giantWalkImages[imageIndex]
                drawImage(image, x, y - 20, align = 'center', width = app.cellWidth + 120, height = app.cellHeight + 100)
            else:
                imageIndex = app.zombieIndex['giantZombie']['eating']
                image = app.giantEatImages[imageIndex]
                drawImage(image, x, y - 50, align = 'center', width = app.cellWidth + 140, height = app.cellHeight + 120)
        elif ztype == 'doorZombie':
            drawImage(app.doorZombieImage, x, y, align = 'center', width = app.cellWidth + 30, height = app.cellHeight + 10)
        else:
            if zombie.state == 'walking':
                imageIndex = app.zombieIndex['zombie']['walking']
                image = app.zombieWalkImages[imageIndex]
                drawImage(image, x, y, align = 'center', width = app.cellWidth + 60, height = app.cellHeight + 20)
            else:
                imageIndex = app.zombieIndex['zombie']['eating']
                image = app.zombieEatImages[imageIndex]
                drawImage(image, x, y, align = 'center', width = app.cellWidth, height = app.cellHeight)
        if app.showHealth:
            healthPercent = zombie.health / zombie.maxHealth
            drawRect(x - 25, y - 55, 50 * healthPercent, 7, fill = 'red')
            drawRect(x - 25, y - 55, 50, 7, fill = None, border = 'black')

def drawMowers(app):
    for mower in app.mowers:
        if mower.active:
            imageUrl = app.mowerImages[mower.index]
            drawImage(imageUrl, mower.x, mower.y, align = 'center', width = 50, height = 40)

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
    selectorWidth = app.width
    selectorHeight = 120
    selectorLeft = 0
    selectorTop = 549
    if (selectorLeft <= x <= selectorLeft + selectorWidth) and (selectorTop <= y <= selectorTop + selectorHeight):
        for i, ztype in enumerate(app.zombieTypes):
            zombieX = selectorLeft + 50 + i * 120
            zombieY = selectorTop + 20
            if (zombieX - 25 <= x <= zombieX + 25) and (zombieY - 25 <= y <= zombieY + 25):
                app.zombieType = ztype
                return
        return
    if app.gameOver:
        return
    if app.paused:
        return
    
    rightColX = app.boardLeft + app.boardWidth
    if x > rightColX and app.boardTop <= y < app.boardTop + app.boardHeight:
        row = int((y - app.boardTop) // app.cellHeight)
        col = app.cols + 1
        if 0 <= row < app.rows:
            ztype = app.zombieType
            zcost = app.zombieCost.get(ztype, 100)
            if app.zombiePoints >= zcost:
                zx = app.boardLeft + col * app.cellWidth + app.cellWidth // 2
                zy = app.boardTop + row * app.cellHeight + app.cellHeight // 2
                zombie = Zombie(zx, zy, row, ztype)
                app.zombies.append(zombie)
                app.zombiePoints -=  zcost

def onKeyPress(app, key):
    if app.commandMode:
        if key == 'escape':
            app.commandMode = False
            app.commandString = ""
        elif key == 'tab':
            if app.commandString.startswith("summon-"):
                com = app.commandString.split("-")
                if len(com) == 2:
                    currentType = com[1]
                    types = ['sunflower', 'peashooter', 'wallnut', 'repeater', 'snowPeaShooter', 'potato', 'zombie', 'giantZombie', 'doorZombie']
                    if currentType in types:
                        currentIndex = types.index(currentType)
                        nextIndex = (currentIndex + 1) % len(types)
                    else:
                        nextIndex = 0
                    app.commandString = f"summon-{types[nextIndex]}"
        elif key == 'backspace':
            if app.commandString:
                app.commandString = app.commandString[:-1]
        elif key == 'enter':
            executeCommand(app, app.commandString)
            app.commandMode = False
            app.commandString = ""
        elif len(key) == 1:
            app.commandString += key
        
    else:
        if key == '/':
            app.commandMode = True
            app.commandString = ""
        elif key == 'r' or key == 'R':
            app.mode = 'menu'
            resetGame(app)
        elif key == 'p' or key == 'P':
            app.paused = not app.paused
        elif key == 's' or key == 'S':
            app.showGrid = not app.showGrid
        elif key == 'h' or key == 'H':
            app.showHealth = not app.showHealth
        elif key == 'left':
            currentIndex = app.zombieTypes.index(app.zombieType)
            app.zombieType = app.zombieTypes[(currentIndex - 1) % len(app.zombieTypes)]
        elif key == 'right':
            currentIndex = app.zombieTypes.index(app.zombieType)
            app.zombieType = app.zombieTypes[(currentIndex + 1) % len(app.zombieTypes)]
        elif key == 'up':
            app.mage.targetY -=  app.cellHeight
            if app.mage.targetY < app.boardTop + app.cellHeight // 2:
                app.mage.targetY = app.boardTop + app.cellHeight // 2
        elif key == 'down':
            app.mage.targetY +=  app.cellHeight
            if app.mage.targetY > app.boardTop + app.boardHeight - app.cellHeight // 2:
                app.mage.targetY = app.boardTop + app.boardHeight - app.cellHeight // 2
        elif key == 'enter':
            ztype = app.zombieType
            zcost = app.zombieCost.get(ztype, 100)
            if app.zombiePoints >= zcost:
                app.mage.summoning = True
                app.mage.summonTimer = 0
                zombie = Zombie(app.mage.x, app.mage.y, app.mage.row, ztype)
                app.zombies.append(zombie)
                app.zombiePoints -=  zcost

def spawnPlant(app):
    emptyPs = [(row, col) for row in range(app.rows) for col in range(app.cols) if app.board[row][col] is None]
    
    if emptyPs:
        plantTypes = {'sunflower': 0.25,'peashooter': 0.2, 'wallnut': 0.2, 'repeater': 0.1, 'snowPeaShooter': 0.15, 'potato': 0.1}
        #plantTypes = {'potato': 1}
        #plantTypes = {'repeater': 1}
        #plantTypes = {'snowPeaShooter': 1}

        #function idea from https://blog.csdn.net/qq_44810930/article/details/139437577
        selectedPlantType = random.choices(list(plantTypes.keys()), weights = list(plantTypes.values()))[0]
        #print(selectedPlantType)
        if selectedPlantType == 'sunflower':
            validPs = [(row, col) for (row, col) in emptyPs if col in (0, 1)]
            if validPs:
                row, col = random.choice(validPs)
                newPlant = Plant(row, col, selectedPlantType)
                app.board[row][col] = newPlant
        elif selectedPlantType == 'wallnut':
            validPs = []
            for row, col in emptyPs:
                for checkCol in range(col - 1, -1, -1):
                    plantBehind = app.board[row][checkCol]
                    if plantBehind and plantBehind.type != 'wallnut':
                        validPs.append((row, col))
                        break
            if validPs:
                # from https://blog.csdn.net/qq_44810930/article/details/139437577
                row, col = random.choice(validPs)
                newPlant = Plant(row, col, selectedPlantType)
                app.board[row][col] = newPlant
                
        else:
            # from https://blog.csdn.net/qq_44810930/article/details/139437577
            row, col = random.choice(emptyPs)
            newPlant = Plant(row, col, selectedPlantType)
            app.board[row][col] = newPlant

def onStep(app):
    if app.paused or app.gameOver:
        return
    app.mage.timer +=  1
    if app.mage.timer >= app.mage.speed:
        app.mage.timer = 0
        if not app.mage.summoning:
            app.mage.index = (app.mage.index + 1) % len(app.mage.images)
    if app.mage.summoning:
        app.mage.summonTimer +=  1
    #Let GPT to help me solve to problem that the dark mage would keep moving up and down when it is in the col 1,2,3
    #It told me to add a 2 pixels of tolerance to avoid minor jitter
    if app.mage.y < app.mage.targetY - 2:
        app.mage.y +=  app.mage.moveSpeed
    elif app.mage.y > app.mage.targetY + 2:
        app.mage.y -=  app.mage.moveSpeed
    else:
        app.mage.y = app.mage.targetY
    app.mage.row = int((app.mage.y - app.boardTop) // app.cellHeight)
    if app.mage.row < 0:
        app.mage.row = 0
    elif app.mage.row >= app.rows:
        app.mage.row = app.rows - 1

    app.plantCount +=  1
    if app.plantCount >= app.plantSpawnNum:
        app.plantCount = 0
        spawnPlant(app)
    #plantIndex
    app.plantIndex['sunflower'] = (app.plantIndex['sunflower'] + 1) % 36
    app.plantIndex['peashooter'] = (app.plantIndex['peashooter'] + 1) % 77
    app.plantIndex['wallnut'] = (app.plantIndex['wallnut'] + 1) % 44
    app.plantIndex['repeater'] = (app.plantIndex['repeater'] + 1) % 49
    app.plantIndex['snowPeaShooter'] = (app.plantIndex['snowPeaShooter'] + 1) % 25
    app.plantIndex['potato'] = (app.plantIndex['potato'] + 1) % 29
    #zombieIndex   
    app.zombieIndex['zombie']['walking'] = (app.zombieIndex['zombie']['walking'] + 1) % 46
    app.zombieIndex['zombie']['eating'] = (app.zombieIndex['zombie']['eating'] + 1) % 40
    app.zombieIndex['giantZombie']['walking'] = (app.zombieIndex['giantZombie']['walking'] + 1) % 161
    app.zombieIndex['giantZombie']['eating'] = (app.zombieIndex['giantZombie']['eating'] + 1) % 38

    app.plantTimer +=  1

    if app.plantTimer >= app.plantRate:
        app.plantTimer = 0
        plantAttack(app)

    updateGame(app)
    checkCollisions(app)
    checkGameState(app)

def updateGame(app):
    for bullet in app.bullets.copy():
        bullet['x'] +=  4
        if bullet['x'] > app.boardLeft + app.boardWidth + 60:
            app.bullets.remove(bullet)
    for zombie in app.zombies.copy():
        if zombie.slowed:
            zombie.slowTimer -=  1
            if zombie.slowTimer <= 0:
                zombie.slowed = False
                if zombie.type == 'zombie':
                    zombie.speed = 0.7
                elif zombie.type == 'giantZombie':
                    zombie.speed = 0.5
                elif zombie.type == 'doorZombie':
                    zombie.speed = 0.6
                #print(f"Slow ended, speed:{zombie.speed}")
        
        zombie.x -=  zombie.speed
        if zombie.x < app.boardLeft - 60:
            app.gameOver = True
    for mower in app.mowers:
        if mower.moving and mower.active:
            mower.x +=  5
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
    for bullet in app.bullets.copy():
        for zombie in app.zombies.copy():
            if (abs(bullet['x'] - zombie.x) < 25 and abs(bullet['y'] - zombie.y) < 35):
                zombie.health -=  bullet['damage']
                
                if bullet.get('type') == 'snow' and not zombie.slowed:
                    #print(f"before: {zombie.speed}")
                    zombie.slowed = True
                    zombie.slowTimer = 180  
                    if zombie.type == 'zombie':
                        zombie.speed = 0.35  
                    elif zombie.type == 'giantZombie':
                        zombie.speed = 0.25
                    elif zombie.type == 'doorZombie':
                        zombie.speed = 0.3 
                    #print(f"after: {zombie.speed}") 
                
                if bullet in app.bullets:
                    app.bullets.remove(bullet)
                if zombie.health <= 0:
                    app.zombies.remove(zombie)
                break

    for zombie in app.zombies.copy():
        attacked = False
        for row in range(app.rows):
            for col in range(app.cols):
                plant = app.board[row][col]
                if plant and zombie.row == row:
                    plantX = app.boardLeft + col * app.cellWidth + app.cellWidth // 2
                    if abs(zombie.x - plantX) < 40:
                        plant.health -=  zombie.damage
                        zombie.speed = 0
                        zombie.state = 'eating'
                        attacked = True
                        if plant.health <= 0:
                            app.board[row][col] = None
                            app.zombiePoints +=  120
                        if plant.type == 'potato':
                            zombiesToRemove = []
                            x = app.boardLeft + col * app.cellWidth + app.cellWidth // 2
                            for z in app.zombies:
                                if z.row == row and abs(z.x - x) < 60:
                                    zombiesToRemove.append(z)
                            for z in zombiesToRemove:
                                app.zombies.remove(z)
                            app.board[row][col] = None
                            break

        if not attacked:
            if zombie.type == 'zombie':
                if not zombie.slowed:
                    zombie.speed = 0.7
            elif zombie.type == 'giantZombie':
                if not zombie.slowed:
                    zombie.speed = 0.5
            elif zombie.type == 'doorZombie':
                if not zombie.slowed:
                    zombie.speed = 0.6
            zombie.state = 'walking'

def plantAttack(app):
    for row in range(app.rows):
        for col in range(app.cols):
            plant = app.board[row][col]
            if plant and (plant.type == 'peashooter' or plant.type == 'repeater' or plant.type == 'snowPeaShooter'):
                for zombie in app.zombies:
                    if zombie.row == row and zombie.x > app.boardLeft + col * app.cellWidth:
                        bulletX = app.boardLeft + col * app.cellWidth + app.cellWidth // 2
                        bulletY = app.boardTop + row * app.cellHeight + app.cellHeight // 2
                        if plant.type == 'peashooter':
                            app.bullets.append({
                                'x': bulletX,
                                'y': bulletY,
                                'row': row,
                                'damage': 20,
                                'type': 'normal'
                            })
                        elif plant.type == 'repeater':
                            app.bullets.append({
                                'x': bulletX,
                                'y': bulletY,
                                'row': row,
                                'damage': 15,
                                'type': 'normal'
                            })
                            app.bullets.append({
                                'x': bulletX + 10,
                                'y': bulletY,
                                'row': row,
                                'damage': 15,
                                'type': 'normal'
                            })
                        elif plant.type == 'snowPeaShooter':
                            app.bullets.append({
                                'x': bulletX,
                                'y': bulletY,
                                'row': row,
                                'damage': 18,
                                'type': 'snow'
                            })
                        break

def checkGameState(app):
    for zombie in app.zombies:
        if zombie.x < app.boardLeft - 60:
            app.gameOver = True
            app.gameWon = True
            return
    if len(app.zombies) == 0 and app.zombiePoints < 100:
        app.gameOver = True
        app.gameWon = False
        return

def resetGame(app):
    app.gameOver = False
    app.gameWon = False
    app.paused = False
    app.zombiePoints = 2000
    app.board = [[None] * app.cols for _ in range(app.rows)]
    app.bullets = []
    app.zombies = []
    app.plantCount = 0
    app.plantTimer = 0
    app.plantIndex = {
        'sunflower': 0,
        'peashooter': 0,
        'wallnut': 0,
        'repeater': 0,
        'snowPeaShooter': 0,
        'potato': 0
    }
    app.zombieIndex = {
        'zombie': {'walking': 0, 'eating': 0},
        'giantZombie': {'walking': 0, 'eating': 0}
    }
    app.showHealth = False
    app.mowers = [Mower(app, r) for r in range(app.rows)]
    app.mage = Mage()

def executeCommand(app, command):
    if command.startswith("summon-"):
        com = command.split("-")
        if len(com) == 4:
            _, type, row, col = com
            row = int(row)
            col = int(col)
            if type in app.plantImages:
                if 0 <= row < app.rows and 0 <= col < app.cols:
                    plant = Plant(row, col, type)
                    app.board[row][col] = plant
            elif type in app.zombieTypes:
                if 0 <= row < app.rows:
                    x = app.boardLeft + col * app.cellWidth + app.cellWidth // 2
                    y = app.boardTop + row * app.cellHeight + app.cellHeight // 2
                    zombie = Zombie(x, y, row, type)
                    app.zombies.append(zombie)
    elif command == "clear":
        app.board = [[None] * app.cols for _ in range(app.rows)]
        app.zombies = []
    elif command == "help":
        print("""
        /summon-<type>-<row>-<col> (type: sunflower, peashooter, wallnut, repeater, snowPeaShooter, potato, zombie, giantZombie, doorZombie)
        /clear (clear all plants and zombies)
        /help (show this help)
        /tab (cycle through plant and zombie types)
        """)
                    
def main():
    runApp(width = 900, height = 650)

if __name__ == '__main__':
    main() 