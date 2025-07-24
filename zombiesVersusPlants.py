from cmu_graphics import *

def onAppStart(app):
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

def redrawAll(app):
    drawImage("garden.jpg", 0, 0)
    drawLabel('Zombies vs Plants', app.width//2, 40, size=40, fill='darkgreen', bold=True)
    drawBoard(app)

def drawBoard(app):
    for row in range(app.rows + 1):
        y = app.boardTop + row * app.cellHeight
        drawLine(app.boardLeft, y, app.boardLeft + app.boardWidth, y, fill='darkGreen', lineWidth=1)
    for col in range(app.cols + 1):
        x = app.boardLeft + col * app.cellWidth
        drawLine(x, app.boardTop, x, app.boardTop + app.boardHeight, fill='darkGreen', lineWidth=1)

def main():
    runApp(width=900, height=650)

if __name__ == '__main__':
    main() 