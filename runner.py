from gamecontroller import GameController
from resources import Resources, Firms
from board import Board
import numpy

stats = []
for i in xrange(1000):
  gc = GameController(Board())
  gc.playGame()
  stats.append(gc.statistics)

numberOfOtherActions = [[], [], [], [], [], []]
amountPerPlayers = [[], [], [], [], [], []]
totalAmount = [[], [], [], [], [], []]
numberOfBuilds = [[], [], [], [], [], []]
numShares = [[], [], [], [], [], []]
numShareSpread = [[], [], [], [], [], []]
shareScores = [[], [], [], [], [], []]
shareSpread = [[], [], [], [], [], []]
buildingsComplete = [[], [], [], [], [], []]
amountOnFirms = [[], [], [], [], [], []]
levelPerPlayer = [[], [], [], [], [], []]
for stat in stats:
  for turnStat in stat:
    turnIndex = turnStat['turnIndex']
    numberOfOtherActions[turnIndex].append(turnStat['numberOfOtherActions'])
    amountPerPlayers[turnIndex].append(
        numpy.mean(turnStat['numberOfSharePerPlayer']))
    totalAmount[turnIndex].append(turnStat['totalAmount'])
    numberOfBuilds[turnIndex].append(turnStat['numberOfBuilds'])
    numShares[turnIndex].append(
        numpy.mean(turnStat['numberOfSharePerPlayer']))
    numShareSpread[turnIndex].append(
        numpy.std(turnStat['numberOfSharePerPlayer']))
    shareScores[turnIndex] += turnStat['shareScores'].values()
    shareSpread[turnIndex].append(numpy.std(turnStat['shareScores'].values()))
    buildingsComplete[turnIndex].append(turnStat['buildingsComplete'])
    amountOnFirms[turnIndex] += \
        [b for a, b in turnStat['amountOnResources'].items() if a in Firms]
    levelPerPlayer[turnIndex] += \
        [a for b in turnStat['levelPerPlayer'] for a in b.values()]

histoNumberOfOtherActions = [
  numpy.histogram(amount, bins=15, range=(0,15)) \
      for amount in numberOfOtherActions
]

histoAmountPerPlayers = [
  numpy.histogram(amount, bins=15, range=(0,30)) for amount in amountPerPlayers
]

histoTotalAmount = [
  numpy.histogram(amount, bins=30, range=(0,300)) for amount in totalAmount
]

histoNumberOfBuilds = [
  numpy.histogram(num, bins=20, range=(0,20)) for num in numberOfBuilds
]

histoNumOfShares = [
  numpy.histogram(values, bins=30, range=(0,30)) for values in numShares
]

histoNumShareSpread = [
  numpy.histogram(values, bins=20, range=(0,20)) for values in numShareSpread
]

histoShareScores = [
  numpy.histogram(values, bins=40, range=(0,40)) for values in shareScores
]

histoShareSpread = [
  numpy.histogram(values, bins=20, range=(0,20)) for values in shareSpread
]

histoBuildingsComplete = [
  numpy.histogram(values, bins=4, range=(0,4)) for values in buildingsComplete
]

histoAmountOnFirms = [
  numpy.histogram(values, bins=10, range=(0,40)) for values in amountOnFirms
]

histoLevelPerPlayer = [
  numpy.histogram(values, bins=10, range=(0,10)) for values in levelPerPlayer
]


print 'histoNumberOfOtherActions'
print histoNumberOfOtherActions
print 'histoAmountPerPlayers'
print histoAmountPerPlayers
print 'histoTotalAmount'
print histoTotalAmount
print 'histoNumberOfBuilds'
print histoNumberOfBuilds
print 'histoNumOfShares'
print histoNumOfShares
print 'histoNumShareSpread'
print histoNumShareSpread
print 'histoShareScores'
print histoShareScores
print 'histoShareSpread'
print histoShareSpread
print 'histoBuildingsComplete'
print histoBuildingsComplete
print 'histoAmountOnFirms'
print histoAmountOnFirms
print 'histoLevelPerPlayer'
print histoLevelPerPlayer


