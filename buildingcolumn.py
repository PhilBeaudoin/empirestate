import unittest
from random import shuffle
import types
import resources
from cardcolumn import CardColumn
from resources import Resources, Goods, AllResources
from mixedcardserror import MixedCardsError
from cards import *

_shareProgress = [
  0,
  1,
  2,
  3,
  4,
  5,
  6,
  7
]

_reputationIncrement = [
  0,
  0,
  1,
  3,
  5,
  7,
  9,
  11
]

class BuildingColumn:
  def __init__(self, firm, stack):
    self.firm = firm
    self.cardColumn = []
    self.stack = stack
    self.numReset = 0
    for card in stack:
      self._checkColumn(card)

  def _checkColumn(self, card):
    try:
      if card.firm != self.firm:
        raise MixedCardsError(self.firm, card)
    except AttributeError:
      pass

  def shuffleStack(self):
    shuffle(self.stack)

  def refresh(self):
    while self.stackSize() > 0 and (self.buildingSize() < 2  or
                                    not self.buildingTop().stop):
      self.cardColumn.append(self.stack.pop())
      if (self.buildingSize() > 8):
        self.stack += self.cardColumn
        self.cardColumn = []
        self.shuffleStack();
        self.numReset += 1
    if (self.buildingSize() < 2):
      if self.stackSize() != 0:
        raise RuntimeError('Building with less than two cards but stack is ' +
                           'not empty, this should never happen.')
      # Not enough cards, close the building
      self.cardColumn = []

  def buildingValue(self):
    return 0 if self.buildingSize() == 0 else self.cardColumn[-1].value

  def buildingTop(self):
    return None if self.buildingSize() == 0 else self.cardColumn[-1]

  def buildingSize(self):
    return len(self.cardColumn)

  def stackSize(self):
    return len(self.stack)

  def getProgress(self):
    return _shareProgess[self.buildingSize()]

  def getRegress(self):
    return -4

  def popTop(self):
    return self.cardColumn.pop()

  def calculatePayment(self, amount = None, goods = None):
    """|amount| is the amount of money the player has, |goods| is a map from
       goods to the amount of goods of that type the player has. Returns None if
       the amount and goods cannot pay for the building, otherwise return a map
       from resources to the amount that must be paid on each resource. If
       |amount| is None, assumes the player has enough resources."""
    value = self.buildingValue()
    if value == 0 or self.buildingSize() == 0:
      return None
    if amount is None:
      amount = value * self.buildingSize()
      available = {good: 0 for good in Goods}
    else :
      available = goods.copy()
    payments = {resource: 0 for resource in AllResources}
    for card in self.cardColumn:
      neededFromAmount = value
      if resources.isGoods(card.resource):
        used = min(value, available[card.resource])
        available[card.resource] -= used
        neededFromAmount -= used
      if amount < neededFromAmount:
        return None
      amount -= neededFromAmount
      payments[card.resource] += value
    return payments

  def printState(self):
    print "  Count: " + str(self.length()) + "  Level: " + str(self.getLevel())

class BuidingColumnTests(unittest.TestCase):
  def testMixedStackFail(self):
    try:
      column = BuildingColumn(Resources.Green,
          [BuildingCard(1, Resources.Blue, Resources.Iron, False)])
    except MixedCardsError as error:
      self.assertEqual(Resources.Green, error.firm)
      self.assertEqual(Resources.Blue, error.card.firm)
    else:
      self.fail()

  def testRefresh(self):
    column = BuildingColumn(Resources.Red,
        [ BuildingCard(3, Resources.Red, Resources.Iron, False),
          BuildingCard(5, Resources.Red, Resources.Iron, False),
          BuildingCard(4, Resources.Red, Resources.Brick, True),  # 4th
          BuildingCard(3, Resources.Red, Resources.Iron, True),   # 3rd
          BuildingCard(2, Resources.Red, Resources.Iron, False),
          BuildingCard(2, Resources.Red, Resources.Iron, False),
          BuildingCard(5, Resources.Red, Resources.Iron, False),
          BuildingCard(2, Resources.Red, Resources.Iron, False),
          BuildingCard(3, Resources.Red, Resources.Iron, False),
          BuildingCard(5, Resources.Red, Resources.Iron, True),   # 2nd
          BuildingCard(1, Resources.Red, Resources.Glass, False),
          BuildingCard(4, Resources.Red, Resources.Brick, True),  # 1st
          BuildingCard(2, Resources.Red, Resources.Red, True)] )
    def fakeShuffle(column):
      self.assertEqual(9, column.stackSize())
      column.stack = [
        BuildingCard(2, Resources.Red, Resources.Iron, False),    # 6th
        BuildingCard(5, Resources.Red, Resources.Iron, False),    # 7th
        BuildingCard(6, Resources.Red, Resources.Iron, True),     # 5th
        BuildingCard(3, Resources.Red, Resources.Iron, False)
      ]
    column.shuffleStack = types.MethodType(fakeShuffle, column)
    self.assertEqual(0, column.buildingSize())
    column.refresh()
    self.assertEqual(4, column.buildingValue())
    self.assertEqual(2, column.buildingSize())
    column.refresh()
    self.assertEqual(4, column.buildingValue())
    self.assertEqual(2, column.buildingSize())
    column.popTop()
    column.refresh()
    self.assertEqual(5, column.buildingValue())
    self.assertEqual(3, column.buildingSize())
    column.popTop()
    column.refresh()
    self.assertEqual(3, column.buildingValue())
    self.assertEqual(8, column.buildingSize())
    column.popTop()
    column.refresh()
    self.assertEqual(4, column.buildingValue())
    self.assertEqual(8, column.buildingSize())
    column.popTop()
    column.refresh()
    self.assertEqual(6, column.buildingValue())
    self.assertEqual(2, column.buildingSize())
    column.popTop()
    column.refresh()
    self.assertEqual(2, column.buildingValue())
    self.assertEqual(3, column.buildingSize())
    column.popTop()
    column.refresh()
    self.assertEqual(5, column.buildingValue())
    self.assertEqual(2, column.buildingSize())
    column.popTop()
    column.refresh()
    self.assertEqual(0, column.buildingValue())
    self.assertEqual(0, column.buildingSize())

  def testCalculatePayment(self):
    column = BuildingColumn(Resources.Red,
        [ BuildingCard(6, Resources.Red, Resources.Iron, True),
          BuildingCard(3, Resources.Red, Resources.Glass, False),
          BuildingCard(4, Resources.Red, Resources.Brick, False),
          BuildingCard(3, Resources.Red, Resources.Red, False),
          BuildingCard(4, Resources.Red, Resources.Bank, False),
          BuildingCard(7, Resources.Red, Resources.Red, False),
          BuildingCard(4, Resources.Red, Resources.Glass, False) ])
    column.refresh()
    expected = {resource: 0 for resource in AllResources}
    expected[Resources.Bank] = 6
    expected[Resources.Iron] = 6
    expected[Resources.Glass] = 12
    expected[Resources.Brick] = 6
    expected[Resources.Red] = 12
    self.assertEqual(expected, column.calculatePayment())
    goods = { good: 0 for good in Goods }
    self.assertIsNone(column.calculatePayment(0, goods))
    self.assertIsNone(column.calculatePayment(41, goods))
    self.assertEqual(expected, column.calculatePayment(42, goods))
    goods[Resources.Iron] = 3
    goods[Resources.Glass] = 11
    goods[Resources.Brick] = 9
    self.assertIsNone(column.calculatePayment(21, goods))
    self.assertEqual(expected, column.calculatePayment(22, goods))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
