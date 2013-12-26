import unittest
from random import shuffle, seed
import json
from resources import Resources, Firms, Goods, FirmsOrGoods
import resources
from buildingcolumn import BuildingColumn
from cardcolumn import CardColumn
from cards import *
from player import Player

def upgradesA():
  return [
    UpgradeCard(2, Resources.Red),
    UpgradeCard(2, Resources.Green),
    UpgradeCard(2, Resources.Blue),
    UpgradeCard(0, Resources.Red),
    UpgradeCard(0, Resources.Green),
    UpgradeCard(0, Resources.Blue),
    UpgradeCard(0, Resources.Red),
    UpgradeCard(0, Resources.Green),
    UpgradeCard(0, Resources.Blue),
    PlusLevelCard(0, Resources.Red),
    PlusLevelCard(0, Resources.Green),
    PlusLevelCard(0, Resources.Blue)
  ]
def upgradesB():
  return [
    UpgradeCard(5, Resources.Red),
    UpgradeCard(5, Resources.Green),
    UpgradeCard(5, Resources.Blue),
    PlusLevelCard(0, Resources.Red),
    PlusLevelCard(0, Resources.Green),
    PlusLevelCard(0, Resources.Blue),
  ]
def investmentsA():
  return [
    FactoryCard(0, Resources.Red, Resources.Iron),
    FactoryCard(0, Resources.Green, Resources.Brick),
    FactoryCard(0, Resources.Blue, Resources.Glass),
    FactoryCard(0, Resources.Red, Resources.Brick),
    FactoryCard(0, Resources.Green, Resources.Glass),
    FactoryCard(0, Resources.Blue, Resources.Iron),
    DividendCard(0, Resources.Red, 2),
    DividendCard(0, Resources.Green, 2),
    DividendCard(0, Resources.Blue, 2),
    DividendCard(0, Resources.Red, 2),
    DividendCard(0, Resources.Green, 2),
    DividendCard(0, Resources.Blue, 2)
  ]
def investmentsB():
  return [
    ShareCard(0, Resources.Red, 1),
    ShareCard(0, Resources.Green, 1),
    ShareCard(0, Resources.Blue, 1),
    ShareCard(0, Resources.Red, 1),
    ShareCard(0, Resources.Green, 1),
    ShareCard(0, Resources.Blue, 1)
  ]


def defaultBank():
  return [4, 6]

def initialBuildings(firm):
  first = resources.mainGoods(firm)
  second = resources.nextGoods(first)
  third = resources.nextGoods(second)
  result = [
    BuildingCard(2, firm, Resources.Bank),
    BuildingCard(2, firm, Resources.Bank),
    BuildingCard(2, firm, Resources.Bank),
    BuildingCard(3, firm, firm),
    BuildingCard(3, firm, firm),
    BuildingCard(3, firm, firm),
    BuildingCard(4, firm, first),
    BuildingCard(4, firm, first),
    BuildingCard(4, firm, first),
#    BuildingCard(5, firm, second),
    BuildingCard(5, firm, second),
    BuildingCard(5, firm, second),
    BuildingCard(6, firm, third),
    BuildingCard(6, firm, third),
    BuildingCard(6, firm, third),
  ]
  shuffle(result)
  return result

class Board:
  def __init__(self):
    self.roofStack = [
      RoofCard(8),
      RoofCard(8),
      RoofCard(8),
      RoofCard(7),
      RoofCard(7),
      RoofCard(6),
      RoofCard(6),
      RoofCard(5),
      RoofCard(5),
      RoofCard(4),
      RoofCard(4),
      RoofCard(4),
      RoofCard(3),
      RoofCard(3),
      RoofCard(3),
      RoofCard(2),
      RoofCard(2),
      RoofCard(2)
    ]
    self.shareValue = {firm: 0 for firm in Firms}
    self.buildingStack = {}
    for firm in Firms:
      self.buildingStack[firm] = BuildingColumn(firm, initialBuildings(firm))
      self.buildingStack[firm].setRoof(self.roofStack.pop())
    A = investmentsA()
    B = investmentsB()
    shuffle(A)
    shuffle(B)
    self.investmentStack = B + A
    A = upgradesA()
    B = upgradesB()
    shuffle(A)
    shuffle(B)
    self.upgradeStack = B + A
    self.investments = []
    self.upgrades = []
    self.bank = []
    self.revenues = {}
    for resource in Firms:
      self.revenues[resource] = 0
    for resource in Goods:
      self.revenues[resource] = 8

  def prepareTurn(self):
    self.investments = [
      self.investmentStack.pop(),
      self.investmentStack.pop(),
      self.investmentStack.pop()
    ]
    self.upgrades = [
      self.upgradeStack.pop(),
      self.upgradeStack.pop(),
      self.upgradeStack.pop()
    ]
    self.bank = defaultBank()

class BoardTests(unittest.TestCase):
  def testInitialSetup(self):
    # Try a bunch of "random" boards, use an initial seed, however, so that the
    # test is deterministic.
    seed(10)
    for i in xrange(100):
      b = Board()
      self.assertEqual(2, b.buildingStack[Resources.Red].cardColumn.length())
      self.assertEqual(2, b.buildingStack[Resources.Green].cardColumn.length())
      self.assertEqual(2, b.buildingStack[Resources.Blue].cardColumn.length())
      self.assertEqual(2, b.buildingStack[Resources.Red].roof.level)
      self.assertEqual(2, b.buildingStack[Resources.Green].roof.level)
      self.assertEqual(2, b.buildingStack[Resources.Blue].roof.level)
      self.assertEqual(18, len(b.investmentStack))
      self.assertEqual(18, len(b.upgradeStack))
      self.assertEqual(0, b.revenues[Resources.Red])
      self.assertEqual(0, b.revenues[Resources.Green])
      self.assertEqual(0, b.revenues[Resources.Blue])
      self.assertEqual(8, b.revenues[Resources.Iron])
      self.assertEqual(8, b.revenues[Resources.Brick])
      self.assertEqual(8, b.revenues[Resources.Glass])

  def testPrepareTurn(self):
    # Try a bunch of "random" boards, use an initial seed, however, so that the
    # test is deterministic.
    seed(10)
    for i in xrange(100):
      b = Board()
      b.prepareTurn()
      self.assertEqual(3, len(b.investments))
      self.assertEqual(3, len(b.upgrades))
      self.assertIn(b.investments[0], investmentsA())
      self.assertIn(b.investments[1], investmentsA())
      self.assertIn(b.investments[2], investmentsA())
      self.assertIn(b.upgrades[0], upgradesA())
      self.assertIn(b.upgrades[1], upgradesA())
      self.assertIn(b.upgrades[2], upgradesA())
      self.assertEqual([4, 6], b.bank)
      b.prepareTurn()
      b.prepareTurn()
      b.prepareTurn()
      self.assertEqual(3, len(b.investments))
      self.assertEqual(3, len(b.upgrades))
      self.assertIn(b.investments[0], investmentsA())
      self.assertIn(b.investments[1], investmentsA())
      self.assertIn(b.investments[2], investmentsA())
      self.assertIn(b.upgrades[0], upgradesA())
      self.assertIn(b.upgrades[1], upgradesA())
      self.assertIn(b.upgrades[2], upgradesA())
      self.assertEqual([4, 6], b.bank)
      b.prepareTurn()
      self.assertEqual(3, len(b.investments))
      self.assertEqual(3, len(b.upgrades))
      self.assertIn(b.investments[0], investmentsB())
      self.assertIn(b.investments[1], investmentsB())
      self.assertIn(b.investments[2], investmentsB())
      self.assertIn(b.upgrades[0], upgradesB())
      self.assertIn(b.upgrades[1], upgradesB())
      self.assertIn(b.upgrades[2], upgradesB())
      self.assertEqual([4, 6], b.bank)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
