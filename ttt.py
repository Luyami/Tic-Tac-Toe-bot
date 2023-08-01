import pygame
import numpy

import copy
import time

import random

pygame.init()

WIDTH = 400
HEIGHT = 400
mainScreen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe")

WHITE = (255, 255, 255)
BROWN = (202, 164, 114)
RED = (194, 24, 7)
BLACK = (0, 0, 0)

#Util
def listSum(l, s, e):
    if (e > len(l)):
        raise BaseException("Invalid end index")
    
    sum = 0

    for i in range(s, e):
        sum += l[i]
    
    return sum

#Represent each rectangle which can be filled with X's and O's. Each cell tells the position of said rectangle and which element is filling it (O or X)
class Cell():
    def updateValue(self, val):
        if (val != 'O' and val != 'X'):
            self.value = 'E'
        else: self.value = val

    def __init__(self, rect, startValue):
        self.rect = rect
        self.updateValue(startValue)

class Node():
    def __init__(self, level, cells, turn = 'X', parent = list(), children = list()):
        self.cells = cells
        self.level = level
        self.turn = turn
        self.parent = parent
        self.children = children

        self.value = None

class BOT():
    #Based on minimax algorithm

    #Value table:
    XWON = 1
    OWON = -1
    DRAW = 0

    #Tic-Tac-Toe board:
    #{0, 1, 2}
    #{3, 4, 5}
    #{6, 7, 8}
    #Where each number is the index of 'cells' array

    def __init__(self, startsFirst, turnIdentifier):
        self.startsFirst = startsFirst
        self.turnIdentifier = turnIdentifier

        self.root = Node(0, BOT.__generateEmpty())
        
        self.nodes = list()
        self.nodes.append(self.root)

        self.nodesQuantity = [1] #Stores the quantity of nodes in each level (index represents the level)

    # **PUBLIC FUNCTIONS**

    def start(self):
        print('Initializing bot...')
        start = time.process_time()

        self.__generateGameTree()
        self.__generateAllNodeValues()

        end = time.process_time()
        print(f'Initialization time: {end - start}')

    #Chooses a Tic-Tac-Toe cell index based on the best move
    def choose(self, currentGrid):
        currentGrid = BOT.__cellsGridToString(currentGrid)

        currentLevel = 9 - currentGrid.count('E')

        #Setting the indexes range of current level nodes to find the node we are goint to work on
        sIndex = listSum(self.nodesQuantity, 0, currentLevel)
        eIndex = sIndex + self.nodesQuantity[currentLevel]

        #Finding the node that matches currentGrid
        currentNode = None
        for i in range(sIndex, eIndex):
            node = self.nodes[i]
            cellsString = BOT.__codedCellsToString(node.cells)

            if (cellsString == currentGrid):
                currentNode = node

                break
        
        #Finding best move
        winMove = None
        bestMoves = list()
        drawMoves = list()

        for c in currentNode.children:
            if (c.value == BOT.__getTurnValue(self.turnIdentifier)):
                #Win move! the best move of all
                if (len(c.children) == 0): #len(c.children) == 0 means that it is a win move
                    winMove = BOT.__codedCellsToString(c.cells)
                    break
                #Optimal move, given current context
                bestMoves.append(BOT.__codedCellsToString(c.cells))

            #Draw move
            elif (len(bestMoves) == 0 and c.value == BOT.DRAW): drawMoves.append(BOT.__codedCellsToString(c.cells))

        #Win move is priorized (obviously!)
        if (winMove != None):
            return BOT.__highlightCellsStringDiff(currentGrid, winMove).find('D') #Win!

        #If win is not possible... we randomize our bot a little (; (but we always want the optimal moves! let's not make a dumb bot O:)
        if (len(bestMoves) > 0):
            randIndex = random.randint(0, len(bestMoves) - 1)
            diff = BOT.__highlightCellsStringDiff(currentGrid, bestMoves[randIndex])
        elif (len(drawMoves) > 0):
            randIndex = random.randint(0, len(drawMoves) - 1)
            diff = BOT.__highlightCellsStringDiff(currentGrid, drawMoves[randIndex])
        else:
            randIndex = random.randint(0, len(currentNode.children) - 1)
            totallyRandomScenario = BOT.__codedCellsToString(currentNode.children[randIndex].cells) #There's nothing we can do! our bot is in danger!!!! but it will never will hahaha
            diff = BOT.__highlightCellsStringDiff(currentGrid, totallyRandomScenario)
        
        return diff.find('D')

    # **PRIVATE FUNCTIONS**

    # **Coded Cells** set of cells represented by a character numpy.array
    def __generateEmpty():
        return numpy.array(['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E'])
    
    def __cellsGridToString(cellsGrid):
        cells = ''

        for c in cellsGrid:
            cells += c.value

        return cells
    
    def __codedCellsToString(codedCells):
        cells = ''

        for c in codedCells:
            cells += c

        return cells

    #Example: s1 = 'EEEEEEEEE', s2 = 'EXEEEEEEE', output = '-D-------', where 'D' indicates the diff
    def __highlightCellsStringDiff(s1, s2):
        if (len(s1) != len(s2)): raise BaseException("Must be of same length")

        diffString = ''

        for i in range(0, len(s1)):
            if (s1[i] == s2[i]): diffString += '-'
            else: diffString += 'D'
        
        return diffString

    def __getNextTurn(currentTurn):
        if (currentTurn == 'X'):
            return 'O'
        else:
            return 'X'
    
    def __getTurnValue(currentTurn):
        if (currentTurn == 'X'): return BOT.XWON
        else: return BOT.OWON

    #Bounded to checkWin function
    def __isWinTrio(c1, c2, c3, turn):
        if (c1 == turn):
            if (c1 == c2 and c2 == c3): return True

    def __checkWin(cells, turn):
        cs = cells
        
        for i in range(0, 3):
            #Horizontal
            c1, c2, c3 = cs[0 + i * 3], cs[1 + i * 3], cs[2 + i * 3]
            if (BOT.__isWinTrio(c1, c2, c3, turn)): return (c1, c2, c3)

            #Vertical
            c1, c2, c3 = cs[i], cs[i + 3], cs[i + 6]
            if (BOT.__isWinTrio(c1, c2, c3, turn)): return (c1, c2, c3)
            
        #Main Diagonal
        if (BOT.__isWinTrio(cs[0], cs[4], cs[8], turn)): return (cs[0], cs[4], cs[8])

        #Secondary Diagonal
        if (BOT.__isWinTrio(cs[2], cs[4], cs[6], turn)): return (cs[2], cs[4], cs[6])

        return None

    def __isDraw(cells, shouldCheckWin = False):
        allCellsFilled = True

        for c in cells:
            if (c == 'E'): 
                allCellsFilled = False
                break

        if (shouldCheckWin):
            return allCellsFilled and BOT.__checkWin(cells, 'X') == None and BOT.__checkWin(cells, 'O') == None
        else:
            return allCellsFilled

    def __generateGameTree(self):
        turn = None

        if (self.startsFirst): turn = self.turnIdentifier
        else: turn = 'X' if (self.turnIdentifier == 'O') else 'O'

        self.nodes[0].turn = turn

        pLevel = 0 #Parent level

        while (pLevel <= 8): #8 is the max parent level possible, because tic-tac-toe has 9 squares
            turn = BOT.__getNextTurn(turn)
            
            totalChildren = 0

            for i in range(0, self.nodesQuantity[pLevel]): #Looping through each node of current parent level
                parentNode = self.nodes[listSum(self.nodesQuantity, 0, pLevel) + i]

                if (parentNode.value != None): continue

                freePositionLastIndex = -1

                for k in range(0, 9 - pLevel): #There is a maximum of (9 - pLevel) possibilities each level
                    for cellIndex in range(0, 9):
                        if (parentNode.cells[cellIndex] != 'E'): continue
                        
                        if (cellIndex > freePositionLastIndex):
                            cells = numpy.copy(parentNode.cells)
                            cells[cellIndex] = BOT.__getNextTurn(turn)

                            node = Node(pLevel + 1, cells, turn, parentNode, list())
                            parentNode.children.append(node)
                            self.nodes.append(node)
                            totalChildren += 1

                            freePositionLastIndex = cellIndex

                            #Filling terminal node's values (if possible)
                            if (BOT.__checkWin(cells, BOT.__getNextTurn(turn))):
                                node.value = BOT.__getTurnValue(BOT.__getNextTurn(turn))
                            elif (BOT.__isDraw(cells, False)):
                                node.value = BOT.DRAW

                            break
            
          
            self.nodesQuantity.append(totalChildren)
   
            pLevel += 1

            print(self.nodesQuantity)

    def __generateAllNodeValues(self):
        for level in range(len(self.nodesQuantity) - 2, -1, -1):
            sIndex = listSum(self.nodesQuantity, 0, level)

            for nodeIndex in range(sIndex, sIndex + self.nodesQuantity[level]):
                node = self.nodes[nodeIndex]
                
                if (node.value != None): continue #Terminal nodes are already valued

                drawScenarios = 0
                value = None

                #Checking if node.turn has a chance to win
                for child in node.children:
                    turnValue = BOT.__getTurnValue(node.turn)

                    if (child.value == 0): drawScenarios += 1
                    elif (child.value == turnValue): 
                        value = turnValue

                        break
    
                if (value == None):
                    #Checking draws and whether next turn has chances to win or not
                    if (drawScenarios > 0): value = BOT.DRAW
                    else: value = BOT.__getTurnValue(BOT.__getNextTurn(node.turn))
                
                node.value = value

class Game():
    def __init__(self, playerIdentifier, botIdentifier, first):
        self.isActive = True

        self.cells = list()

        self.botIdentifier = botIdentifier
        self.playerIdentifier = playerIdentifier
        self.first = first

        self.__drawGrid()

        #Initializing bot...
        self.bot = BOT(self.botIdentifier == first, self.botIdentifier)
        self.bot.start()

    # **PUBLIC STATIC FUNCTIONS**

    def getNextTurn(currentTurn):
        if (currentTurn == 'X'):
            return 'O'
        else:
            return 'X'

    def checkWin(cells, turn):
        cs = cells

        for i in range(0, 3):
            #Horizontal
            c1, c2, c3 = cs[0 + i * 3], cs[1 + i * 3], cs[2 + i * 3]
            if (Game.__isWinTrio(c1, c2, c3, turn)): return (c1, c2, c3)

            #Vertical
            c1, c2, c3 = cs[i], cs[i + 3], cs[i + 6]
            if (Game.__isWinTrio(c1, c2, c3, turn)): return (c1, c2, c3)
            
        #Main Diagonal
        if (Game.__isWinTrio(cs[0], cs[4], cs[8], turn)): return (cs[0], cs[4], cs[8])

        #Secondary Diagonal
        if (Game.__isWinTrio(cs[2], cs[4], cs[6], turn)): return (cs[2], cs[4], cs[6])

        return None

    def isDraw(cells, shouldCheckWin = False):
        allCellsFilled = True

        for c in cells:
            if (c.value == 'E'): 
                allCellsFilled = False
                break

        if (shouldCheckWin):
            return allCellsFilled and Game.checkWin(cells, 'X') == None and Game.checkWin(cells, 'O') == None
        else:
            return allCellsFilled

    # **PRIVATE FUNCTIONS**

    #Draws tic-tac-toe grid
    def __drawGrid(self):
        mainScreen.fill(BROWN)

        #Horizontal lines
        pygame.draw.line(mainScreen, WHITE, (0, HEIGHT/3 * 1), (WIDTH, HEIGHT/3 * 1), 5)
        pygame.draw.line(mainScreen, WHITE, (0, HEIGHT/3 * 2), (WIDTH, HEIGHT/3 * 2), 5)

        #Vertical lines
        pygame.draw.line(mainScreen, WHITE, (WIDTH/3 * 1, 0), (WIDTH/3 * 1, HEIGHT), 5)
        pygame.draw.line(mainScreen, WHITE, (WIDTH/3 * 2, 0), (WIDTH/3 * 2, HEIGHT), 5)

        pygame.display.flip()

    def __getCellsRect(self):
        rectWidth = WIDTH/3
        rectHeight = HEIGHT/3

        cells = list()
        for x in range(0, 3):
            for y in range(0, 3):
                cells.append(
                    pygame.Rect(WIDTH/3 * x, HEIGHT/3 * y, rectWidth, rectHeight)
                )
        
        return cells
    
    def __getCellFromPoint(self, x, y):
        for c in self.cells:
            if (x >= c.rect.topleft[0] and x < c.rect.topright[0]):
                if (y >= c.rect.topleft[1] and y < c.rect.bottomleft[1]):
                    return c
                
    def __drawX(self, cell):
        xWidth = cell.rect.width/4
        xHeight = cell.rect.height/4

        pygame.draw.line(mainScreen, BLACK, (cell.rect.center[0] - xWidth, cell.rect.center[1] + xHeight), (cell.rect.center[0] + xWidth, cell.rect.center[1] - xHeight), 3)
        pygame.draw.line(mainScreen, BLACK, (cell.rect.center[0] + xWidth, cell.rect.center[1] + xHeight), (cell.rect.center[0] - xWidth, cell.rect.center[1] - xHeight), 3)

    def __drawO(self, cell):
        pygame.draw.circle(mainScreen, BLACK, cell.rect.center, (cell.rect.width + cell.rect.height)/6, 3)

    #Bounded to checkWin function
    def __isWinTrio(c1, c2, c3, turn):
        if (c1.value == turn):
            if (c1.value == c2.value and c2.value == c3.value): return True

    def __reset(self):
        self.isActive = True

        #Setting cells rects
        self.cells = list()

        for c in self.__getCellsRect():
            self.cells.append(Cell(c, None))

        self.__drawGrid()
        pygame.display.flip()

    # **PUBLIC FUNCTIONS**

    def start(self):
        self.__reset()

        turn = self.first

        while self.isActive:
            mouseDown = False

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.isActive = False
                if e.type == pygame.MOUSEBUTTONDOWN:
                    mouseDown = True

            shouldProcessPlayerMove = mouseDown and pygame.mouse.get_pressed()[0] == True and turn == self.playerIdentifier
            if (shouldProcessPlayerMove or turn == self.botIdentifier):
                cell = None
            
                if (turn == self.playerIdentifier):
                    mouseX, mouseY = pygame.mouse.get_pos()
                    cell = self.__getCellFromPoint(mouseX, mouseY)
                else: #Bot's turn
                    cell = self.cells[self.bot.choose(self.cells)]
                    
                #Filling cell
                if (cell.value == 'E'):
                    if (turn == 'X'):
                        self.__drawX(cell)
                    else:
                        self.__drawO(cell)
                    cell.updateValue(turn)
                        
                    pygame.display.flip()

                    #Checking win
                    winTrio = Game.checkWin(self.cells, turn) 
                    if (winTrio != None):
                        pygame.draw.line(
                            mainScreen, RED,
                            (winTrio[0].rect.center[0], winTrio[0].rect.center[1]), (winTrio[2].rect.center[0], winTrio[2].rect.center[1]), 4
                        )
                        pygame.display.flip()

                        self.isActive = False
                        pygame.time.wait(3000)
                    #Checking draw
                    elif (Game.isDraw(self.cells)):
                        self.isActive = False
                        pygame.time.wait(1500)

                    turn = Game.getNextTurn(turn)

#Asking user to choose who starts first
shouldPlayStart = False

info_font = pygame.font.Font('freesansbold.ttf', 32)
info_text = info_font.render("Want to start first?", True, WHITE)

yes_font = pygame.font.Font('freesansbold.ttf', 32)
yes_text = yes_font.render(" Yes ", True, WHITE)

no_font = pygame.font.Font('freesansbold.ttf', 32)
no_text = no_font.render(" No ", True, WHITE)

i_rect = info_text.get_rect(center=(WIDTH/2, 60))
y_rect = yes_text.get_rect(center=(WIDTH/2 - 60, HEIGHT/2))
n_rect = no_text.get_rect(center=(WIDTH/2 + 60, HEIGHT/2))

mainScreen.blit(info_text, i_rect)
mainScreen.blit(yes_text, y_rect)
mainScreen.blit(no_text, n_rect)

pygame.display.flip()

chose = False
while not chose:
    for e in pygame.event.get():
        if (e.type == pygame.QUIT): chose = True
        if (e.type == pygame.MOUSEBUTTONDOWN):
            if (y_rect.collidepoint(e.pos)):
                shouldPlayStart = True
                chose = True

            elif (n_rect.collidepoint(e.pos)):
                shouldPlayStart = False
                chose = True

g = Game('X', 'O', 'X' if (shouldPlayStart) else 'O')

while True:
    g.start()
