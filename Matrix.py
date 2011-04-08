#!/usr/bin/env python

# Arduino LED matrix control for the Simmons LED Gym Display
# By Isaac Evans
# ine@mit.edu
# 3/25/2011

import LEDCharacters

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
        return self.SM.getMatrix()

    def getWidth(self):
        return self.SM.getWidth()

    def getHeight(self):
        return self.SM.getHeight()
    
    def getText(self):
        return self.SM.getText()

    def __repr__(self):
        return str(self.SM)

class MatrixSM:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        
        self.str = 'Do-nothing MatrixSM'
        
        self.resetMatrix()
    
    def reset(self):
        self.resetMatrix()
    
    def resetMatrix(self):
        self.matrix = [[0]*self.HEIGHT for i in range(self.WIDTH)]
    
    def next(self):
        return 1

    def applyTransform(self, perm, position):
        new = [0]*len(position)
        for i, element in enumerate(position):
            new[perm[i]] = element
        return new
    
    def toList(self):
        r = []
        i, j = 0, 0
        for i in range(self.WIDTH):
            for j in range(self.HEIGHT):
                r.append(self.matrix[j][i])
        return r

    def matrixFromList(self, aList, width, height):
        matrix = [[]]*height
        for i in range(height):
            matrix[i] = [aList[i*width + x] for x in range(width)]
        return matrix

    def getArduinoList(self):
        transformMatrix = [17, 4, 14, 15, 2, 1,
                           0, 5, 13, 10, 3, 8,
                           16, 7, 6, 9, 11, 12,
                           28, 29, 24, 33, 30, 32,
                           18, 23, 27, 25, 21, 34,
                           31, 26, 19, 35, 20, 22]
        normal = self.toList()
                           
        arduino = self.applyTransform(transformMatrix, normal)
        
        return arduino
            
    def getMatrix(self):
        return self.matrix

    def getWidth(self):
        return self.WIDTH

    def getHeight(self):
        return self.HEIGHT
    
    def getText(self):
        return self.str
    
    def __str__(self):
        strArray = []
        for row in self.matrix:
            strArray.append(str(row))
        return '\n'.join(strArray)

class MatrixScroller(MatrixSM):
    def __init__(self, message, width, height):
        MatrixSM.__init__(self, width, height)
        
        self.str = message
        self.index = 0
        self.charIndex = 0

    def reset(self):
        self.index = 0
        self.charIndex = 0
        
        self.resetMatrix()
    
    def next(self):
        if self.index == len(self.str):
            return None

        #shift columns to the left
        i, j = 0, 0
        for i in range(self.WIDTH - 1):
            for j in range(self.HEIGHT):
                self.matrix[i][j] = self.matrix[i + 1][j]

        #get the new right-most column
        currentChar = LEDCharacters.getCharacter(self.str[self.index], self.WIDTH, self.HEIGHT)     
        #extract the new column at the specified index
        if self.charIndex == len(currentChar[0]):
            newColumn = [0]*self.HEIGHT; #spacer
        else:
            newColumn = [currentChar[i][self.charIndex] for i in range(self.HEIGHT)]
        self.charIndex += 1
        for i in range(self.HEIGHT):
            self.matrix[self.WIDTH-1][i] = newColumn[i]

        #if we've passed the width of the character, move to the next letter
        if self.charIndex > len(currentChar[0]):
            self.index += 1
            self.charIndex = 0

        return self.index


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
