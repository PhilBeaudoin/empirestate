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
  0,   # 0 and -  ==> 0$
  0,   # 0 and -  ==> 1$
  0,   #          ==> 2$
  0,   #          ==> 3$
  0,   #          ==> 4$
  4,   # 4 and -  ==> 5$
  7,   # 7 and -  ==> 6$
  10,  #          ==> 7$
  13,  #          ==> 8$
  16,  #          ==> 9$
  18,  #          ==> 10$
  20,  #          ==> 11$
  22,  #          ==> 12$
  23,  #          ==> 13$
  24,  #          ==> 14$
  25,  #          ==> 15$
  26,  #          ==> 16$
  27,  #          ==> 17$
  28,  #          ==> 18$
  29,  #          ==> 19$
       # 30 and + ==> 20$
]
_interestsBracket = [
  35,  #  30 and +  ==> 0$
  30,  #  25 and +  ==> 1$
  25,  #            ==> 2$
  20,  #            ==> 3$
       #  14 and -  ==> 4$
]

def cardsA():
  return [
    LoanCard(10, 1, -5),
    LoanCard(10, 1, -5),
    LoanCard(9, 1, -5),
    LoanCard(9, 1, -5),
    LoanCard(8, 1, -5),
    LoanCard(8, 1, -5),

    FactoryCard(Resources.Iron, 0, 1, 2),
    FactoryCard(Resources.Brick, 0, 1, 2),
    FactoryCard(Resources.Glass, 0, 1, 2),
    WorkforceCard(1, 2, 6),
    WorkforceCard(1, 2, 6),
    EquipmentCard(0, 1, 0),
    EquipmentCard(0, 1, 0),
    PlusLevelCard(1, 1, 0),
    MoneyForLevelCard(2, 2, 0, 0),

    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard()
  ]

def cardsB():
  return [
    LoanCard(8, 1, -4),
    LoanCard(7, 1, -4),
    LoanCard(7, 1, -4),
    LoanCard(6, 1, -4),
    LoanGoodsCard(Resources.Iron, 6, 1, -4),
    LoanGoodsCard(Resources.Brick, 6, 1, -4),
    LoanGoodsCard(Resources.Glass, 6, 1, -4),

    FactoryCard(Resources.Iron, 1, 1, 2),
    FactoryCard(Resources.Brick, 1, 1, 2),
    FactoryCard(Resources.Glass, 1, 1, 2),
    WorkforceCard(2, 2, 6),
    EquipmentCard(1, 1, 0),
    PlusLevelCard(1, 1, 0),
    MoneyForLevelCard(4, 3, 0, 0),
    MoneyForLevelCard(5, 4, 0, 0),
    FinalMoneyCard(2, 30),

    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),

    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard()
  ]

def cardsC():
  return [
    LoanCard(16, 1, -4),
    LoanGoodsCard(Resources.Iron, 8, 1, -4),
    LoanGoodsCard(Resources.Brick, 8, 1, -4),
    LoanGoodsCard(Resources.Glass, 8, 1, -4),

    FactoryCard(Resources.Iron, 2, 1, 2),
    FactoryCard(Resources.Brick, 2, 1, 2),
    FactoryCard(Resources.Glass, 2, 1, 2),
    WorkforceCard(6, 3, 6),
    EquipmentCard(4, 2, 0),
    MoneyForLevelCard(6, 5, 0, 0),
    ShareCard(Resources.Red, 1),
    ShareCard(Resources.Green, 1),
    ShareCard(Resources.Blue, 1),

    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),
    ActionCard(),

    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard(),
    ConfidenceDecreaseCard()
  ]

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
      FinalRoofCard(8, 4),
      FinalRoofCard(8, 4),
      FinalRoofCard(8, 4),
      RoofCard(7, 7, 4),
      RoofCard(7, 7, 4),
      RoofCard(7, 7, 4),
      RoofCard(6, 6, 3),
      RoofCard(6, 6, 3),
      RoofCard(5, 5, 3),
      RoofCard(5, 5, 3),
      RoofCard(4, 4, 2),
      RoofCard(4, 4, 2),
      RoofCard(3, 3, 2),
      RoofCard(3, 3, 2),
      RoofCard(2, 0, 0),
      RoofCard(2, 0, 0),
      RoofCard(2, 0, 0)
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
    if player.ident in track[-1]:
      return  # Already on last space, moving it could cause it to go behind
              # another token on that same space.
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
            self.shareScore[firm] - self.buildingColumn[firm].getRegress())

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
    player.addCard(column.popLargest().flip())
    player.setLevelCard(column.roof.flip())
    column.setRoof(self.roofStack.pop())
    self.advanceShareScore(firm, column.roof.progress)

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
      self.assertEqual(22*3 + 3 + 5, len(b.cardStack))
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
    self.assertEqual({2: 10}, b.positionsOnFirmTrack(Resources.Red))
    b.resetFirmTrack(Resources.Red)
    b.advancePlayerOnFirmTrack(p1, Resources.Red, 10)
    b.advancePlayerOnFirmTrack(p3, Resources.Red, 15)
    self.assertEqual([1, 3], b.playerOrderOnFirmTrack(Resources.Red))
    self.assertEqual({1: 10, 3: 10}, b.positionsOnFirmTrack(Resources.Red))
    b.advancePlayerOnFirmTrack(p1, Resources.Red, 10)
    self.assertEqual([1, 3], b.playerOrderOnFirmTrack(Resources.Red))
    self.assertEqual({1: 10, 3: 10}, b.positionsOnFirmTrack(Resources.Red))

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
    b.buildingColumn[Resources.Red].setRoof(RoofCard(1, 3, 8))
    b.buildingColumn[Resources.Green] = BuildingColumn(Resources.Green, [
        BuildingCard(2, Resources.Green, Resources.Bank)])
    b.buildingColumn[Resources.Green].setRoof(RoofCard(1, 1, 9))
    b.buildingColumn[Resources.Blue] = BuildingColumn(Resources.Blue, [
        BuildingCard(2, Resources.Blue, Resources.Bank)])
    b.buildingColumn[Resources.Blue].setRoof(RoofCard(1, 2, 3))
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
    testCases = [(0, 0), (1, 5), (4, 5), (5, 6), (7, 6), (9, 7), (17, 10),
                 (18, 10), (19, 11), (29, 19), (30, 20), (35, 20)]
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
    b.roofStack = [RoofCard(5, 5, 3)]
    column.setRoof(RoofCard(4, 4, 2))

    p.amount = 20
    b.buildForFirm(p, Resources.Red)

    self.assertEqual(0, p.amount)
    self.assertEqual(4, p.getLevel())
    self.assertIn(ShareCard(Resources.Red, 3), p.cards)
    self.assertEqual(10, b.revenues[Resources.Red])
    self.assertEqual(5, b.revenues[Resources.Glass])
    self.assertEqual(5, b.shareScore[Resources.Red])
    self.assertEqual(5, column.length())
    self.assertEqual(6, column.getLevel())

def main():
    unittest.main()

if __name__ == '__main__':
    main()
