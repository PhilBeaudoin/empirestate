import unittest
from random import shuffle, seed
import json
from resources import Resources, Firms, Goods, FirmsOrGoods
import resources
from buildingcolumn import BuildingColumn
from cardcolumn import CardColumn
from cards import *
from player import Player

_initialConfidenceMarker = 40
_firmTrackTrigger = 6
_firmTrackLength = 10
_shareValueBracket = [
  4,   # 4 and -  ==> 0$
  8,   # 8 and -  ==> 1$
  11,  #          ==> 2$
  14,  #          ==> 3$
  17,  #          ==> 4$
  19,  #          ==> 5$
  21,  #          ==> 6$
  23,  #          ==> 7$
  25,  #          ==> 8$
  28,  #          ==> 9$
  31,  #          ==> 10$
  34,  #          ==> 11$
       # 35 and + ==> 12$
]
_interestsBracket = [
  35,  #  35 and +  ==> 0$
  30,  #  30 and +  ==> 1$
  25,  #  25 and +  ==> 2$
  20,  #  20 and +  ==> 3$
       #  19 and -  ==> 4$
]

def cardsA():
  return [
    LoanCard(10, 1, 1),
    LoanCard(9, 1, 1),
    LoanCard(9, 1, 1),
    LoanCard(8, 1, 1),
    LoanCard(8, 1, 1),
    LoanCard(7, 1, 1),

    PlusLevelCard(1, 1),
    PlusLevelCard(1, 1),
    WorkforceCard(1, 2),
    WorkforceCard(0, 1),
    WorkforceCard(0, 1),
    EquipmentCard(1, 2),
    EquipmentCard(0, 1),
    EquipmentCard(0, 1),
    FactoryCard(Resources.Iron, 1, 1),
    FactoryCard(Resources.Brick, 1, 1),
    FactoryCard(Resources.Glass, 1, 1),

    GoodsCard(Resources.Iron, 5, 0),
    GoodsCard(Resources.Brick, 5, 0),
    GoodsCard(Resources.Glass, 5, 0),
    MoneyForLevelCard(3, 5, 1),
    MoneyForLevelCard(4, 6, 1),

    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
  ]

def cardsB():
  return [
    LoanCard(12, 2, 2),
    LoanCard(11, 2, 2),
    LoanCard(11, 2, 2),
    LoanCard(10, 2, 2),
    LoanCard(9, 2, 2),

    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),

    WorkforceCard(2, 2),
    WorkforceCard(1, 1),
    EquipmentCard(2, 2),
    EquipmentCard(1, 1),
    FactoryCard(Resources.Iron, 2, 1),
    FactoryCard(Resources.Brick, 2, 1),
    FactoryCard(Resources.Glass, 2, 1),

    GoodsCard(Resources.Iron, 7, 2),
    GoodsCard(Resources.Brick, 7, 2),
    GoodsCard(Resources.Glass, 7, 2),
    BonusTokenCard(5, 0),
    BonusTokenCard(5, 0),
    BonusTokenCard(5, 0),

    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
  ]

def cardsC():
  return [
    LoanCard(8, 2, 3),
    LoanCard(7, 2, 3),

    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),

    ShareCard(Resources.Red, 1),
    ShareCard(Resources.Green, 1),
    ShareCard(Resources.Blue, 1),
    WorkforceCard(4, 2),
    EquipmentCard(4, 2),

    MoneyForLevelCard(5, 8, 1),
    MoneyForLevelCard(6, 9, 1),
    UpgradeCard(0),
    UpgradeCard(0),
    UpgradeCard(0),
    UpgradeCard(0),
    UpgradeCard(0),

    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
  ]

def initialBuildings(firm):
  first = resources.mainGoods(firm)
  second = resources.nextGoods(first)
  third = resources.nextGoods(second)
  result = [
    BuildingCard(3, firm, firm),
    BuildingCard(3, firm, firm),
    BuildingCard(3, firm, firm),
    BuildingCard(4, firm, first),
    BuildingCard(4, firm, first),
    BuildingCard(4, firm, first),
    BuildingCard(5, firm, second),
    BuildingCard(5, firm, second),
    BuildingCard(5, firm, second),
    BuildingCard(6, firm, third),
    BuildingCard(6, firm, third),
    BuildingCard(6, firm, third),
    BuildingCard(6, firm, third),
  ]
  shuffle(result)
  return result

class Board:
  def __init__(self):
    self.roofStack = [
      FinalRoofCard(10),
      FinalRoofCard(10),
      FinalRoofCard(10),
      RoofCard(6, 10),
      RoofCard(6, 10),
      RoofCard(6, 9),
      RoofCard(6, 8),
      RoofCard(6, 7),
      RoofCard(5, 6),
      RoofCard(5, 5),
      RoofCard(4, 4),
      RoofCard(4, 3),
      RoofCard(3, 2),
      RoofCard(3, 1),
      RoofCard(2, 0),
      RoofCard(2, 0),
      RoofCard(2, 0)
    ]
    self.bonusCardForFirm = {
      Resources.Red: BonusFactoryCard(1),
      Resources.Green: BonusWorkforceCard(1),
      Resources.Blue: BonusEquipmentCard(1)
    }
    self.investmentActionCircles = [
      { 'counts': [1, 1], 'playerId': None },
      { 'counts': [2], 'playerId': None },
      { 'counts': [3], 'playerId': None },
      { 'counts': [2, 2], 'playerId': None },
      { 'counts': [4], 'playerId': None },
    ]
    self.confidenceMarker = _initialConfidenceMarker
    self.shareScore = {firm: 0 for firm in Firms}
    self.buildingColumn = {}
    for firm in Firms:
      self.buildingColumn[firm] = BuildingColumn(firm, initialBuildings(firm))
      self.buildingColumn[firm].setRoof(self.roofStack.pop())
    A = list(cardsA())
    B = list(cardsB())
    C = list(cardsC())
    shuffle(A)
    shuffle(B)
    shuffle(C)
    self.cardStack = C + B + A
    self.cardsAvailable = []
    self.goodsOfCard = []
    self.revenues = {resource: 0 for resource in FirmsOrGoods}
    self.firmTracks = \
        {firm: [[] for i in range(_firmTrackLength)] for firm in Firms}

  def prepareTurn(self):
    # Draw 11 cards.
    self.cardsAvailable = []
    while len(self.cardsAvailable) < 11:
      card = self.cardStack.pop()
      if card.type == CardTypes.ConfidenceDecrease:
        self.advanceConfidenceMarker(1)
      else:
        self.cardsAvailable.insert(0, card)
    self.goodsOfCard = [good for good in Goods] + [None] * 8

  def getCardByIndex(self, cardIndex):
    return self.cardsAvailable[cardIndex]

  def removeCardByIndex(self, cardIndex):
    del self.cardsAvailable[cardIndex]
    del self.goodsOfCard[cardIndex]

  def goodsOfCardByIndex(self, cardIndex):
    return self.goodsOfCard[cardIndex]

  def advancePlayerOnFirmTrack(self, player, firm, count):
    track = self.firmTracks[firm]
    newSpace = min(count - 1, len(track) - 1)
    for i, space in enumerate(track):
      if player.ident in space:
        space.remove(player.ident)
        newSpace = min(i + count, len(track) - 1)
        break
    track[newSpace].append(player.ident)

  def resetFirmTrack(self, firm):
    self.firmTracks[firm] = [[] for i in range(_firmTrackLength)]

  def playerOrderOnFirmTrack(self, firm):
    return [item for sublist in reversed(self.firmTracks[firm])
            for item in sublist]

  def positionsOnFirmTrack(self, firm):
    positions = {}
    for position, space in enumerate(self.firmTracks[firm]):
      for playerId in space:
        positions[playerId] = position + 1
    return positions

  def isFirmTrackTriggering(self, firm):
    for space in self.firmTracks[firm][_firmTrackTrigger - 1:]:
      if space:
        return True
    return False

  def resetInvestmentActionCircles(self):
    for circle in self.investmentActionCircles:
      circle['playerId'] = None

  def putPlayerOnInvestmentCircle(self, player, circleIndex):
    circle = self.investmentActionCircles[circleIndex]
    if circle['playerId'] is not None:
      raise RuntimeError('Placing a player on a circle that has already one.')
    circle['playerId'] = player.ident

  def getNewPlayerOrder(self, currentOrder):
    currentOrderIdents = [player.ident for player in currentOrder]
    for circle in reversed(self.investmentActionCircles):
      playerId = circle['playerId']
      if playerId is not None:
        currentOrderIdents.remove(playerId)
        currentOrderIdents.insert(0, playerId)
    return currentOrderIdents

  def advanceShareScore(self, firm, count):
    self.shareScore[firm] = min(self.shareScore[firm] + count,
        self.confidenceMarker - 1)

  def advanceConfidenceMarker(self, count):
    self.confidenceMarker = max(1, self.confidenceMarker - count)
    for firm in Firms:
      while (self.shareScore[firm] >= self.confidenceMarker):
        self.shareScore[firm] = max(0,
            self.shareScore[firm] - self.buildingColumn[firm].getProgress())

  def getShareValueForScore(self, score):
    for value, bound in enumerate(_shareValueBracket):
      if score <= bound:
        return value
    return len(_shareValueBracket)

  def getShareValue(self, firm):
    return self.getShareValueForScore(self.shareScore[firm])

  def getInterestsForMarker(self, marker):
    for value, bound in enumerate(_interestsBracket):
      if marker >= bound:
        return value
    return len(_interestsBracket)

  def getInterests(self):
    return self.getInterestsForMarker(self.confidenceMarker)

  def buildForFirm(self, player, firm):
    if not self.roofStack:
      raise RuntimeError('Cannot build firm: no more roof card left.')
    column = self.buildingColumn[firm]
    payments = player.payForBuilding(column)
    for resource in FirmsOrGoods:
      self.revenues[resource] += payments[resource]
    buildingCard = column.popLargest()
    roofCard = column.roof
    self.advanceShareScore(firm, roofCard.progress)
    player.addCard(buildingCard.flip())
    player.setLevelCard(roofCard.flip())
    column.setRoof(self.roofStack.pop())

  def printState(self):
    for firm in Firms:
      print 'Column ' + Resources.reverse_mapping[firm]
      self.buildingColumn[firm].printState()

class BoardTests(unittest.TestCase):
  def testInitialSetup(self):
    # Try a bunch of "random" boards, use an initial seed, however, so that the
    # test is deterministic.
    seed(10)
    for i in xrange(100):
      b = Board()
      self.assertEqual(2, b.buildingColumn[Resources.Red].cardColumn.length())
      self.assertEqual(2, b.buildingColumn[Resources.Green].cardColumn.length())
      self.assertEqual(2, b.buildingColumn[Resources.Blue].cardColumn.length())
      self.assertEqual(2, b.buildingColumn[Resources.Red].roof.cardCount)
      self.assertEqual(2, b.buildingColumn[Resources.Green].roof.cardCount)
      self.assertEqual(2, b.buildingColumn[Resources.Blue].roof.cardCount)
      self.assertEqual(80, len(b.cardStack))
      self.assertEqual(0, b.revenues[Resources.Red])
      self.assertEqual(0, b.revenues[Resources.Green])
      self.assertEqual(0, b.revenues[Resources.Blue])
      self.assertEqual(0, b.revenues[Resources.Iron])
      self.assertEqual(0, b.revenues[Resources.Brick])
      self.assertEqual(0, b.revenues[Resources.Glass])

  def testPrepareTurn(self):
    # Try a bunch of "random" boards, use an initial seed, however, so that the
    # test is deterministic.
    seed(10)
    for i in xrange(100):
      b = Board()
      b.prepareTurn()
      self.assertEqual(11, len(b.cardsAvailable))
      for card in b.cardsAvailable:
        self.assertIn(card, cardsA())
      self.assertEqual(Resources.Glass, b.goodsOfCardByIndex(2))
      b.removeCardByIndex(1)
      self.assertEqual(Resources.Glass, b.goodsOfCardByIndex(1))
      self.assertIsNone(b.goodsOfCardByIndex(2))
      b.prepareTurn()
      self.assertEqual(11, len(b.cardsAvailable))
      for card in b.cardsAvailable:
        self.assertIn(card, cardsA())
      b.prepareTurn()
      self.assertEqual(11, len(b.cardsAvailable))
      for card in b.cardsAvailable:
        self.assertIn(card, cardsB())
      b.prepareTurn()
      self.assertEqual(11, len(b.cardsAvailable))
      for card in b.cardsAvailable:
        self.assertIn(card, cardsB())
      b.prepareTurn()
      self.assertEqual(11, len(b.cardsAvailable))
      for card in b.cardsAvailable:
        self.assertIn(card, cardsC())
      b.prepareTurn()
      self.assertEqual(11, len(b.cardsAvailable))
      for card in b.cardsAvailable:
        self.assertIn(card, cardsC())

  def testPrepareTurnWithConfidenceDecrease(self):
      b = Board()
      # cardStack is emptied from the last card, so the first
      # ConfidenceDecreaseCard in the following list will be ignored.
      b.cardStack = [UpgradeCard(i) for i in range(11)]
      b.cardStack.insert(0, ConfidenceDecreaseCard())
      b.cardStack.insert(3, ConfidenceDecreaseCard())
      b.cardStack.insert(3, ConfidenceDecreaseCard())
      b.cardStack.insert(6, ConfidenceDecreaseCard())
      b.prepareTurn()
      self.assertEqual([UpgradeCard(i) for i in range(11)], b.cardsAvailable)
      self.assertEqual(_initialConfidenceMarker - 3, b.confidenceMarker)

  def testAdvancePlayerOnFirmTrack(self):
    b = Board()
    p0 = Player(0)
    p1 = Player(1)
    p2 = Player(2)
    p3 = Player(3)
    b.advancePlayerOnFirmTrack(p0, Resources.Red, 3)
    b.advancePlayerOnFirmTrack(p3, Resources.Red, 5)
    b.advancePlayerOnFirmTrack(p0, Resources.Red, 2)
    b.advancePlayerOnFirmTrack(p1, Resources.Red, 5)
    b.advancePlayerOnFirmTrack(p0, Resources.Red, 2)
    self.assertEqual([0,3,1], b.playerOrderOnFirmTrack(Resources.Red))
    self.assertEqual({0: 7, 1: 5, 3: 5}, b.positionsOnFirmTrack(Resources.Red))
    b.resetFirmTrack(Resources.Red)
    self.assertEqual([], b.playerOrderOnFirmTrack(Resources.Red))
    self.assertEqual({}, b.positionsOnFirmTrack(Resources.Red))
    b.advancePlayerOnFirmTrack(p2, Resources.Blue, 100)
    self.assertEqual([2], b.playerOrderOnFirmTrack(Resources.Blue))
    self.assertEqual({2: 10}, b.positionsOnFirmTrack(Resources.Blue))
    b.advancePlayerOnFirmTrack(p2, Resources.Red, 5)
    b.advancePlayerOnFirmTrack(p2, Resources.Red, 5)
    self.assertEqual([2], b.playerOrderOnFirmTrack(Resources.Red))
    self.assertEqual({2: 10}, b.positionsOnFirmTrack(Resources.Blue))

  def testIsFirmTrackTriggering(self):
    b = Board()
    p0 = Player(0)
    b.advancePlayerOnFirmTrack(p0, Resources.Red, _firmTrackTrigger - 1)
    self.assertFalse(b.isFirmTrackTriggering(Resources.Red))
    b.advancePlayerOnFirmTrack(p0, Resources.Red, 1)
    self.assertTrue(b.isFirmTrackTriggering(Resources.Red))
    b.advancePlayerOnFirmTrack(p0, Resources.Red, 100)
    self.assertTrue(b.isFirmTrackTriggering(Resources.Red))

  def testChangeShareScore(self):
    b = Board()
    # Doctor the board
    b.buildingColumn[Resources.Red] = BuildingColumn(Resources.Red, [
        BuildingCard(2, Resources.Red, Resources.Bank)])
    b.buildingColumn[Resources.Red].setRoof(RoofCard(1, 8))
    b.buildingColumn[Resources.Green] = BuildingColumn(Resources.Green, [
        BuildingCard(2, Resources.Green, Resources.Bank)])
    b.buildingColumn[Resources.Green].setRoof(RoofCard(1, 9))
    b.buildingColumn[Resources.Blue] = BuildingColumn(Resources.Blue, [
        BuildingCard(2, Resources.Blue, Resources.Bank)])
    b.buildingColumn[Resources.Blue].setRoof(RoofCard(1, 3))
    b.confidenceMarker = 20
    self.assertEqual(0, b.shareScore[Resources.Red])
    b.advanceShareScore(Resources.Red, 5)
    self.assertEqual(5, b.shareScore[Resources.Red])
    b.advanceShareScore(Resources.Red, 8)
    self.assertEqual(13, b.shareScore[Resources.Red])
    b.advanceShareScore(Resources.Red, 10)
    self.assertEqual(19, b.shareScore[Resources.Red])
    b.advanceShareScore(Resources.Green, 20)
    self.assertEqual(19, b.shareScore[Resources.Green])
    b.advanceShareScore(Resources.Blue, 18)
    self.assertEqual(18, b.shareScore[Resources.Blue])
    b.advanceConfidenceMarker(1)
    self.assertEqual(19, b.confidenceMarker)
    self.assertEqual(11, b.shareScore[Resources.Red])
    self.assertEqual(10, b.shareScore[Resources.Green])
    self.assertEqual(18, b.shareScore[Resources.Blue])
    b.advanceConfidenceMarker(5)
    self.assertEqual(14, b.confidenceMarker)
    self.assertEqual(11, b.shareScore[Resources.Red])
    self.assertEqual(10, b.shareScore[Resources.Green])
    self.assertEqual(12, b.shareScore[Resources.Blue])
    b.advanceConfidenceMarker(40)
    self.assertEqual(1, b.confidenceMarker)
    self.assertEqual(0, b.shareScore[Resources.Red])
    self.assertEqual(0, b.shareScore[Resources.Green])
    self.assertEqual(0, b.shareScore[Resources.Blue])

  def testNewPlayerOrder(self):
    b = Board()
    players = [ Player(0), Player(1), Player(2), Player(3) ]
    self.assertEqual([0, 1, 2, 3], b.getNewPlayerOrder(players))
    b.putPlayerOnInvestmentCircle(players[0], 3)
    self.assertEqual([0, 1, 2, 3], b.getNewPlayerOrder(players))
    b.putPlayerOnInvestmentCircle(players[1], 1)
    self.assertEqual([1, 0, 2, 3], b.getNewPlayerOrder(players))
    b.putPlayerOnInvestmentCircle(players[1], 4)
    self.assertEqual([1, 0, 2, 3], b.getNewPlayerOrder(players))
    b.putPlayerOnInvestmentCircle(players[2], 0)
    self.assertEqual([2, 1, 0, 3], b.getNewPlayerOrder(players))
    b.resetInvestmentActionCircles()
    self.assertEqual([0, 1, 2, 3], b.getNewPlayerOrder(players))
    b.putPlayerOnInvestmentCircle(players[3], 0)
    b.putPlayerOnInvestmentCircle(players[3], 1)
    b.putPlayerOnInvestmentCircle(players[3], 2)
    b.putPlayerOnInvestmentCircle(players[3], 3)
    b.putPlayerOnInvestmentCircle(players[3], 4)
    self.assertEqual([3, 0, 1, 2], b.getNewPlayerOrder(players))

  def testGetShareValue(self):
    b = Board()
    self.assertEqual(0, b.getShareValue(Resources.Red))
    testCases = [(0, 0), (4, 0), (5, 1), (8, 1), (9, 2), (15, 4), (17, 4),
                 (18, 5), (34, 11), (35, 12), (60, 12)]
    for testCase in testCases:
      b.shareScore[Resources.Red] = testCase[0]
      self.assertEqual(testCase[1], b.getShareValue(Resources.Red))

  def testGetInterests(self):
    b = Board()
    self.assertEqual(0, b.getInterests())
    testCases = [(36, 0), (35, 0), (34, 1), (30, 1), (29, 2), (25, 2), (24, 3),
                 (22, 3), (19, 4), (1, 4)]
    for testCase in testCases:
      b.confidenceMarker = testCase[0]
      self.assertEqual(testCase[1], b.getInterests())

  def testBuildForFirm(self):
    b = Board()
    p = Player()
    # Doctor the board
    for resource in FirmsOrGoods:
      b.revenues[resource] = 0
    column = BuildingColumn(Resources.Red, [
        BuildingCard(5, Resources.Red, Resources.Glass),
        BuildingCard(6, Resources.Red, Resources.Iron),
        BuildingCard(5, Resources.Red, Resources.Glass),
        BuildingCard(2, Resources.Red, Resources.Bank),
        BuildingCard(3, Resources.Red, Resources.Red),
        BuildingCard(3, Resources.Red, Resources.Red),
        ])
    b.buildingColumn[Resources.Red] = column
    b.roofStack = [RoofCard(5, 6)]
    column.setRoof(RoofCard(4, 3))

    p.amount = 20
    b.buildForFirm(p, Resources.Red)

    self.assertEqual(0, p.amount)
    self.assertEqual(4, p.getLevel())
    self.assertIn(ShareCard(Resources.Red, 3), p.cards)
    self.assertEqual(10, b.revenues[Resources.Red])
    self.assertEqual(5, b.revenues[Resources.Glass])
    self.assertEqual(3, b.shareScore[Resources.Red])
    self.assertEqual(5, column.length())
    self.assertEqual(6, column.getLevel())

def main():
    unittest.main()

if __name__ == '__main__':
    main()
