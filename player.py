import unittest
from resources import Resources, Firms, Goods
from cardcolumn import CardColumn
from buildingcolumn import BuildingColumn
from cardtypes import PlayerAreaCardTypes
from cards import *

class Player:
  def __init__(self, ident = 0, numActions = 3, amount = 0):
    self.ident = ident
    self.levelCard = None
    self.cards = []
    self.bonusCards = []
    self.numActions = numActions
    self.amount = amount

  def addCard(self, card):
    if card.type not in PlayerAreaCardTypes:
      raise RuntimeError('Expected a player area card, got: ' + cardToJson(card))
    self.cards.append(card)

  def addBonusCard(self, card):
    if card.type != CardTypes.Bonus:
      raise RuntimeError('Expected a bonus card, got: ' + cardToJson(card))
    self.bonusCards.append(card)

  def removeBonusCard(self, card):
    if card not in self.bonusCards:
      raise RuntimeError('Trying to remove a bonus card the player does not ' +
                         'have, got: ' + cardToJson(card))
    self.bonusCards.remove(card)

  def setLevelCard(self, card):
    if card.type != CardTypes.Level:
      raise RuntimeError('Expected a level card, got: ' + cardToJson(card))
    level = 0 if not self.levelCard else self.levelCard.level
    if (card.level >= level):
      self.levelCard = card

  def getLevel(self):
    level = 0 if not self.levelCard else self.levelCard.level
    for card in self.cards:
      if card.name == 'plusLevel':
        level += card.plusLevel
    return level

  def getPayoff(self):
    level = self.getLevel()
    for card in self.cards:
      self.amount += card.payoff(level, self.bonusCards)

  def payInterests(self, interests):
    """Returns how much money is missing, or 0 if none is missing."""
    for card in self.cards:
      self.amount -= card.upkeep * interests
    if self.amount < 0:
      missing = -self.amount
      self.amount = 0
      return missing
    return 0

  def canPayForBuilding(self, buildingColumn):
    return buildingColumn.calculatePayment(self.amount,
        self.getResources()) is not None

  def payForBuilding(self, buildingColumn):
    payments = buildingColumn.calculatePayment(self.amount,
        self.getResources())
    if payments is None:
      raise RuntimeError('Not enough money or resources to pay for building.')
    needed = payments.copy()
    for card in self.cards:
      if card.name == 'factory' or card.name == 'loanGoods':
        paid = min(needed[card.resource], card.amount)
        needed[card.resource] -= paid
        card.amount -= paid
    self.amount -= sum(needed.values())
    return payments

  def getResources(self):
    available = {good: 0 for good in Goods}
    for card in self.cards:
      if card.name == 'factory' or card.name == 'loanGoods':
        available[card.resource] += card.amount
    return available

  def sellShares(self, shareValues):
    for card in self.cards:
      if card.name == 'share':
        self.amount += card.multiplicity * shareValues[card.firm]
    self.cards = [card for card in self.cards if not card.name == 'share']

  def finalPayoff(self):
    for card in self.cards:
      self.amount = max(0, self.amount + card.finalPayoff)

  def printState(self):
    print "Player " + str(self.ident) + "  Amount: " + str(self.amount) + \
        "  Level card: " + \
        str(0 if not self.levelCard else self.levelCard.level)
    for card in self.cards:
      print "  " + cardToJson(card)

class PlayerTests(unittest.TestCase):
  def testCanPayForBuilding(self):
    building = BuildingColumn(Resources.Red, [
      BuildingCard(2, Resources.Red, Resources.Bank),
      BuildingCard(3, Resources.Red, Resources.Red),
      BuildingCard(4, Resources.Red, Resources.Iron),
      BuildingCard(4, Resources.Red, Resources.Iron)
    ])
    building.setRoof(RoofCard(4, 0, 0))
    player = Player(3, 3, 12)
    player.addCard(FactoryCard(Resources.Iron, 0, 0, 0, 3))
    self.assertFalse(player.canPayForBuilding(building))
    player.addCard(LoanGoodsCard(Resources.Iron, 1, 0, 0))
    self.assertTrue(player.canPayForBuilding(building))
    player.addCard(FactoryCard(Resources.Iron, 0, 0, 0, 40))
    player.amount = 8
    self.assertTrue(player.canPayForBuilding(building))
    player.amount = 7
    self.assertFalse(player.canPayForBuilding(building))
    player.amount = 1000
    self.assertFalse(
        player.canPayForBuilding(BuildingColumn(Resources.Red, [])))
    building.setRoof(FinalRoofCard(10, 5))
    self.assertFalse(player.canPayForBuilding(building))

  def testPayForBuilding(self):
    building = BuildingColumn(Resources.Red, [
      BuildingCard(2, Resources.Red, Resources.Bank),
      BuildingCard(3, Resources.Red, Resources.Red),
      BuildingCard(4, Resources.Red, Resources.Iron),
      BuildingCard(4, Resources.Red, Resources.Iron)
    ])
    building.setRoof(RoofCard(4, 0, 0))
    player = Player(3, 3, 16)
    player.addCard(FactoryCard(Resources.Iron, 0, 0, 0, 3))
    player.payForBuilding(building)
    self.assertEqual(3, player.amount)
    self.assertEqual(0, player.cards[0].amount)
    player.amount = 8
    player.addCard(LoanGoodsCard(Resources.Iron, 20, 0, 0))
    player.payForBuilding(building)
    self.assertEqual(0, player.amount)
    self.assertEqual(0, player.cards[0].amount)
    self.assertEqual(12, player.cards[1].amount)
    with self.assertRaises(RuntimeError):
      player.payForBuilding(building)
    building.setRoof(FinalRoofCard(10, 5))
    player.amount = 1000
    with self.assertRaises(RuntimeError):
      player.payForBuilding(building)

  def testGetLevel(self):
    player = Player(3, 3, 16)
    player.setLevelCard(LevelCard(3))
    self.assertEqual(3, player.getLevel())
    player.setLevelCard(LevelCard(5))
    self.assertEqual(5, player.getLevel())
    player.setLevelCard(LevelCard(2))
    self.assertEqual(5, player.getLevel())
    player.addCard(PlusLevelCard(2, 0, 0))
    self.assertEqual(7, player.getLevel())
    player.addCard(PlusLevelCard(1, 0, 0))
    self.assertEqual(8, player.getLevel())
    with self.assertRaises(RuntimeError):
      player.setLevelCard(BuildingCard(2, Resources.Red, Resources.Red))

  def testAddCards(self):
    player = Player()
    with self.assertRaises(RuntimeError):
      player.addCard(BuildingCard(2, Resources.Red, Resources.Red))
    player.addCard(ActionCard())
    self.assertIn(ActionCard(), player.cards)
    with self.assertRaises(RuntimeError):
      player.addBonusCard(ActionCard())
    player.addBonusCard(BonusEquipmentCard(3))
    self.assertIn(BonusEquipmentCard(3), player.bonusCards)
    with self.assertRaises(RuntimeError):
      player.removeBonusCard(BonusEquipmentCard(2))
    player.removeBonusCard(BonusEquipmentCard(3))
    self.assertNotIn(BonusEquipmentCard(3), player.bonusCards)

  def testGetPayoff(self):
    player = Player()
    player.setLevelCard(LevelCard(3))
    player.addCard(FactoryCard(Resources.Iron, 1, 0, 0))    # +6 iron
    player.addCard(LoanGoodsCard(Resources.Glass, 5, 0, 0)) # No increase.
    player.addCard(PlusLevelCard(1, 0, 0))
    player.addCard(WorkforceCard(1, 0, 0))         # +7
    player.addCard(EquipmentCard(0, 0, 0))         # +7
    player.addCard(MoneyForLevelCard(4, 3, 0, 0))  # +3
    player.addCard(MoneyForLevelCard(5, 6, 0, 0))  # Will not activate.
    player.addBonusCard(BonusFactoryCard(1))
    player.addBonusCard(BonusWorkforceCard(2))
    player.addBonusCard(BonusEquipmentCard(3))
    player.getPayoff()
    self.assertEqual(17, player.amount)
    resources = player.getResources()
    self.assertEqual(6, resources[Resources.Iron])
    self.assertEqual(5, resources[Resources.Glass])

  def testPayInterests(self):
    player = Player(3, 3, 50)
    player.addCard(FactoryCard(Resources.Iron, 1, 1, 0))
    player.addCard(LoanGoodsCard(Resources.Glass, 5, 1, 0))
    player.addCard(PlusLevelCard(1, 0, 0))
    player.addCard(WorkforceCard(1, 2, 0))
    player.addCard(EquipmentCard(0, 2, 0))
    player.addCard(MoneyForLevelCard(4, 3, 3, 0))
    player.addCard(MoneyForLevelCard(5, 6, 1, 0))
    self.assertEqual(0, player.payInterests(0))
    self.assertEqual(50, player.amount)
    self.assertEqual(0, player.payInterests(1))
    self.assertEqual(40, player.amount)
    self.assertEqual(0, player.payInterests(3))
    self.assertEqual(10, player.amount)
    self.assertEqual(0, player.payInterests(1))
    self.assertEqual(0, player.amount)
    self.assertEqual(0, player.payInterests(0))
    self.assertEqual(0, player.amount)
    self.assertEqual(10, player.payInterests(1))
    self.assertEqual(0, player.amount)
    player.amount = 19
    self.assertEqual(1, player.payInterests(2))
    self.assertEqual(0, player.amount)
    player.amount = 15
    self.assertEqual(5, player.payInterests(2))
    self.assertEqual(0, player.amount)

  def testSellShares(self):
    player = Player()
    player.addCard(FactoryCard(Resources.Iron, 1, 1, 0))
    player.addCard(LoanCard(5, 2, 0))
    player.addCard(ShareCard(Resources.Green, 3))
    player.addCard(ShareCard(Resources.Red, 2))
    player.addCard(LoanGoodsCard(Resources.Glass, 5, 1, 0))
    player.addCard(ShareCard(Resources.Green, 2))
    player.addCard(PlusLevelCard(1, 0, 0))
    player.addCard(ShareCard(Resources.Blue, 4))

    player.sellShares({
      Resources.Red:   5,
      Resources.Green: 10,
      Resources.Blue:  20
    })

    self.assertEqual(10 + 50 + 80, player.amount)
    for card in player.cards:
      self.assertNotEqual('share', card.name)

  def testFinalPayoff(self):
    player = Player()
    cards = [
      FactoryCard(Resources.Iron, 1, 1, 2),
      LoanCard(5, 2, -3),
      ShareCard(Resources.Green, 3),
      LoanCard(8, 2, -4),
      LoanGoodsCard(Resources.Glass, 5, 1, -4),
      EmergencyLoanCard(1, -8),
      PlusLevelCard(1, 0, 0),
      LoanCard(3, 2, -1),
    ];

    player.amount = 100
    for card in cards:
      player.addCard(card)
    player.finalPayoff()
    self.assertEqual(100 + (2 - 3 - 4 - 4 - 8 - 1), player.amount)

    player.amount = 10
    for card in cards:
      player.addCard(card)
    player.finalPayoff()
    self.assertEqual(0, player.amount)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
