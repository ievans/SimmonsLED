#!/usr/bin/env python

# Arduino LED matrix control for the Simmons LED Gym Display
# By Isaac Evans
# ine@mit.edu
# 3/25/2011

import LEDCharacters

def applyTransform(perm, position):
    new = [0]*len(position)
    for i, element in enumerate(position):
        new[perm[i]] = element
    return new

class MatrixScrollRepeater():
    def __init__(self, repeats, iSM):
        self.repeats = repeats
        self.SM = iSM

    def next(self):
        if self.SM.next() == None:
            if self.repeats == 0:              
                return None
            else:
                self.repeats -= 1
                self.SM.reset()
        return 1

    def getMatrix(self, arduino = False):
        if arduino:
            return self.SM.getArduinoList()
        return self.SM.matrix

    def getWidth(self):
        return self.SM.MATRIX_WIDTH

    def getHeight(self):
        return self.SM.MATRIX_HEIGHT
    
    def getText(self):
        return self.SM.str

    def __repr__(self):
        return str(self.SM)

class MatrixScroller():
    def __init__(self, message, width, height):
        self.MATRIX_WIDTH = width
        self.MATRIX_HEIGHT = height
        self.str = message
        self.index = 0
        self.charIndex = 0
        self.matrix = [[0]*self.MATRIX_HEIGHT for i in range(self.MATRIX_WIDTH)]

    def reset(self):
        self.index = 0
        self.charIndex = 0
        self.matrix = [[0]*self.MATRIX_HEIGHT for i in range(self.MATRIX_WIDTH)]

    def toList(self):
        r = []
        i, j = 0, 0
        for i in range(self.MATRIX_WIDTH):
            for j in range(self.MATRIX_HEIGHT):
                r.append(self.matrix[j][i])
        return r

    def matrixFromList(self, aList, width, height):
        c = 0
        matrix = [[]]*height
        for i in range(height):
            matrix[i] = [aList[i*width + x] for x in range(width)]
        return matrix

    def getArduinoList(self):
        normal = self.toList()
        arduino = applyTransform([17, 4, 14, 15, 2, 1,
                               0, 5, 13, 10, 3, 8,
                               16, 7, 6, 9, 11, 12,
                               28, 29, 24, 33, 30, 32,
                               18, 23, 27, 25, 21, 34,
                               31, 26, 19, 35, 20, 22],
                               normal)
        return arduino
    
    def next(self):
        if self.index == len(self.str):
            return None

        #shift columns to the left
        i, j = 0, 0
        for i in range(self.MATRIX_WIDTH - 1):
            for j in range(self.MATRIX_HEIGHT):
                self.matrix[i][j] = self.matrix[i + 1][j]

        #get the new right-most column
        currentChar = LEDCharacters.getCharacter(self.str[self.index], self.MATRIX_WIDTH, self.MATRIX_HEIGHT)     
        #extract the new column at the specified index
        if self.charIndex == len(currentChar[0]):
            newColumn = [0]*self.MATRIX_HEIGHT; #spacer
        else:
            newColumn = [currentChar[i][self.charIndex] for i in range(self.MATRIX_HEIGHT)]
        self.charIndex += 1
        for i in range(self.MATRIX_HEIGHT):
            self.matrix[self.MATRIX_WIDTH-1][i] = newColumn[i]

        #if we've passed the width of the character, move to the next letter
        if self.charIndex > len(currentChar[0]):
            self.index += 1
            self.charIndex = 0

        return self.index

    def __repr__(self):
        return str(self.matrix)


def test():
    allowedChars = LEDCharacters.allowedChars()
    test = MatrixScroller(allowedChars, 6, 6)
    for i in range(len(allowedChars)*10):
        test.next()
    print 'all tests OK'
    test = MatrixScroller('A', 6, 6)
    msr = MatrixScrollRepeater(2, test)
    for i in range(20):
        msr.next()
        print msr.getMatrix()

    test = MatrixScroller('....', 6, 6)
    test.next()
    test.next()
    test.next()
    test.next()
    test.next()
    print test #.getArduinoMatrix()
    print test.getArduinoList()
    #print test.getArduinoMatrix()
    #test.next()
    #print test #.getArduinoMatrix()
    #test.next()
    #print test #.getArduinoMatrix()
    #test.next()
    #print test
    #test.next()
    #print test 
