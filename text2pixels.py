#!/usr/bin/env python
"""Return a string of text as pixels where each pixel is a character.

You can pass unicode characters by passing \u0123, for example.
"""

import string
import optparse
import sys
import wx


def Init():
  """Start the app to make wxPython happy.

  You'll need to hold on to this for a long as you need to get pixels.
  Otherwise you'll get an error.
  """
  return wx.PySimpleApp()

def Trim(lines, white):
  # Strip trailing blank lines
  left = right = 99
  top = bottom = 0
  inTop = True
  for line in lines:
    width = len(line)
    if inTop:
      if line.strip(white):
        inTop = False
      else:
        top += 1
    if line.strip(white):
      bottom = 0
    else:
      bottom += 1
    cur_left = width - len(line.lstrip(white))
    if cur_left < left:
      left = cur_left
    cur_right = width - len(line.rstrip(white))
    if cur_right < right:
      right = cur_right
  ret = []
  for line in lines[top:len(lines)-bottom]:
    ret.append(line[left:len(line)-right])
  return ret


def FitSize(width, height, lines, white):
  """Make it fit a certain size.

  Args:
    width: Size, if <= 0 then it's not set to the width
    height: height, we always trim to this height
    lines: lines to fix [[], []]
    white: What is the white character, ex. ' '
  """
  if len(lines) > height:
    lines = lines[:height]
  elif len(lines) < height:
    diff = height - len(lines)
    top = diff // 2
    bottom = diff - top
    for unused_i in range(top):
      lines.insert(0, white * width)
    for unused_i in range(bottom):
      lines.append(white * width)

  if width <= 0:
    return lines
  ret = []
  for line in lines:
    curw = len(line)
    if curw > width:
      line = line[:width]
    elif curw < width:
      diff = width - len(line)
      left = diff // 2
      right = diff - left
      for unused_i in range(left):
        line.insert(0, white)
      for unused_i in range(right):
        line += white
    ret.append(line)

  return ret


def GetFontPixels(font, text, black, white):
  """Draw the text and get the pixels."""

  dc = wx.MemoryDC()
  bitmap = wx.EmptyBitmap(400, 80, -1)
  dc.SelectObject(bitmap)
  dc.SetFont(font)
  dc.SetBackground(wx.Brush('white', wx.SOLID))
  dc.Clear()  # Uses background color
  dc.DrawText(text, 0, 0)
  w, h, descent, unused_ext_leading = dc.GetFullTextExtent(text)
  ret = []
  for y in range(descent - 1, h):
    line = []
    for x in range(w):
      col = dc.GetPixel(x, y)
      if col.Red() > 128:
        line.append(white)
      else:
        line.append(black)
    ret.append(''.join(line))

  # Clear the memory
  dc.SelectObject(wx.NullBitmap)

  return Trim(ret, white)


def Get6PixelsHigh(text, color, fit_width=False):
  """Useful for my 8x8 pixel LED matrix from sparkfun."""
  font = wx.Font(6, wx.SWISS, style=wx.NORMAL, weight=wx.BOLD)
  white = ' '
  width = -1
  if fit_width:
    width = 6
  lines = FitSize(width, 6, GetFontPixels(font, text, color, white), white)
  return lines


def Indent(indents):
  """Indent X number of indents."""
  return ' ' * (2 * indents)


def KingWen(font, hexid):
  """Output the a King Wen char.

  The unicode characters are from \u4DC0 - \u4DFF
  """

  ret = []
  ch = 0x4DC0 + hexid - 1
  exec 'char = u\'\u%4x\'' % ch
  lines = GetFontPixels(font, char, 'R', ' ')
  ret.append(' ' * 8)
  for line in lines[1::2]:
    hex_chars = ''.join(line[1:-1])
    ret.append(hex_chars[1:-1])
  ret.append(' ' * 8)
  return ret


def DoKingWen():
  """Do the King Wen sequence."""
  names = [
      'Creative Power', 'Natural Response', 'Difficult Beginnings',
      'Inexperience', 'Calculated Waiting', 'Conflict', 'Collective Force',
      'Unity', 'Restrained', 'Conduct', 'Prospering', 'Stagnation',
      'Community', 'Sovereignty', 'Moderation', 'Harmonize', 'Adapting',
      'Repair', 'Promotion', 'Contemplating', 'Reform', 'Grace',
      'Deterioration', 'Returning', 'Innocence', 'Potential Energy',
      'Nourishing', 'Critical Mass', 'Danger', 'Synergy', 'Attraction',
      'Continuing', 'Retreat', 'Great Power', 'Progress', 'Censorship',
      'Family', 'Contradiction', 'Obstacles', 'Liberation', 'Decline',
      'Benefit', 'Resolution', 'Temptation', 'Assembling', 'Advancement',
      'Adversity', 'The Source', 'Revolution', 'Cosmic Order', 'Shocking',
      'Meditation', 'Developing', 'Subordinate', 'Zenith', 'Traveling',
      'Penetrating Influence', 'Encouraging', 'Reuniting', 'Limitations',
      'Insight', 'Conscientiousness', 'After the End', 'Before the End'
  ]

  font = wx.FontFromPixelSize((17, 17), wx.SWISS,
                              style=wx.NORMAL, weight=wx.NORMAL)
  for ch in range(1, 65):
    print '%s\'hex%d\': (\'King Wen sequence %d (%s)\', [' % (Indent(2),
                                                              ch,
                                                              ch,
                                                              names[ch - 1])
    lines = KingWen(font, ch)
    assert 8 == len(lines)
    for line in lines:
      assert 8 == len(line)
      print '%s\'%s\',' % (Indent(4), line)
    print '%s]),' % Indent(2)

def printNormally(lines):
  zero = True
  print '',
  for i, line in enumerate(lines):
    print '[',
    #if options.grid:
    #  sys.stdout.write('%02d: ' % (i + 1))
    #if options.python:
    #  sys.stdout.write('%s\'' % (Indent(4)))
    inzero = True
    for bit in line:
      if not zero and not inzero: print ',',
      if zero: zero = False
      if inzero: inzero = False
      if bit == ' ':
        print '0',
      else:
        print '1',
    print ']',
    #sys.stdout.write(''.join(line))
    #if options.python:
    #  sys.stdout.write('\',')
    # Print a blank between lines, but not on last line
    if i + 1 != len(lines):
      sys.stdout.write(',\n')

def printBinary(lines, original, blank=' '):
  # Rotate
  rotated = []
  for i, ch in enumerate(lines[0]):
    rotated.append([])
  for line in lines:
    for i, ch in enumerate(line):
      rotated[i].append(ch)

  #print '  // Prints out the message "%s"' % original
  #print '  // %d bits per line, %d lines long' % (len(rotated[0]), len(rotated))
  #print '  const byte image[] PROGMEM = {'
  print '(' + original + ', ['
  for bits in rotated:
    line = ['    ']
    zero = True
    for bit in bits:
      if not zero: print ',',
      if zero: zero = False
      if bit == blank:
        line.append('0')
      else:
        line.append('1')
    print ''.join(line)
  print '  ] #prints: ' + original



if __name__ == '__main__':
    app = wx.PySimpleApp()
    fsize = 3
    size = (fsize + 5, fsize + 5)
    weight = wx.LIGHT #was .NORMAL
    style = wx.NORMAL
    afont = wx.FontFromPixelSize(size, wx.SWISS, style=style, weight=weight,
                                 face='04b24')
    #afont = wx.FontFromPixelSize(size, wx.SWISS, style=style, weight=weight)

    allowed = string.ascii_letters #best: string.printable

    print allowed
    #print 'String printablesIndex[] = "' + str(allowed) + '";'
    #print

    width = 6
    white = ' '
    color = 'R'

    first = True
    print 'LED_CHARACTERS = ['
    for a in allowed:
      #Get6PixelsHigh(a, 'R', False)
      d = GetFontPixels(afont, a, '#', ' ')
      if not first:
          print ','
      first = False
      print #printBinary(d, a)
      print '("' + str(a) + '", ['
      printNormally(d)
      print '  ])',
    print ']'

##  parse = optparse.OptionParser(
##      ('%prog [options] Text\n'
##       ' Text can have \\u1234 style unicode escapes as well.'))
##  parse.add_option('-s', '--size', dest='fsize', type='int',
##                   help='Font size to use in pixels', default=8)
##  parse.add_option('-b', '--bold', dest='bold', action='store_true',
##                   help='Use bold version')
##  parse.add_option('-i', '--italics', dest='italics', action='store_true',
##                   help='Use italics version')
##  parse.add_option('-f', '--font', dest='font', default='',
##                   help='Font to use')
##  parse.add_option('-g', '--grid', dest='grid', action='store_true',
##                   default=False, help='Show the column, row numbers')
##  parse.add_option('-c', '--char', dest='char', default='#',
##                   help='Character to use')
##  parse.add_option('-p', '--python', dest='python', action='store_true',
##                   default=False,
##                   help='Output as lines of python')
##  parse.add_option('-m', '--matrix', dest='matrix', action='store_true',
##                   help='Emulate the 8x8 matrix')
##  parse.add_option('--binary', dest='binary', action='store_true',
##                   help='Output as list of binary numbers, one per line.')
##  parse.add_option('--kingwen', dest='kingwen', action='store_true',
##                   default=False, help='Output King Wen sequence')
##  options, args = parse.parse_args()
##  app = wx.PySimpleApp()
##  size = (options.fsize + 5, options.fsize + 5)
##  weight = wx.NORMAL
##  if options.bold:
##    weight = wx.BOLD
##  style = wx.NORMAL
##  if options.italics:
##    style = wx.ITALIC
##  if options.font:
##    afont = wx.FontFromPixelSize(size, wx.SWISS, style=style, weight=weight,
##                                 face=options.font)
##  else:
##    afont = wx.FontFromPixelSize(size, wx.SWISS, style=style, weight=weight)
##
##  if options.kingwen:
##    DoKingWen()
##    sys.exit(0)
##
##  for arg in args:
##    exec 'arg = u\'%s\'' % arg
##    if options.matrix:
##      lines = Get8PixelsHigh(arg, 'R')
##    else:
##      lines = GetFontPixels(afont, arg, options.char, ' ')
##    if options.grid:
##      line = '    '
##      for col in range(len(lines[0])):
##        line += '%d' % ((col + 1) % 10)
##      print line
##
##    if options.binary:
##      printBinary(lines, arg)
##    else:
##      printNormally(lines)
