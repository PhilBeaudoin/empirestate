from random import shuffle
import numpy
from resources import Resources, AllResources, FirmsOrGoods
import resources
from cards import *
from buildingcolumn2 import BuildingColumn2

firm = Resources.Red
first = resources.mainGoods(firm)
second = resources.nextGoods(first)
third = resources.nextGoods(second)
column = [
      BuildingCard(2, firm, Resources.Bank, False),
      BuildingCard(2, firm, Resources.Bank, False),
      BuildingCard(2, firm, Resources.Bank, True),
      BuildingCard(3, firm, firm, False),
      BuildingCard(3, firm, firm, False),
      BuildingCard(3, firm, firm, True),
      BuildingCard(4, firm, first, False),
      BuildingCard(4, firm, first, False),
      BuildingCard(4, firm, first, True),
      BuildingCard(5, firm, second, False),
      BuildingCard(5, firm, second, True),
      BuildingCard(5, firm, second, True),
      BuildingCard(6, firm, third, False),
      BuildingCard(6, firm, third, True),
      BuildingCard(6, firm, third, True),
      BuildingCard(6, firm, third, True),
    ]

nbTurns = 15

valuePerTurn = [[] for i in range(nbTurns)]
sizePerTurn = [[] for i in range(nbTurns)]
amountPerTurn = [[] for i in range(nbTurns)]
resetPerTurn = [[] for i in range(nbTurns)]
amountPerResourcePerTurn = { r: [[] for i in range(nbTurns)]
                             for r in AllResources}

for i in xrange(1000):
  building = BuildingColumn2(firm, list(column))
  building.shuffleStack()
  for turn in xrange(nbTurns):
    building.refresh()
    valuePerTurn[turn].append(building.buildingValue())
    sizePerTurn[turn].append(building.buildingSize())
    amountPerTurn[turn].append(building.buildingSize() *
                               building.buildingValue())
    resetPerTurn[turn].append(building.numReset)
    payment = building.calculatePayment()
    for r in AllResources:
      amountPerResourcePerTurn[r][turn].append(payment[r])
    building.popTop()

def printHisto(name, bins, range, stats, printHeader):
  histo = numpy.histogram(stats, bins=bins, range=range)
  if printHeader:
    print " " * 10 + str([int(h) for h in histo[1]])
  print "  " + name.ljust(8) + str(list(histo[0])) + \
      "  (" + str(numpy.mean(stats)) + ")"

for turn in xrange(nbTurns):
  print "Turn = " + str(turn)
  printHisto("Value", 5, (2, 7), valuePerTurn[turn], True)
  printHisto("Size", 9, (0, 9), sizePerTurn[turn], True)
  printHisto("Amount", 20, (0, 40), amountPerTurn[turn], True)
  printHisto("Reset", 10, (0, 10), resetPerTurn[turn], True)
  printHisto("Bank", 15, (0, 30),
             amountPerResourcePerTurn[Resources.Bank][turn], True)
  for r in FirmsOrGoods:
    printHisto(Resources.reverse_mapping[r], 15, (0, 30),
               amountPerResourcePerTurn[r][turn], False)
