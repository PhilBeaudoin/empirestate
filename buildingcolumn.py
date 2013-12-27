import unittest
import resources
from cardcolumn import CardColumn
from resources import Resources, Goods, AllResources
from mixedcardserror import MixedCardsError
from cards import *

class BuildingColumn:
  def __init__(self, firm, stack):
    self.cardColumn = CardColumn(firm)
    self.stack = stack
    self.roof = None
    for card in stack:
      self._checkColumn(card)
  def _checkColumn(self, card):
    try:
      if card.firm != self.cardColumn.firm:
        raise MixedCardsError(self.cardColumn.firm, card)
    except AttributeError:
      pass
  def setRoof(self, roofCard):
    if roofCard.type != CardTypes.Roof:
      raise RuntimeError('Expected a roof card, got: ' + cardToJson(roofCard))
    self.roof = roofCard
    if roofCard.name == 'finalRoof':
      self.cardColumn.clear()
      return
    if roofCard.cardCount < self.cardColumn.length():
      raise RuntimeError('Roof card card count (' + str(roofCard.cardCount) +
                         ') smaller than column length, ' +
                         str(self.cardColumn.length()))
    while (self.cardColumn.length() < self.roof.cardCount):
      if len(self.stack) == 0:
        self.cardColumn.clear()
        return
      self.cardColumn.add(self.stack.pop())

  def getLevel(self):
    return self.cardColumn.getLevel()

  def length(self):
    return self.cardColumn.length()

  def getProgress(self):
    return 0 if not self.roof else self.roof.progress

  def calculatePayment(self, amount = None, goods = None):
    """|amount| is the amount of money the player has, |goods| is a map from
       goods to the amount of goods of that type the player has. Returns None if
       the amount and goods cannot pay for the building, otherwise return a map
       from resources to the amount that must be paid on each resource."""
    level = self.getLevel()
    if level == 0 or self.length() == 0:
      return None
    if amount is None:
      amount = level * self.length()
      available = {good: 0 for good in Goods}
    else :
      available = goods.copy()
    payments = {resource: 0 for resource in AllResources}
    for card in self.cardColumn.getCards():
      neededFromAmount = level
      if resources.isGoods(card.resource):
        used = min(level, available[card.resource])
        available[card.resource] -= used
        neededFromAmount -= used
      if amount < neededFromAmount:
        return None
      amount -= neededFromAmount
      payments[card.resource] += level
    return payments

class BuidingColumnTests(unittest.TestCase):
  def testMixedStackFail(self):
    try:
      column = BuildingColumn(Resources.Green,
                              [BuildingCard(1, Resources.Blue, Resources.Iron)])
    except MixedCardsError as error:
      self.assertEqual(Resources.Green, error.firm)
      self.assertEqual(Resources.Blue, error.card.firm)
    else:
      self.fail()

  def testSetRoof(self):
    column = BuildingColumn(Resources.Red,
        [ BuildingCard(1, Resources.Red, Resources.Iron),
          BuildingCard(3, Resources.Red, Resources.Glass),
          BuildingCard(4, Resources.Red, Resources.Brick),
          BuildingCard(2, Resources.Red, Resources.Red)] )
    self.assertEqual(0, column.getProgress())
    column.setRoof(RoofCard(1, 3))
    self.assertEqual(2, column.getLevel())
    self.assertEqual(3, column.getProgress())
    column.setRoof(RoofCard(3))
    self.assertEqual(4, column.getLevel())
    column.cardColumn.popLargest()
    self.assertEqual(3, column.getLevel())
    column.cardColumn.popLargest()
    self.assertEqual(2, column.getLevel())
    column.setRoof(RoofCard(3))
    self.assertEqual(0, column.length())

  def testSetRoofFail(self):
    column = BuildingColumn(Resources.Red,
        [ BuildingCard(1, Resources.Red, Resources.Iron),
          BuildingCard(3, Resources.Red, Resources.Glass),
          BuildingCard(4, Resources.Red, Resources.Brick),
          BuildingCard(2, Resources.Red, Resources.Red)] )
    column.setRoof(RoofCard(3))
    self.assertEqual(4, column.cardColumn.getLevel())
    with self.assertRaises(RuntimeError):
      column.setRoof(BuildingCard(2, Resources.Red, Resources.Red))
    with self.assertRaises(RuntimeError):
      column.setRoof(RoofCard(2))

  def testSetFinalRoof(self):
    column = BuildingColumn(Resources.Red,
        [ BuildingCard(1, Resources.Red, Resources.Iron),
          BuildingCard(3, Resources.Red, Resources.Glass),
          BuildingCard(4, Resources.Red, Resources.Brick),
          BuildingCard(2, Resources.Red, Resources.Red)] )
    column.setRoof(FinalRoofCard(10))
    self.assertEqual(0, column.getLevel())
    self.assertEqual(0, column.length())
    self.assertEqual(10, column.getProgress())

  def testSetRoofNotEnoughCards(self):
    column = BuildingColumn(Resources.Red,
        [ BuildingCard(1, Resources.Red, Resources.Iron),
          BuildingCard(3, Resources.Red, Resources.Glass),
          BuildingCard(1, Resources.Red, Resources.Brick),
          BuildingCard(2, Resources.Red, Resources.Red)] )
    column.setRoof(RoofCard(4,6))
    self.assertEqual(3, column.getLevel())
    self.assertEqual(4, column.length())
    self.assertEqual(6, column.getProgress())
    column.setRoof(RoofCard(5, 7))
    self.assertEqual(0, column.getLevel())
    self.assertEqual(0, column.length())
    self.assertEqual(7, column.getProgress())

  def testCalculatePayment(self):
    column = BuildingColumn(Resources.Red,
        [ BuildingCard(1, Resources.Red, Resources.Iron),
          BuildingCard(3, Resources.Red, Resources.Glass),
          BuildingCard(4, Resources.Red, Resources.Brick),
          BuildingCard(3, Resources.Red, Resources.Red),
          BuildingCard(4, Resources.Red, Resources.Bank),
          BuildingCard(7, Resources.Red, Resources.Red),
          BuildingCard(4, Resources.Red, Resources.Glass) ])
    column.setRoof(RoofCard(7))
    expected = {resource: 0 for resource in AllResources}
    expected[Resources.Bank] = 7
    expected[Resources.Iron] = 7
    expected[Resources.Glass] = 14
    expected[Resources.Brick] = 7
    expected[Resources.Red] = 14
    self.assertEqual(expected, column.calculatePayment())
    goods = { good: 0 for good in Goods }
    self.assertIsNone(column.calculatePayment(0, goods))
    self.assertIsNone(column.calculatePayment(48, goods))
    self.assertEqual(expected, column.calculatePayment(49, goods))
    goods[Resources.Iron] = 3
    goods[Resources.Glass] = 13
    goods[Resources.Brick] = 9
    self.assertIsNone(column.calculatePayment(25, goods))
    self.assertEqual(expected, column.calculatePayment(26, goods))
    column.setRoof(RoofCard(8))
    self.assertIsNone(column.calculatePayment(500, goods))
    column = BuildingColumn(Resources.Red,
        [ BuildingCard(1, Resources.Red, Resources.Iron) ])
    column.setRoof(FinalRoofCard(10))
    self.assertIsNone(column.calculatePayment(500, goods))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
