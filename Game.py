from Matrix import *
import random

class GameBoard:
    def __init__(self, game, player):
        self.game = game
        self.player = player

        self.reset()

    def reset(self):
        self.game.reset()
        self.player.reset()
        
        self.gameOver = False

    def next(self):
        if not self.gameOver:
            playerInp = self.player.next(self.game)
            print playerInp

            gameOut = self.game.next(playerInp)
            if gameOut == None:
                self.gameOver = True
                return 1
            else:
                return gameOut
        else:
            return self.game.gameOver()
            
    def getMatrix(self):
        return self.game.getMatrix()

    def getWidth(self):
        return self.game.getWidth()

    def getHeight(self):
        return self.game.getHeight()

    def __str__(self):
        return str(self.game)


class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.reset()

    def reset(self):
        self.resetMatrix()

    def resetMatrix(self):
        self.matrix = [[0 for i in range(self.height)] for j in range(self.width)]

    def next(self):
        return None

    def gameOver(self):
        return None

    def getMatrix(self):
        return self.matrix

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def __str__(self):
        strArray = []
        for row in self.matrix:
            strArray.append(str(row))
        return '\n'.join(strArray)


class SnakeGame(Game):
    def __init__(self, width, height):
        Game.__init__(self, width, height)

        self.gameOverScreens = 5
        
        self.moves = {'u': (0, 1),
                      'd': (0, -1),
                      'l': (-1, 0),
                      'r': (1, 0)}
        
    def reset(self):
        Game.reset(self)

        self.gameOverCounter = 0
        
        self.snake = [(1,1), (1,2)]
        self.dir = 'd'

        self.dropFood()
        
        self.updateMatrix()


    def next(self, inp):
        if inp not in self.moves.keys():
            inp = self.dir
        else:
            self.dir = inp
            
        dx, dy = self.moves[inp]
            
        oldX, oldY = self.snake[0]
        newX, newY = oldX + dx, oldY + dy

        if newX == self.food[0] and newY == self.food[1]:
            self.growSnake(newX, newY)
            self.dropFood()
        else:
            self.moveSnake(newX, newY)

        if self.noneIfInvalid() == None:
            return None
        else:
            self.updateMatrix()
            return 1

    # Called when the game ends, and will continue to be called until this returns None
    def gameOver(self):
        if self.gameOverCounter < self.gameOverScreens:
            if self.gameOverCounter % 2 == 0:
                self.endMatrix = self.matrix
                self.resetMatrix()
            else:
                self.matrix = self.endMatrix
            
            self.gameOverCounter += 1
            
            return 1
        else:
            return None

    def updateMatrix(self):
        self.resetMatrix()
        
        for x, y in self.snake + [self.food]:
            self.matrix[x][y] = 1

    def dropFood(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        
        self.food = (x, y)
            
    def noneIfInvalid(self):
        for i in range(len(self.snake)):
            x, y = self.snake[i]
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return None
            
            for j in range(i + 1, len(self.snake)):
                if self.snake[i] == self.snake[j]:
                    return None

        return 1
        
    def growSnake(self, x, y):
        self.snake.insert(0, (x, y))

    def moveSnake(self, x, y):
        self.snake.insert(0, (x, y))
        self.snake.pop()

    def getValidMoves(self):
        if self.dir == 'u':
            invalid = 'd'
        elif self.dir == 'd':
            invalid = 'u'
        elif self.dir == 'l':
            invalid = 'r'
        elif self.dir == 'r':
            invalid = 'l'

        return [move for move in self.moves.keys() if move != invalid]

    def moveToCoords(self, move):
        return self.moves[move]

    def coordsToMove(self, dx, dy):
        isXGreater = abs(dx) > abs(dy)
        
        if dx > 0:
            dx = 1
        elif dx < 0:
            dx = -1
        else:
            dx = 0
            
        if dy > 0:
            dy = 1
        elif dy < 0:
            dy = -1
        else:
            dy = 0

        if dx != 0 and dy != 0:
            if isXGreater:
                dy = 0
            else:
                dx = 0
        print dx, dy
            
        for move, coords in self.moves.items():
            if (dx, dy) == coords:
                return move
            
        return None

    def getAllMoves(self):
        return self.moves

    def getSnake(self):
        return self.snake

    def getFood(self):
        return self.food

    def getSnakeDirection(self):
        return self.dir


class Player:
    def reset(self):
        pass

    def next(self, game):
        return None

class RandomSnakePlayer(Player):
    def next(self, game):
        moves = game.getValidMoves()
        
        return moves[random.randint(0, len(moves) - 1)]

class DumbSnakePlayer(Player):
    def __init__(self, p):
        self.p = p
        
    def next(self, game):
        validMoves = game.getValidMoves()
        headX, headY = game.getSnake()[0]
        foodX, foodY = game.getFood()

        dx, dy = foodX - headX, foodY - headY
        print dx, dy
        
        goodMove = game.coordsToMove(dx, dy)

        if goodMove in validMoves and random.random() < self.p:
            return goodMove
        else:
            return validMoves[random.randint(0, len(validMoves) - 1)]

def test():
    game = SnakeGame(6, 6)
    player = DumbSnakePlayer(1)
    board = GameBoard(game, player)
    done = False
    while done != None:
        print board
        print
        done = board.next()
        
