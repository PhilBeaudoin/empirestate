import unittest
import resources
import gamecontroller
from board import Board
from buildingcolumn import BuildingColumn
from resources import Resources, Firms, Goods, FirmsOrGoods
from cards import *
import copy

# For each turn, given the current share score, give the estimated final share
# value
finalShareScore = [
  [25 for i in range(50)],
  [20 + i/4 for i in range(50)],
  [18 + i/3 for i in range(50)],
  [15 + i/2 for i in range(50)],
  [10 + 3*i/4 for i in range(50)],
  [i for i in range(50)],
]

# For each turn, given the current confidence marker, give the confidence marker
# level at turn j
predictedConfidenceMarker = [
 [
   [i for i in range(50)], # At turn 1, predicting for turn 1
   [max(0, i - 3) for i in range(50)],
   [max(0, i - 6) for i in range(50)],
   [max(0, i - 9) for i in range(50)],
   [max(0, i - 12) for i in range(50)],
   [max(0, i - 15) for i in range(50)],
 ],
 [
   [i for i in range(50)], # At turn 2, predicting for turn 1
   [i for i in range(50)], # At turn 2, predicting for turn 2
   [max(0, i - 3) for i in range(50)],
   [max(0, i - 6) for i in range(50)],
   [max(0, i - 9) for i in range(50)],
   [max(0, i - 12) for i in range(50)],
 ],
 [
   [i for i in range(50)], # At turn 3, predicting for turn 1
   [i for i in range(50)], # At turn 3, predicting for turn 2
   [i for i in range(50)], # At turn 3, predicting for turn 3
   [max(0, i - 3) for i in range(50)],
   [max(0, i - 6) for i in range(50)],
   [max(0, i - 9) for i in range(50)],
 ],
 [
   [i for i in range(50)], # At turn 4, predicting for turn 1
   [i for i in range(50)], # At turn 4, predicting for turn 2
   [i for i in range(50)], # At turn 4, predicting for turn 3
   [i for i in range(50)], # At turn 4, predicting for turn 4
   [max(0, i - 3) for i in range(50)],
   [max(0, i - 6) for i in range(50)],
 ],
 [
   [i for i in range(50)], # At turn 5, predicting for turn 1
   [i for i in range(50)], # At turn 5, predicting for turn 2
   [i for i in range(50)], # At turn 5, predicting for turn 3
   [i for i in range(50)], # At turn 5, predicting for turn 4
   [i for i in range(50)], # At turn 5, predicting for turn 5
   [max(0, i - 3) for i in range(50)],
 ],
 [
   [i for i in range(50)], # At turn 6, predicting for turn 1
   [i for i in range(50)], # At turn 6, predicting for turn 2
   [i for i in range(50)], # At turn 6, predicting for turn 3
   [i for i in range(50)], # At turn 6, predicting for turn 4
   [i for i in range(50)], # At turn 6, predicting for turn 5
   [i for i in range(50)], # At turn 6, predicting for turn 6
 ],
]

class BasicAi:
  def __init__(self, player):
    self.player = player

  def takeAction(self, gameController):
    board = gameController.board
    bestMove = { 'value': -1000, 'move': None }
    for cardIndex, card in enumerate(board.cardsAvailable):
      value = self.computeGetCardValue(gameController, cardIndex)
      if value > bestMove['value']:
        bestMove['value'] = value
        bestMove['action'] = gameController.actionGetCard
        bestMove['params'] = [cardIndex]
    for goods in Goods:
      value = self.computeGetMoneyOnGoodsValue(gameController, goods)
      if value > bestMove['value']:
        bestMove['value'] = value
        bestMove['action'] = gameController.actionGetMoneyOnGoods
        bestMove['params'] = [goods]
    for circleIndex, circle in enumerate(board.investmentActionCircles):
      for firms in self.generateFirmTuples(len(circle['counts'])):
        value = self.computeInvestValue(gameController, circleIndex, firms)
        if value > bestMove['value']:
          bestMove['value'] = value
          bestMove['action'] = gameController.actionInvest
          bestMove['params'] = [circleIndex, firms]
    for firm in Firms:
      value = self.computeBuildValue(gameController, firm)
      if value > bestMove['value']:
        bestMove['value'] = value
        bestMove['action'] = gameController.actionBuild
        bestMove['params'] = [firm]
    for card in board.cardsAvailable:
      if card.name == 'share':
        value = self.computeSellShareValue(gameController, card)
        if value > bestMove['value']:
          bestMove['value'] = value
          bestMove['action'] = gameController.actionSellShare
          bestMove['params'] = [card]
    for card in board.cardsAvailable:
      if card.name == 'loan':
        value = self.computePayLoanValue(gameController, card)
        if value > bestMove['value']:
          bestMove['value'] = value
          bestMove['action'] = gameController.actionPayLoan
          bestMove['params'] = [card]
    value = self.computeSkipActionValue(gameController)
    if value > bestMove['value']:
      bestMove['value'] = value
      bestMove['action'] = gameController.actionSkipAction
      bestMove['params'] = []
    bestMove['action'](self.player, *bestMove['params'])

  def computePayoffForCard(self, card, level):
    card = copy.copy(card)
    directPayoff = card.payoff(level, self.player.bonusCards)
    return directPayoff + (card.amount * 0.7 if card.name == 'factory' else 0)

  def computeGetCardValue(self, gameController, cardIndex):
    turn = gameController.turnIndex
    board = gameController.board
    card = board.getCardByIndex(cardIndex)
    goods = board.goodsOfCardByIndex(cardIndex)
    valueToAdvanceOnFirmTrack = 0
    if goods:
      valueToAdvanceOnFirmTrack = self.computeAdvanceOnFirmValue(
          gameController, resources.mainFirm(goods), 1)

    # Estimate 1 more level per round
    valueForCard = 0
    level = self.player.getLevel()
    for i in range(turn, 6):
      valueForCard += self.computePayoffForCard(card, level)
      level += 1

    costForUpkeep = 0
    confidenceMarker = board.confidenceMarker
    for i in range(turn, 6):
      prediction = predictedConfidenceMarker[turn][i][confidenceMarker]
      interests = board.getInterestsForMarker(prediction)
      costForUpkeep += card.upkeep * interests

    # TODO: That's a bit rough...
    extraValue = 0
    if card.name == 'plusLevel':
      extraValue = 2 * card.bonus * (6 - turn)
    elif card.name == 'goods':
      extraValue = card.amount
    elif card.name == 'loan':
      buildingValue = 0
      for firm in Firms:
        if not self.player.canPayForBuilding(board.buildingColumn[firm]):
          self.player.amount += card.value
          if self.player.canPayForBuilding(board.buildingColumn[firm]):
            buildingValue = max(buildingValue,
                                self.computeBuildingValue(gameController, firm))
          self.player.amount -= card.value
      extraValue = buildingValue * 0.7

    return valueToAdvanceOnFirmTrack + valueForCard + extraValue - costForUpkeep

  def computeGetMoneyOnGoodsValue(self, gameController, goods):
    board = gameController.board
    return -(-board.revenues[goods] / 2) + self.computeAdvanceOnFirmValue(
        gameController, resources.mainFirm(goods), 1) + 0.1

  def computeInvestValue(self, gameController, circleIndex, firms):
    board = gameController.board
    circle = board.investmentActionCircles[circleIndex]
    if circle['playerId'] is not None:
      return -1000
    counts = circle['counts']
    value = sum([self.computeAdvanceOnFirmValue(gameController, firm, count)
        for firm, count in zip(firms, counts)])
    return value + 0.1 * (5 - circleIndex)

  def computeBuildValue(self, gameController, firm):
    board = gameController.board
    if not self.player.canPayForBuilding(board.buildingColumn[firm]):
      return -1000
    return self.computeBuildingValue(gameController, firm)

  def computeSellShareValue(self, gameController, card):
    turn = gameController.turnIndex
    board = gameController.board
    shareScore = board.shareScore[card.firm]
    currentValue = board.getShareValueForScore(shareScore)
    finalValue = board.getShareValueForScore(finalShareScore[turn][shareScore])
    return card.multiplicity * (currentValue - finalValue)

  def computePayLoanValue(self, gameController, card):
    # TODO: For now, never repay loan. It's hard to evaluate the loss in
    # liquidity.
    return -1000

  def computeSkipActionValue(self, gameController):
    return gameController.amountToSkipAction

  def computeBuildingValue(self, gameController, firm):
    turn = gameController.turnIndex
    board = gameController.board
    column = board.buildingColumn[firm]
    buildingCard = column.getLargest()
    shareCard = buildingCard.flip()
    roofCard = column.roof
    # TODO: This disregards the confidence marker.
    oldShareScore = board.shareScore[firm]
    newShareScore = oldShareScore + roofCard.progress

    oldShareValue = board.getShareValueForScore(
        finalShareScore[turn][oldShareScore])
    newShareValue = board.getShareValueForScore(
        finalShareScore[turn][newShareScore])

    valueDiff = newShareValue - oldShareValue
    valueForOldShares = 0
    for card in self.player.cards:
      if card.name == 'share' and card.firm == firm:
        valueForOldShares += card.multiplicity * valueDiff

    valueForNewShares = shareCard.multiplicity * newShareValue

    payoffBefore = 0
    payoffAfter = 0
    level = self.player.getLevel()
    for card in self.player.cards:
      payoffBefore += self.computePayoffForCard(card, level)
    newLevel = level + roofCard.flip().level - \
        (0 if not self.player.levelCard else self.player.levelCard.level)
    for card in self.player.cards:
      payoffAfter += self.computePayoffForCard(card, newLevel)
    valueForLevelIncrease = (payoffAfter - payoffBefore) * (6 - turn)

    # TODO: Factories shouldn't be counted in cost.
    cost = buildingCard.level * roofCard.cardCount

    return valueForOldShares + valueForNewShares + valueForLevelIncrease - cost

  def computeAdvanceOnFirmValue(self, gameController, firm, count):
    board = gameController.board
    revenues = board.revenues[firm]
    orderBefore = board.playerOrderOnFirmTrack(firm)
    positions = board.positionsOnFirmTrack(firm)
    amountBefore = 0
    positionAfter = count
    orderAfter = list(orderBefore)
    if self.player.ident in orderBefore:
      orderAfter.remove(self.player.ident)
      for ident in orderBefore:
        given = -(-revenues / 2)
        revenues -= given
        if ident == self.player.ident:
          amountBefore = given
          break
      positionAfter = positions[self.player.ident] + count
    index = 0
    for ident in orderAfter:
      if positions[ident] < positionAfter:
        break
      index += 1
    orderAfter.insert(index, self.player.ident)
    revenues = board.revenues[firm]
    for ident in orderAfter:
      given = -(-revenues / 2)
      revenues -= given
      if ident == self.player.ident:
        amountAfter = given
        break
    # TODO: Compute value of first position.
    return amountAfter - amountBefore

  def generateFirmTuples(self, n):
    if   n == 0: return []
    elif n == 1: return [[firm] for firm in Firms]
    elif n == 2:
      return [
        [Resources.Red, Resources.Green],
        [Resources.Red, Resources.Blue],
        [Resources.Green, Resources.Blue]
      ];
    elif n == 3:
      return [list(Firms)]
    raise RuntimeError('Trying to generate a tuple of firms with n: ' + str(n))

class BasicAiTests(unittest.TestCase):
  def testComputeGetCardValue(self):
    b = Board()
    gc = gamecontroller.GameController(b)
    p0, p1, p2, p3 = gc.players
    p0.amount = 0
    ai0, ai1, ai2, ai3 = [gc.ais[i] for i in range(4)]
    b.cardStack = [
      FactoryCard(Resources.Glass, 0, 1),
      WorkforceCard(0, 1),
      PlusLevelCard(1, 1),
      GoodsCard(Resources.Iron, 5, 0),
      MoneyForLevelCard(3, 3, 0),
      WorkforceCard(0, 1),
      ActionCard(),
      UpgradeCard(2),
      LoanCard(10, 1, 2),
      LoanCard(8, 1, 2),
      GoodsCard(Resources.Brick, 4, 0)]
    b.prepareTurn()
    b.revenues[Resources.Red] = 2
    b.revenues[Resources.Green] = 4
    b.revenues[Resources.Blue] = 8
    column = BuildingColumn(Resources.Red, [
        BuildingCard(5, Resources.Red, Resources.Glass),
        BuildingCard(3, Resources.Red, Resources.Red),
        ])
    b.buildingColumn[Resources.Red] = column
    column.setRoof(RoofCard(2, 1))
    b.buildingColumn[Resources.Green].setRoof(FinalRoofCard(5))
    b.buildingColumn[Resources.Blue].setRoof(FinalRoofCard(5))

    # Estimated confidence marker:
    confidenceMarker = [predictedConfidenceMarker[0][i][b.confidenceMarker]
        for i in range(6)]
    interests = sum([b.getInterestsForMarker(marker)
        for marker in confidenceMarker])
    totalLevel = sum(range(6))
    # First card gets 1 to advance on red.
    self.assertEqual(1 + totalLevel * 0.7 - interests,
        ai0.computeGetCardValue(gc, 0))
    # Second card gets 2 to advance on green.
    self.assertEqual(2 + totalLevel - interests, ai0.computeGetCardValue(gc, 1))
    # Second card gets 4 to advance on blue.
    self.assertEqual(4 + 2 * 6 - interests, ai0.computeGetCardValue(gc, 2))
    self.assertEqual(5, ai0.computeGetCardValue(gc, 3))
    self.assertEqual(9, ai0.computeGetCardValue(gc, 4))
    self.assertEqual(totalLevel - interests, ai0.computeGetCardValue(gc, 5))
    self.assertEqual(0, ai0.computeGetCardValue(gc, 6))
    self.assertEqual(-2 * interests, ai0.computeGetCardValue(gc, 7))
    buildingValue = 3 * b.getShareValueForScore(finalShareScore[0][1]) - 10
    self.assertEqual(buildingValue * 0.7 - interests,
        ai0.computeGetCardValue(gc, 8))
    self.assertEqual(-interests, ai0.computeGetCardValue(gc, 9))
    self.assertEqual(4, ai0.computeGetCardValue(gc, 10))

  def testComputeGetMoneyOnGoodsValue(self):
    b = Board()
    gc = gamecontroller.GameController(b)
    ai0, ai1, ai2, ai3 = [gc.ais[i] for i in range(4)]
    b.revenues[Resources.Iron] = 7  # + 4
    b.revenues[Resources.Red] = 9   # + 5
    self.assertEqual(9.1, ai0.computeGetMoneyOnGoodsValue(gc, Resources.Iron))

  def testComputeInvestValue(self):
    b = Board()
    gc = gamecontroller.GameController(b)
    p0, p1, p2, p3 = gc.players
    ai0, ai1, ai2, ai3 = [gc.ais[i] for i in range(4)]
    b.revenues[Resources.Red]   = 7   # + 4
    b.revenues[Resources.Green] = 10  # + 5
    b.revenues[Resources.Blue]  = 11  # + 6
    self.assertEqual(4 + 5 + 5*0.1, ai0.computeInvestValue(gc, 0,
        [Resources.Red, Resources.Green]))
    self.assertEqual(6 + 4*0.1, ai0.computeInvestValue(gc, 1, [Resources.Blue]))
    self.assertEqual(4 + 3*0.1, ai0.computeInvestValue(gc, 2, [Resources.Red]))
    self.assertEqual(5 + 6 + 2*0.1, ai0.computeInvestValue(gc, 3,
        [Resources.Green, Resources.Blue]))
    self.assertEqual(5 + 0.1, ai0.computeInvestValue(gc, 4, [Resources.Green]))
    b.putPlayerOnInvestmentCircle(p1, 1)
    self.assertEqual(-1000, ai0.computeInvestValue(gc, 1, [Resources.Green]))

  def testComputeSellShareValue(self):
    b = Board()
    gc = gamecontroller.GameController(b)
    ai0, ai1, ai2, ai3 = [gc.ais[i] for i in range(4)]
    b.advanceShareScore(Resources.Red, 17)
    currentValue = b.getShareValueForScore(17)
    finalValue = b.getShareValueForScore(finalShareScore[0][17])
    self.assertEqual((currentValue - finalValue) * 4,
        ai0.computeSellShareValue(gc, ShareCard(Resources.Red, 4)))

  def testComputePayLoanValue(self):
    b = Board()
    gc = gamecontroller.GameController(b)
    ai0, ai1, ai2, ai3 = [gc.ais[i] for i in range(4)]
    b.advanceShareScore(Resources.Red, 17)
    currentValue = b.getShareValueForScore(17)
    finalValue = b.getShareValueForScore(finalShareScore[0][17])
    self.assertEqual((currentValue - finalValue) * 4,
        ai0.computeSellShareValue(gc, ShareCard(Resources.Red, 4)))

  def testComputeBuildValue(self):
    b = Board()
    gc = gamecontroller.GameController(b)
    gc.turnIndex = 2
    p0, p1, p2, p3 = gc.players
    ai0, ai1, ai2, ai3 = [gc.ais[i] for i in range(4)]
    column = BuildingColumn(Resources.Red, [
        BuildingCard(5, Resources.Red, Resources.Glass),
        BuildingCard(2, Resources.Red, Resources.Bank),
        BuildingCard(3, Resources.Red, Resources.Red),
        BuildingCard(3, Resources.Red, Resources.Red),
        ])
    b.buildingColumn[Resources.Red] = column
    column.setRoof(RoofCard(4, 4))
    b.buildingColumn[Resources.Green].setRoof(FinalRoofCard(10))

    p0.amount = 100
    p0.addCard(ShareCard(Resources.Red, 2))
    p0.addCard(WorkforceCard(0, 1))
    b.advanceShareScore(Resources.Red, 17)

    valueBefore = b.getShareValueForScore(finalShareScore[2][17])
    valueAfter = b.getShareValueForScore(finalShareScore[2][21])
    expected = 2 * (valueAfter - valueBefore) + 3 * valueAfter + 4 * 4 - 20
    self.assertEqual(expected, ai0.computeBuildValue(gc, Resources.Red))
    self.assertEqual(-1000, ai0.computeBuildValue(gc, Resources.Green))
    p0.amount = 10
    self.assertEqual(-1000, ai0.computeBuildValue(gc, Resources.Red))

  def testComputeAdvanceOnFirmTrackValue(self):
    b = Board()
    gc = gamecontroller.GameController(b)
    p0, p1, p2, p3 = gc.players
    ai0, ai1, ai2, ai3 = [gc.ais[i] for i in range(4)]
    firm = Resources.Red
    b.revenues[firm] = 21  # 11, 5, 3, 1
    gc.advanceOnFirmTrack(p0, firm, 4)
    gc.advanceOnFirmTrack(p1, firm, 3)
    gc.advanceOnFirmTrack(p3, firm, 4)
    self.assertEqual(1, ai2.computeAdvanceOnFirmValue(gc, firm, 3))
    self.assertEqual(3, ai2.computeAdvanceOnFirmValue(gc, firm, 4))
    self.assertEqual(11, ai2.computeAdvanceOnFirmValue(gc, firm, 5))
    gc.advanceOnFirmTrack(p2, firm, 1)
    self.assertEqual(0, ai2.computeAdvanceOnFirmValue(gc, firm, 2))
    self.assertEqual(2, ai2.computeAdvanceOnFirmValue(gc, firm, 3))
    self.assertEqual(10, ai2.computeAdvanceOnFirmValue(gc, firm, 4))
    gc.advanceOnFirmTrack(p0, firm, 1)
    self.assertEqual(0, ai2.computeAdvanceOnFirmValue(gc, firm, 2))
    self.assertEqual(2, ai2.computeAdvanceOnFirmValue(gc, firm, 3))
    self.assertEqual(4, ai2.computeAdvanceOnFirmValue(gc, firm, 4))
    self.assertEqual(10, ai2.computeAdvanceOnFirmValue(gc, firm, 5))
    gc.advanceOnFirmTrack(p2, firm, 10)
    self.assertEqual(0, ai2.computeAdvanceOnFirmValue(gc, firm, 2))
    self.assertEqual(0, ai2.computeAdvanceOnFirmValue(gc, firm, 3))
    self.assertEqual(0, ai2.computeAdvanceOnFirmValue(gc, firm, 4))
    self.assertEqual(0, ai2.computeAdvanceOnFirmValue(gc, firm, 5))

def main():
    unittest.main()

if __name__ == '__main__':
    main()

