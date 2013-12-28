from gamecontroller import GameController
from resources import Resources, Firms
from board import Board
import numpy

stats = []
for i in xrange(10):
  gc = GameController(Board())
  gc.playGame()
  stats.append(gc.statistics)

statsData = [
  { 'name': 'amountPerPlayer', 'bins': 10, 'range': (0, 100) },
  { 'name': 'levelPerPlayer', 'bins': 10, 'range': (0, 100) },
  { 'name': 'shareScore', 'bins': 10, 'range': (0, 50) },
  { 'name': 'shareValue', 'bins': 20, 'range': (0, 20) },
]

statsResult = {
  data['name']: [[] for i in range(7)] for data in statsData
}

amountPerPlayer = [[], [], [], [], [], [], []]
levelPerPlayer = [[], [], [], [], [], [], []]
for stat in stats:
  for turnStat in stat:
    turnIndex = turnStat['turnIndex']
    for data in statsData:
      statsResult[data['name']][turnIndex].append(
          turnStat[data['name']].values())

def printHisto(name, bins, range):
  print name
  histos = [ numpy.histogram(turn, bins=bins, range=range)
             for turn in statsResult[name] ]
  print "  " + str(list(histos[0][1]))
  for histo in histos:
    print "  " + str(list(histo[0]))

for data in statsData:
  printHisto(data['name'], data['bins'], data['range'])
