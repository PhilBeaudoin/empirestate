import unittest
import resources
from resources import Resources
from cardcolumn import CardColumn
from buildingcolumn import BuildingColumn
from cards import *

class Player:
  def __init__(self, initialIndex = 0, numActions = 3, amount = 0):
    self.initialIndex = initialIndex
    self.columns = {
      Resources.Red: CardColumn(Resources.Red),
      Resources.Green: CardColumn(Resources.Green),
      Resources.Blue: CardColumn(Resources.Blue),
    }
    self.numActions = numActions
    self.amount = amount

  def addCard(self, card):
    self.columns[card.column].add(card)

  def getPayoff(self):
    for column in self.columns.values():
      for i in xrange(column.length()):
        card = column.getCard(i)
        self.amount += card.payoff(column.getLevel())

  def canPayForBuilding(self, buildingColumn):
    if buildingColumn.cardColumn.length() == 0:
      return False
    return self._payOrCheckBuilding(buildingColumn, False)

  def payForBuilding(self, buildingColumn):
    self._payOrCheckBuilding(buildingColumn, True)

  def _payOrCheckBuilding(self, buildingColumn, pay):
    level = buildingColumn.cardColumn.getLevel()
    needed = {
      Resources.Iron: 0,
      Resources.Brick: 0,
      Resources.Glass: 0
    }
    amount = self.amount
    for i in xrange(buildingColumn.cardColumn.length()):
      resource = buildingColumn.cardColumn.getCard(i).resource
      if resources.isGoods(resource):
        needed[resource] += level
      else:
        amount -= level
    for column in self.columns.values():
      for i in xrange(column.length()):
        card = column.getCard(i)
        if card.type == 'factory':
          cardAmount = max(0, card.amount - needed[card.resource])
          needed[card.resource] = max(0, needed[card.resource] - card.amount)
          if pay:
            card.amount = cardAmount
    for need in needed.values():
      amount -= need
    if pay:
      if amount < 0:
        raise RuntimeError('Not enough money or resources to pay for building.')
      self.amount = amount
    return amount >= 0

class PlayerTests(unittest.TestCase):
  def testCanPayForBuilding(self):
    building = BuildingColumn(Resources.Red, [
      BuildingCard(2, Resources.Red, Resources.Bank),
      BuildingCard(3, Resources.Red, Resources.Red),
      BuildingCard(4, Resources.Red, Resources.Iron),
      BuildingCard(4, Resources.Red, Resources.Iron)
    ])
    player = Player(3, 3, 12)
    player.columns[Resources.Red].add(
        FactoryCard(2, Resources.Red, Resources.Iron, 3))
    building.setRoof(RoofCard(4))
    self.assertFalse(player.canPayForBuilding(building))
    player.columns[Resources.Red].add(
        FactoryCard(2, Resources.Red, Resources.Iron, 1))
    self.assertTrue(player.canPayForBuilding(building))
    player.columns[Resources.Red].add(
        FactoryCard(2, Resources.Red, Resources.Iron, 40))
    player.amount = 8
    self.assertTrue(player.canPayForBuilding(building))
    player.amount = 7
    self.assertFalse(player.canPayForBuilding(building))
    player.amount = 1000
    self.assertFalse(
        player.canPayForBuilding(BuildingColumn(Resources.Red, [])))

  def testPayForBuilding(self):
    building = BuildingColumn(Resources.Red, [
      BuildingCard(2, Resources.Red, Resources.Bank),
      BuildingCard(3, Resources.Red, Resources.Red),
      BuildingCard(4, Resources.Red, Resources.Iron),
      BuildingCard(4, Resources.Red, Resources.Iron)
    ])
    player = Player(3, 3, 16)
    player.columns[Resources.Red].add(
        FactoryCard(2, Resources.Red, Resources.Iron, 3))
    building.setRoof(RoofCard(4))
    player.payForBuilding(building)
    self.assertEqual(3, player.amount)
    card = player.columns[Resources.Red].popLargest()
    self.assertEqual(0, card.amount)
    player.amount = 8
    player.columns[Resources.Red].add(
        FactoryCard(3, Resources.Red, Resources.Iron, 20))
    player.payForBuilding(building)
    self.assertEqual(0, player.amount)
    card = player.columns[Resources.Red].popLargest()
    self.assertEqual(12, card.amount)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
