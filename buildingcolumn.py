import unittest
from cardcolumn import CardColumn
from resources import Resources
from mixedcardserror import MixedCardsError
from cards import *

class BuildingColumn:
  def __init__(self, column, stack):
    self.cardColumn = CardColumn(column)
    self.stack = stack
    self.roof = None
    for card in stack:
      self._checkColumn(card)
  def _checkColumn(self, card):
    try:
      if card.column != self.cardColumn.column:
        raise MixedCardsError(self.cardColumn.column, card)
    except AttributeError:
      pass
  def setRoof(self, roofCard):
    if roofCard.type != 'roof':
      raise RuntimeError('Expected a roof card, got: ' + cardToJson(roofCard))
    if roofCard.level < self.cardColumn.length():
      raise RuntimeError('Roof card level (' + str(roofCard.level) +
                         ') smaller than column length, ' +
                         str(self.cardColumn.length()))
    self.roof = roofCard
    while (self.cardColumn.length() < self.roof.level):
      if len(self.stack) == 0:
        self.cardColumn.clear()
        self.roof = None
        return
      self.cardColumn.add(self.stack.pop())
  def clear(self):
    self.roof = None
    self.cardColumn.clear()

class CardColumnTests(unittest.TestCase):
  def testMixedStackFail(self):
    try:
      column = BuildingColumn(Resources.Green, [ShareCard(3, Resources.Blue)])
    except MixedCardsError as error:
      self.assertEqual(Resources.Green, error.column)
      self.assertEqual(Resources.Blue, error.card.column)
    else:
      self.fail()

  def testSetRoof(self):
    column = BuildingColumn(Resources.Red,
        [ BuildingCard(1, Resources.Red, Resources.Iron),
          BuildingCard(3, Resources.Red, Resources.Glass),
          BuildingCard(4, Resources.Red, Resources.Brick),
          BuildingCard(2, Resources.Red, Resources.Red)] )
    column.setRoof(RoofCard(1))
    self.assertEqual(2, column.cardColumn.getLevel())
    column.setRoof(RoofCard(3))
    self.assertEqual(4, column.cardColumn.getLevel())
    column.cardColumn.popLargest()
    self.assertEqual(3, column.cardColumn.getLevel())
    column.cardColumn.popLargest()
    self.assertEqual(2, column.cardColumn.getLevel())
    column.setRoof(RoofCard(3))
    self.assertEqual(0, column.cardColumn.length())

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

def main():
    unittest.main()

if __name__ == '__main__':
    main()
