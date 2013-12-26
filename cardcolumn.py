import unittest
import heapq
from resources import Resources
from mixedcardserror import MixedCardsError
from cards import *

class CardColumn:
  def __init__(self, column, cards = []):
    self.column = column
    self._cards = [(-card.level, card) for card in cards]
    self._plusLevel = 0
    for card in cards:
      self._increasePlusLevel(card)
      self._checkColumn(card)
    heapq.heapify(self._cards)
  def add(self, card):
    self._increasePlusLevel(card)
    self._checkColumn(card)
    heapq.heappush(self._cards, (-card.level, card))
  def popLargest(self):
    card = heapq.heappop(self._cards)[1]
    self._decreasePlusLevel(card)
    return card
  def getLevel(self):
    if not self._cards:
      return 0
    return self._cards[0][1].level + self._plusLevel
  def length(self):
    return len(self._cards)
  def getCard(self, i):
    return self._cards[i][1]
  def getCards(self):
    return [b for a, b in self._cards]
  def clear(self):
    self._cards = []
    self._plusLevel = 0
  def _checkColumn(self, card):
    try:
      if card.column != self.column:
        raise MixedCardsError(self.column, card)
    except AttributeError:
      pass
  def _increasePlusLevel(self, card):
    try:
      self._plusLevel += card.plusLevel
    except AttributeError:
      pass
  def _decreasePlusLevel(self, card):
    try:
      self._plusLevel -= card.plusLevel
    except AttributeError:
      pass


class CardColumnTests(unittest.TestCase):
  def testMixedColumnFail(self):
    try:
      column = CardColumn(Resources.Green, [ShareCard(3, Resources.Blue)])
    except MixedCardsError as error:
      self.assertEqual(Resources.Green, error.column)
      self.assertEqual(Resources.Blue, error.card.column)
    else:
      self.fail()

  def testAddMixedColumnFail(self):
    column = CardColumn(Resources.Green)
    with self.assertRaises(MixedCardsError):
      column.add(ShareCard(3, Resources.Blue))

  def testNoColumnCardDoesntFail(self):
    column = CardColumn(Resources.Green, [RoofCard(3)])

  def testPopLargest(self):
    column = CardColumn(Resources.Green,
        [ RoofCard(3), BuildingCard(1, Resources.Green, Resources.Glass),
          FactoryCard(2, Resources.Green, Resources.Brick) ])
    self.assertEqual(3, column.popLargest().level)
    self.assertEqual(2, column.popLargest().level)
    self.assertEqual(1, column.popLargest().level)

  def testAddCards(self):
    column = CardColumn(Resources.Red,
      [ RoofCard(1), BuildingCard(7, Resources.Red, Resources.Glass),
        FactoryCard(5, Resources.Red, Resources.Brick) ])
    column.add(RoofCard(3))
    column.add(DividendCard(4, Resources.Red))
    self.assertEqual(7, column.popLargest().level)
    self.assertEqual(5, column.getLevel())
    column.add(BuildingCard(6, Resources.Red, Resources.Glass))
    self.assertEqual(6, column.popLargest().level)
    self.assertEqual(5, column.popLargest().level)
    column.add(RoofCard(2))
    self.assertEqual(4, column.popLargest().level)
    self.assertEqual(3, column.popLargest().level)
    self.assertEqual(2, column.popLargest().level)
    self.assertEqual(1, column.popLargest().level)

  def testPlusLevel(self):
    column = CardColumn(Resources.Red,
      [ PlusLevelCard(3, Resources.Red, 2), RoofCard(4) ])
    self.assertEqual(6, column.getLevel())  # 4 + 2
    column.add(PlusLevelCard(2, Resources.Red, 1))
    self.assertEqual(7, column.getLevel())  # 4 + 2 + 1
    column.popLargest();  # Pops 4 (highest: 3)
    self.assertEqual(6, column.getLevel())  # 3 + 2 + 1
    column.popLargest();  # Pops 3 + 2 (highest: 2)
    self.assertEqual(3, column.getLevel())  # 2 + 1
    column.popLargest();  # Pops 2 + 1
    self.assertEqual(0, column.getLevel())  # Empty


def main():
    unittest.main()

if __name__ == '__main__':
    main()
