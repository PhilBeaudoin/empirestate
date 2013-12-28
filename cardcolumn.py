import unittest
import heapq
from resources import Resources
from mixedcardserror import MixedCardsError
from cards import *

class CardColumn:
  def __init__(self, firm, cards = []):
    self.firm = firm
    self._cards = [(-card.level, card) for card in cards]
    for card in cards:
      self._checkColumn(card)
    heapq.heapify(self._cards)
  def add(self, card):
    self._checkColumn(card)
    heapq.heappush(self._cards, (-card.level, card))
  def popLargest(self):
    card = heapq.heappop(self._cards)[1]
    return card
  def getLargest(self):
    if not self._cards:
      return 0
    return self._cards[0][1]
  def getLevel(self):
    if not self._cards:
      return 0
    return self._cards[0][1].level
  def length(self):
    return len(self._cards)
  def getCard(self, i):
    return self._cards[i][1]
  def getCards(self):
    return [b for a, b in self._cards]
  def clear(self):
    self._cards = []
  def _checkColumn(self, card):
    try:
      if card.firm != self.firm:
        raise MixedCardsError(self.firm, card)
    except AttributeError:
      pass

class CardColumnTests(unittest.TestCase):
  def testMixedColumnFail(self):
    try:
      column = CardColumn(Resources.Green,
                          [BuildingCard(3, Resources.Blue, Resources.Glass)])
    except MixedCardsError as error:
      self.assertEqual(Resources.Green, error.firm)
      self.assertEqual(Resources.Blue, error.card.firm)
    else:
      self.fail()

  def testAddMixedColumnFail(self):
    column = CardColumn(Resources.Green)
    with self.assertRaises(MixedCardsError):
      column.add(ShareCard(3, Resources.Blue))

  def testPopLargest(self):
    column = CardColumn(Resources.Red,
        [ BuildingCard(3, Resources.Red, Resources.Glass),
          BuildingCard(1, Resources.Red, Resources.Brick),
          BuildingCard(2, Resources.Red, Resources.Red)])
    self.assertEqual(3, column.popLargest().level)
    self.assertEqual(2, column.popLargest().level)
    self.assertEqual(1, column.popLargest().level)

  def testAddCards(self):
    column = CardColumn(Resources.Red,
      [ BuildingCard(7, Resources.Red, Resources.Glass),
        BuildingCard(4, Resources.Red, Resources.Red)])
    column.add(BuildingCard(3, Resources.Red, Resources.Red))
    column.add(BuildingCard(5, Resources.Red, Resources.Iron))
    self.assertEqual(7, column.popLargest().level)
    self.assertEqual(5, column.getLevel())
    column.add(BuildingCard(6, Resources.Red, Resources.Glass))
    self.assertEqual(6, column.getLevel())
    self.assertEqual(6, column.popLargest().level)
    self.assertEqual(5, column.popLargest().level)
    column.add(BuildingCard(2, Resources.Red, Resources.Brick))
    self.assertEqual(4, column.popLargest().level)
    self.assertEqual(3, column.popLargest().level)
    self.assertEqual(2, column.popLargest().level)
    self.assertEqual(0, column.length())

def main():
    unittest.main()

if __name__ == '__main__':
    main()
