import unittest
import resources
from operator import itemgetter
from cardcolumn import CardColumn
from resources import Resources, Firms, Goods, FirmsOrGoods
from mixedcardserror import MixedCardsError
from buildingcolumn import BuildingColumn
from cards import *
from player import Player
from board import Board
from random import shuffle
import copy

_confidenceLossPerLoan = 1
_confidenceLossPerSale = 2
_confidenceLossPerEmergencyLoan = 3

class GameController:
  def __init__(self, board):
    self.board = board
    self.players = [Player(i, 3, 5+i) for i in range(4)]
    self.turnIndex = 0
    self.roundIndex = 0
    self.actionsOfRound = []
    self.actionsOfTurn = []
    self.actionsOfGame = []
    self.statistics = []

  def identsToPlayers(self, idents):
    players = []
    for ident in idents:
      for player in self.players:
        if player.ident == ident:
          players.append(player)
    return players

  def playGame(self):
    for i in xrange(6):
      self.prepareTurn()
      for j in xrange(6):
        for player in self.players:
          if player.numActions > j:
            self.takeAction(player)
        self.finalizeRound()
      self.finalizeTurn()

  def appendStatistics(self):
    amountPerPlayer = [0] * len(self.players)
    levelPerPlayer = [None] * len(self.players)
    amountOnFactoriesPerPlayer = [0] * len(self.players)
    numberOfSharePerPlayer = [0] * len(self.players)
    amountOnResources = {}
    buildings = {}
    for firm in Firms:
      buildings[firm] = {
        'size': self.board.buildingColumn[firm].cardColumn.length(),
        'level': self.board.buildingColumn[firm].cardColumn.getLevel()
      }

    for player in self.players:
      amountPerPlayer[player.initialIndex] += player.amount
      levelPerPlayer[player.initialIndex] = {}
      for firm in Firms:
        levelPerPlayer[player.initialIndex][firm] = \
            player.columns[firm].getLevel()
        for card in player.columns[firm].getCards():
          if card.type == 'factory':
            amountOnFactoriesPerPlayer[player.initialIndex] += card.amount
          elif card.type == 'share':
            numberOfSharePerPlayer[player.initialIndex] += card.multiplicity
    numberOfBuilds = 0
    for gameAction in self.actionsOfGame:
      for turnAction in gameAction['turnActions']:
        for roundAction in turnAction['roundActions']:
          if roundAction['action'] == 'build':
            numberOfBuilds += 1
    amountOnResources = dict(self.board.revenues)
    self.statistics.append({
      'buildings': buildings,
      'turnIndex': self.turnIndex,
      'amountPerPlayer': amountPerPlayer,
      'amountOnFactoriesPerPlayer': amountOnFactoriesPerPlayer,
      'numberOfSharePerPlayer': numberOfSharePerPlayer,
      'amountOnPlayers': sum(amountPerPlayer),
      'amountOnFactories': sum(amountOnFactoriesPerPlayer),
      'numberOfShares': sum(numberOfSharePerPlayer),
      'amountOnResources': amountOnResources,
      'totalAmount': sum(amountOnResources.values()) + sum(amountPerPlayer) + \
                     sum(amountOnFactoriesPerPlayer),
      'numberOfBuilds': numberOfBuilds,
      'shareScores': dict(self.board.shareScore),
      'buildingsComplete':
          sum([0 if self.board.buildingColumn[f].roof else 1 for f in Firms]),
      'levelPerPlayer': levelPerPlayer
    })

  def prepareTurn(self):
    self.board.prepareTurn()
    if self.turnIndex == 2 or self.turnIndex == 4:
      for player in self.players:
        player.numActions += 1

  def finalizeRound(self):
    # Log actions of round.
    self.actionsOfTurn.append({
      'roundIndex': self.roundIndex,
      'roundActions': self.actionsOfRound
    })
    self.actionsOfRound = []
    # Increment turn
    self.roundIndex += 1

  def finalizeTurn(self):
    # Players get payoff
    for player in self.players:
      player.getPayoff()  # TODO: Give them their sixth action if needed.

    # Distribute the money on the firm revenue areas that trigger.
    for firm in Firms:
      if self.board.isFirmTrackTriggering(firm):
        players = self.identsToPlayers(self.board.playerOrderOnFirmTrack(firm))
        for player in players:
          given = -(-self.board.revenues[firm] / 2)  # Trick to round up.
          player.amount += given
          self.board.revenues[firm] -= given
        # Return the bonus card if there's someone on the track.
        if players:
          players[0].removeBonusCard(self.board.bonusCardForFirm[firm])
        # Reset the track
        self.board.resetFirmTrack(firm)

    # Pay interests.
    interests = self.board.getInterests()
    for player in self.players:
      if player.payInterests(interests) > 0 :
        player.addCard(EmergencyLoanCard(2, _confidenceLossPerEmergencyLoan))
        self.board.advanceConfidenceMarker(_confidenceLossPerEmergencyLoan)

    # Change player order
    newOrderIdents = self.board.getNewPlayerOrder(self.players)
    self.players = self.identsToPlayers(newOrderIdents)

    # Log actions of turn.
    self.actionsOfGame.append({
      'turnIndex': self.turnIndex,
      'turnActions': self.actionsOfTurn
    })
    # Calculate statistics before we reset everything.
# TODO: Reenable statistics
#    self.appendStatistics()
    # Reset and increment constants.
    self.actionsOfTurn = []
    self.turnIndex += 1
    self.roundIndex = 0


  def advanceOnFirmTrack(self, player, firm, count):
    orderBefore = self.board.playerOrderOnFirmTrack(firm)
    leaderBefore = None if not orderBefore else orderBefore[0]
    self.board.advancePlayerOnFirmTrack(player, firm, count)
    leaderAfter = self.board.playerOrderOnFirmTrack(firm)[0]
    if leaderBefore != leaderAfter:
      if leaderAfter != player.ident:
        raise RuntimeError('The new leader is not the advancing player.')
      bonusCard = self.board.bonusCardForFirm[firm]
      if leaderBefore is not None:
        otherPlayer = self.identsToPlayers([leaderBefore])[0]
        otherPlayer.removeBonusCard(bonusCard)
      player.addBonusCard(bonusCard)

  def actionGetCard(self, player, cardIndex):
    card = self.board.getCardByIndex(cardIndex)
    goods = self.board.goodsOfCardByIndex(cardIndex)
    self.board.removeCardByIndex(cardIndex)
    player.addCard(card)
    if goods:
      self.advanceOnFirmTrack(player, resources.mainFirm(goods), 1)
    if card.type == CardTypes.Loan:
      self.board.advanceConfidenceMarker(_confidenceLossPerLoan)
      player.amount += card.value
    self.actionsOfRound.append({
        'action': 'getCard',
        'player': player.ident,
        'card': card,
        'advanceOnGoods': goods
      })

  def actionGetMoneyOnGoods(self, player, goods):
    if goods not in Goods:
      raise RuntimeError('Getting money on something that\'s not a goods.')
    given = -(-self.board.revenues[goods] / 2)  # Trick to get ceil.
    player.amount += given
    self.board.revenues[goods] -= given
    self.advanceOnFirmTrack(player, resources.mainFirm(goods), 1)
    self.actionsOfRound.append({
        'action': 'getMoneyOnGoods',
        'player': player.ident,
        'goods': goods,
        'amount': given
      })

  def actionInvest(self, player, circleIndex, firms):
    counts = self.board.investmentActionCircles[circleIndex]['counts']
    if len(counts) != len(firms):
      raise RuntimeError('Action invest specified ' + str(len(firms)) +
          ' firms, but the circle involves ' + str(len(counts)) + ' firms.')
    self.board.putPlayerOnInvestmentCircle(player, circleIndex)
    for firm, count in zip(firms, counts):
      self.advanceOnFirmTrack(player, firm, count)
    self.actionsOfRound.append({
        'action': 'invest',
        'player': player.ident,
        'firms': firms,
        'counts': counts
      })

  def actionBuild(self, player, firm):
    self.board.buildForFirm(player, firm)
    self.actionsOfRound.append({
        'action': 'build',
        'player': player.ident,
        'firm': firm
      })

  def actionSellShare(self, player, card):
    if card.name != 'share':
      raise RuntimeError('Trying to sell not a share card ' + cardToJson(card))
    if card not in player.cards:
      raise RuntimeError('Trying to sell a card the player doesn\'t hold '
          + cardToJson(card))
    shareValue = self.board.getShareValue(card.firm)
    player.amount += card.multiplicity * shareValue
    player.cards.remove(card)
    self.board.advanceConfidenceMarker(_confidenceLossPerSale)
    self.actionsOfRound.append({
        'action': 'sellShare',
        'player': player.ident,
        'card': card,
        'shareValue': shareValue
      })

  def actionPayLoan(self, player, card):
    if card.name != 'loan':
      raise RuntimeError('Trying to pay not a loan card ' + cardToJson(card))
    if card not in player.cards:
      raise RuntimeError('Trying to pay a loan the player doesn\'t hold '
          + cardToJson(card))
    if player.amount < card.value:
      raise RuntimeError('Not enough money (' + str(player.amount) + ') ' +
          'to pay back loan: ' + cardToJson(card))
    player.amount -= card.value
    player.cards.remove(card)

class BoardControllerTests(unittest.TestCase):
  def testInitialSetup(self):
    gc = GameController(Board())
    self.assertEqual(0, gc.turnIndex)
    self.assertEqual(0, gc.roundIndex)
    self.assertEqual([0, 1, 2, 3], [player.ident for player in gc.players])

  def testPrepareTurn(self):
    gc = GameController(Board())
    gc.turnIndex = 0
    gc.prepareTurn()
    self.assertEqual([3] * 4, [player.numActions for player in gc.players])
    gc.turnIndex = 1
    gc.prepareTurn()
    self.assertEqual([3] * 4, [player.numActions for player in gc.players])
    gc.turnIndex = 2
    gc.prepareTurn()
    self.assertEqual([4] * 4, [player.numActions for player in gc.players])
    gc.turnIndex = 3
    gc.prepareTurn()
    self.assertEqual([4] * 4, [player.numActions for player in gc.players])
    gc.turnIndex = 4
    gc.prepareTurn()
    self.assertEqual([5] * 4, [player.numActions for player in gc.players])
    gc.turnIndex = 5
    gc.prepareTurn()
    self.assertEqual([5] * 4, [player.numActions for player in gc.players])

  def testAdvanceOnFirmTrack(self):
    b = Board()
    gc = GameController(b)
    p0, p1, p2, p3 = gc.players
    gc.advanceOnFirmTrack(p0, Resources.Red, 2)
    gc.advanceOnFirmTrack(p2, Resources.Red, 5)
    gc.advanceOnFirmTrack(p3, Resources.Red, 5)
    bonusCard = b.bonusCardForFirm[Resources.Red]
    self.assertIn(bonusCard, p2.bonusCards)
    self.assertNotIn(bonusCard, p0.bonusCards)
    self.assertNotIn(bonusCard, p3.bonusCards)
    gc.advanceOnFirmTrack(p0, Resources.Green, 1)
    gc.advanceOnFirmTrack(p1, Resources.Green, 1)
    gc.advanceOnFirmTrack(p2, Resources.Green, 1)
    gc.advanceOnFirmTrack(p3, Resources.Green, 1)
    bonusCard = b.bonusCardForFirm[Resources.Green]
    self.assertIn(bonusCard, p0.bonusCards)
    self.assertNotIn(bonusCard, p1.bonusCards)
    self.assertNotIn(bonusCard, p2.bonusCards)
    self.assertNotIn(bonusCard, p3.bonusCards)
    gc.advanceOnFirmTrack(p0, Resources.Blue, 1)
    gc.advanceOnFirmTrack(p1, Resources.Blue, 2)
    gc.advanceOnFirmTrack(p2, Resources.Blue, 3)
    gc.advanceOnFirmTrack(p3, Resources.Blue, 4)
    bonusCard = b.bonusCardForFirm[Resources.Blue]
    self.assertIn(bonusCard, p3.bonusCards)
    self.assertNotIn(bonusCard, p0.bonusCards)
    self.assertNotIn(bonusCard, p1.bonusCards)
    self.assertNotIn(bonusCard, p2.bonusCards)

  def testFinalizeTurn(self):
    b = Board()
    gc = GameController(b)
    gc.prepareTurn()
    # Setup the game controller at the end of a turn.
    gc.roundIndex = 5
    gc.turnIndex = 2
    # Doctor the board a little.
    # Set the roof stack to be used for the future building
    b.revenues = {
      Resources.Red: 50,
      Resources.Green: 13,  # Triggered. (3 takers) 13->6->3->1
      Resources.Blue: 23,   # Triggered. (4 takers) 23->11->5->2->1
      Resources.Iron: 75,
      Resources.Brick: 44,
      Resources.Glass: 5
    }
    b.buildingColumn[Resources.Red].setRoof(RoofCard(4, 4))
    b.buildingColumn[Resources.Green].setRoof(RoofCard(2, 1))
    b.buildingColumn[Resources.Blue].setRoof(FinalRoofCard(5))

    b.advanceConfidenceMarker(14)  # Go to interests = 2$
    confidenceMarkerBefore = b.confidenceMarker

    p0, p1, p2, p3 = gc.players

    gc.advanceOnFirmTrack(p0, Resources.Red, 3)
    gc.advanceOnFirmTrack(p2, Resources.Red, 3)
    gc.advanceOnFirmTrack(p1, Resources.Red, 4)

    gc.advanceOnFirmTrack(p0, Resources.Green, 7)   # p0 gets 7
    gc.advanceOnFirmTrack(p1, Resources.Green, 7)   # p1 gets 3
    gc.advanceOnFirmTrack(p3, Resources.Green, 1)   # p3 gets 2

    gc.advanceOnFirmTrack(p1, Resources.Blue, 6)    # p1 gets 12
    gc.advanceOnFirmTrack(p2, Resources.Blue, 1)    # p2 gets 3
    gc.advanceOnFirmTrack(p3, Resources.Blue, 1)    # p3 gets 6
    gc.advanceOnFirmTrack(p3, Resources.Blue, 1)
    gc.advanceOnFirmTrack(p0, Resources.Blue, 1)    # p0 gets 1

    b.putPlayerOnInvestmentCircle(p0, 3)
    b.putPlayerOnInvestmentCircle(p1, 0)
    b.putPlayerOnInvestmentCircle(p2, 1)
    # New order will be: p1, p2, p0, p3

    # p0 has BonusWorkforceCard
    p0.amount = 1
    p0.addCard(EquipmentCard(0, 1))                 # Pay: 0+1        Due: 1*2
    p0.addCard(WorkforceCard(1, 1))                 # Pay: 0+1+1+1    Due: 1*2
    p0.addCard(WorkforceCard(1, 3))                 # Pay: 0+1+1+1    Due: 3*2
    p0.addCard(PlusLevelCard(1, 2))                 # Pay: 0          Due: 2*2
    p0.addCard(FactoryCard(Resources.Glass, 0, 1))  # Pay: 0+1 glass  Due: 1*2

    # p1 has BonusEquipmentCard and BonusFactoryCard
    p1.amount = 40
    p1.setLevelCard(LevelCard(3))
    p1.addCard(EquipmentCard(1, 2))                 # Pay: 3+1+1      Due: 2*2
    p1.addCard(FactoryCard(Resources.Iron, 1, 3))   # Pay: 3+1+1 iron Due: 3*2
    p1.addCard(LoanCard(12, 2, 2))                  # Pay: 0          Due: 2*2
    p1.addCard(MoneyForLevelCard(3, 5, 1))          # Pay: 5          Due: 1*2
    p1.addCard(MoneyForLevelCard(4, 10, 1))         # Pay: 0          Due: 1*2

    # p2 has no bonus card
    p2.amount = 0
    p2.setLevelCard(LevelCard(2))
    p2.addCard(FactoryCard(Resources.Brick, 1, 3))  # Pay: 2+1 brick  Due: 3*2
    p2.addCard(WorkforceCard(2, 1))                 # Pay: 2+2        Due: 1*2

    # p3 has no bonus card
    p3.amount = 0
    p3.setLevelCard(LevelCard(4))

    gc.finalizeTurn();

    # Check that everything is reset or advanced as expected.
    self.assertEqual(0, gc.roundIndex)
    self.assertEqual(3, gc.turnIndex)

    # Check revenue areas.
    self.assertEqual(50, b.revenues[Resources.Red])
    self.assertEqual(1, b.revenues[Resources.Green])
    self.assertEqual(1, b.revenues[Resources.Blue])
    self.assertEqual(75, b.revenues[Resources.Iron])
    self.assertEqual(44, b.revenues[Resources.Brick])
    self.assertEqual(5, b.revenues[Resources.Glass])

    # Check players
    self.assertEqual(0, p0.amount)
    self.assertNotIn(EmergencyLoanCard(2, 3), p0.cards)
    self.assertEqual(
        { Resources.Iron: 0, Resources.Brick: 0, Resources.Glass: 1 },
        p0.getResources())

    self.assertEqual(47, p1.amount)
    self.assertNotIn(EmergencyLoanCard(2, 3), p1.cards)
    self.assertEqual(
        { Resources.Iron: 5, Resources.Brick: 0, Resources.Glass: 0 },
        p1.getResources())

    self.assertEqual(0, p2.amount)
    self.assertIn(EmergencyLoanCard(2, 3), p2.cards)
    self.assertEqual(
        { Resources.Iron: 0, Resources.Brick: 3, Resources.Glass: 0 },
        p2.getResources())

    self.assertEqual(8, p3.amount)
    self.assertNotIn(EmergencyLoanCard(2, 3), p3.cards)
    self.assertEqual(
        { Resources.Iron: 0, Resources.Brick: 0, Resources.Glass: 0 },
        p3.getResources())

    # Check order
    self.assertEqual([1, 2, 0, 3], [p.ident for p in gc.players])

    # Check confidence marker (advanced because of emergency loan)
    self.assertEqual(confidenceMarkerBefore - _confidenceLossPerEmergencyLoan,
        b.confidenceMarker)

  def testIdentToPlayer(self):
    b = Board()
    gc = GameController(b)
    expected = [gc.players[i] for i in [3, 0, 2, 1]]
    shuffle(gc.players)
    players = gc.identsToPlayers([3, 0, 2, 1])
    self.assertEqual(expected, players)
    self.assertEqual([], gc.identsToPlayers([]))

  def testActionGetCard(self):
    b = Board()
    gc = GameController(b)
    confidenceMarkerBefore = b.confidenceMarker
    # Doctor the board a little.
    for player in gc.players:
      player.amount = 0
    b.cardStack = [
      FactoryCard(Resources.Glass, 0, 1),
      WorkforceCard(0, 1),
      PlusLevelCard(1, 2),
      GoodsCard(Resources.Iron, 3, 0),
      MoneyForLevelCard(3, 3, 0),
      WorkforceCard(0, 1),
      ActionCard(),
      UpgradeCard(2),
      LoanCard(10, 1, 2),
      LoanCard(8, 1, 2),
      GoodsCard(Resources.Brick, 4, 0)]
    b.prepareTurn()

    p0, p1, p2, p3 = gc.players

    gc.actionGetCard(p0, 2)  # Advances p0 on blue firm track.
    self.assertIn(PlusLevelCard(1,2), p0.cards)
    self.assertEqual([], b.playerOrderOnFirmTrack(Resources.Red))
    self.assertEqual([], b.playerOrderOnFirmTrack(Resources.Green))
    self.assertEqual([0], b.playerOrderOnFirmTrack(Resources.Blue))

    gc.actionGetCard(p1, 2)  # Does not advance on any track.
    self.assertIn(GoodsCard(Resources.Iron, 3, 0), p1.cards)
    self.assertEqual([], b.playerOrderOnFirmTrack(Resources.Red))
    self.assertEqual([], b.playerOrderOnFirmTrack(Resources.Green))
    self.assertEqual([0], b.playerOrderOnFirmTrack(Resources.Blue))

    gc.actionGetCard(p2, 0) # Advances p2 on red firm track.
    self.assertIn(FactoryCard(Resources.Glass, 0, 1), p2.cards)
    self.assertEqual([2], b.playerOrderOnFirmTrack(Resources.Red))
    self.assertEqual([], b.playerOrderOnFirmTrack(Resources.Green))
    self.assertEqual([0], b.playerOrderOnFirmTrack(Resources.Blue))

    self.assertEqual(confidenceMarkerBefore, b.confidenceMarker)
    gc.actionGetCard(p3, 5) # Does not advance on any track.
    self.assertIn(LoanCard(10, 1, 2), p3.cards)
    self.assertEqual([2], b.playerOrderOnFirmTrack(Resources.Red))
    self.assertEqual([], b.playerOrderOnFirmTrack(Resources.Green))
    self.assertEqual([0], b.playerOrderOnFirmTrack(Resources.Blue))
    self.assertEqual(confidenceMarkerBefore - _confidenceLossPerLoan,
        b.confidenceMarker)

  def testActionGetMoneyOnGoods(self):
    b = Board()
    gc = GameController(b)
    # Doctor the board a little.
    for player in gc.players:
      player.amount = 0
    b.revenues[Resources.Glass] = 13

    p0, p1, p2, p3 = gc.players

    gc.actionGetMoneyOnGoods(p1, Resources.Glass)
    self.assertEqual(7, p1.amount)
    self.assertEqual(6, b.revenues[Resources.Glass])
    self.assertEqual([], b.playerOrderOnFirmTrack(Resources.Red))
    self.assertEqual([], b.playerOrderOnFirmTrack(Resources.Green))
    self.assertEqual([1], b.playerOrderOnFirmTrack(Resources.Blue))

  def testActionInvest(self):
    b = Board()
    gc = GameController(b)

    p0, p1, p2, p3 = gc.players

    gc.actionInvest(p0, 0, [Resources.Red, Resources.Blue])   # p0: +1 R, +1 B
    with self.assertRaises(RuntimeError):
      gc.actionInvest(p1, 0, [Resources.Red, Resources.Blue])
    gc.actionInvest(p2, 1, [Resources.Green])                 # p2: +2 G
    with self.assertRaises(RuntimeError):
      gc.actionInvest(p2, 2, [Resources.Red, Resources.Blue])
    gc.actionInvest(p0, 2, [Resources.Red])                   # p0: +3 R
    with self.assertRaises(RuntimeError):
      gc.actionInvest(p2, 3, [Resources.Green])
    gc.actionInvest(p3, 3, [Resources.Red, Resources.Blue])   # p3: +2 R, +2 B
    gc.actionInvest(p2, 4, [Resources.Red])                   # p2: +4 R
    self.assertEqual([[], [3], [], [0, 2]], b.firmTracks[Resources.Red][:4])
    self.assertEqual([[], [2], [], []], b.firmTracks[Resources.Green][:4])
    self.assertEqual([[0], [3], [], []], b.firmTracks[Resources.Blue][:4])

    gc.finalizeTurn()
    # Check order
    self.assertEqual([0, 2, 3, 1], [p.ident for p in gc.players])

  def testActionBuild(self):
    b = Board()
    gc = GameController(b)

    p0, p1, p2, p3 = gc.players
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

    p2.amount = 20
    gc.actionBuild(p2, Resources.Red)

    self.assertEqual(0, p2.amount)
    self.assertEqual(4, p2.getLevel())
    self.assertIn(ShareCard(Resources.Red, 3), p2.cards)
    self.assertEqual(10, b.revenues[Resources.Red])
    self.assertEqual(5, b.revenues[Resources.Glass])
    self.assertEqual(3, b.shareScore[Resources.Red])
    self.assertEqual(5, column.length())
    self.assertEqual(6, column.getLevel())

  def testActionSellShare(self):
    b = Board()
    gc = GameController(b)

    # Doctor the board
    b.advanceShareScore(Resources.Green, 18)  # Share value = 5$

    confidenceMarkerBefore = b.confidenceMarker
    p0, p1, p2, p3 = gc.players
    p0.amount = 0
    p0.addCard(ShareCard(Resources.Green, 3))
    p0.addCard(ActionCard())
    gc.actionSellShare(p0, ShareCard(Resources.Green, 3))  # 3 * 5$

    self.assertEqual(15, p0.amount)
    self.assertNotIn(ShareCard(Resources.Green, 3), p0.cards)
    self.assertEqual(confidenceMarkerBefore - _confidenceLossPerSale,
        b.confidenceMarker)

    with self.assertRaises(RuntimeError):
      gc.actionSellShare(p0, ShareCard(Resources.Green, 3))

    with self.assertRaises(RuntimeError):
      gc.actionSellShare(p0, ActionCard())

  def testActionPayLoan(self):
    b = Board()
    gc = GameController(b)

    p0, p1, p2, p3 = gc.players
    p2.amount = 10
    p2.addCard(LoanCard(8, 2, 2))
    p2.addCard(LoanCard(6, 1, 2))
    gc.actionPayLoan(p2, LoanCard(8, 2, 2))

    self.assertEqual(2, p2.amount)
    self.assertNotIn(LoanCard(8, 2, 2), p2.cards)

    with self.assertRaises(RuntimeError):
      gc.actionPayLoan(p2, LoanCard(6, 1, 2))

    p2.amount = 6
    gc.actionPayLoan(p2, LoanCard(6, 1, 2))
    self.assertEqual(0, p2.amount)
    self.assertNotIn(LoanCard(6, 1, 2), p2.cards)

    with self.assertRaises(RuntimeError):
      gc.actionPayLoan(p0, LoanCard(6, 1, 2))

    with self.assertRaises(RuntimeError):
      gc.actionPayLoan(p0, EmergencyLoanCard(1, 2))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
