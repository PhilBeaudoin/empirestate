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
      for j in xrange(5):
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
        'size': self.board.buildingStack[firm].cardColumn.length(),
        'level': self.board.buildingStack[firm].cardColumn.getLevel()
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
      'shareValues': dict(self.board.shareValue),
      'buildingsComplete':
          sum([0 if self.board.buildingStack[f].roof else 1 for f in Firms]),
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

  def takeAction(self, player):
    if self.tryBuild(player):
      return
    if self.tryUpgrade(player):
      return
    if self.tryInvestment(player):
      return
    if self.tryGetRevenues(player):
      return
    if self.tryBank(player):
      return
    self.actionsOfRound.append({
      'action': 'other',
      'player': player.initialIndex
    })

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
    player.addCard(card)
    if goods:
      self.advanceOnFirmTrack(player, firm, resources.mainFirm(goods), 1)
    if card.type == CardTypes.Loan:
      self.board.advanceConfidenceMarker(_confidenceLossPerLoan)
      player.amount += card.value

  def actionGetCard(self, player, cardIndex):
    card = self.board.getCardByIndex(cardIndex)
    goods = self.board.goodsOfCardByIndex(cardIndex)
    player.addCard(card)
    if goods:
      self.advanceOnFirmTrack(player, firm, resources.mainFirm(goods), 1)
    if card.type == CardTypes.Loan:
      self.board.advanceConfidenceMarker(_confidenceLossPerLoan)
      player.amount += card.value

  def expectedRevenueFromFirms(self):
    return sum([self.board.revenues[i] for i in Firms]) / 6

  def tryBank(self, player):
    if (self.board.bank and
        self.board.bank[-1] >= self.expectedRevenueFromFirms()):
      amount = self.board.bank.pop()
      player.amount += amount
      self.actionsOfRound.append({
        'action': 'bank',
        'player': player.initialIndex,
        'amount': amount
      })
      return True
    return False

  def tryUpgrade(self, player):
    if self.board.upgrades:
      card = self.board.upgrades.pop()
      player.addCard(card)
      self.actionsOfRound.append({
        'action': 'upgrade',
        'player': player.initialIndex,
        'card': copy.copy(card)
      })
      return True
    return False

  def tryInvestment(self, player):
    if self.board.investments:
      card = self.board.investments.pop()
      player.addCard(card)
      self.actionsOfRound.append({
        'action': 'investment',
        'player': player.initialIndex,
        'card': copy.copy(card)
      })
      return True
    return False

  def tryGetRevenues(self, player):
    threshold = self.expectedRevenueFromFirms()
    if self.board.bank:
      threshold = max(threshold, self.board.bank[-1])
    for i in Goods:
      if (self.board.revenues[i] - (self.board.revenues[i] / 2) >= threshold):
        amountLeft = self.board.revenues[i] / 2
        amount = self.board.revenues[i] - amountLeft
        player.amount += amount
        self.board.revenues[i] = amountLeft
        self.actionsOfRound.append({
          'action': 'revenue',
          'player': player.initialIndex,
          'amount': amount
        })
        return True
    return False

  def tryBuild(self, player):
    for firm in Firms:
      buildingStack = self.board.buildingStack[firm]
      if player.canPayForBuilding(buildingStack):
        player.payForBuilding(buildingStack)
        level = buildingStack.cardColumn.getLevel()
        amount = level * buildingStack.cardColumn.length()
        amountSink = 0
        for i in xrange(buildingStack.cardColumn.length()):
          resource = buildingStack.cardColumn.getCard(i).resource
          if resource != Resources.Bank:
            self.board.revenues[resource] += level
          else:
            amountSink += level
        self.board.shareValue[firm] += \
            buildingStack.roof.progress if buildingStack.roof else 10
        player.addCard(buildingStack.cardColumn.popLargest().flip())
        player.addCard(ShareCard(buildingStack.roof.level - 1, firm))
        if self.board.roofStack:
          buildingStack.setRoof(self.board.roofStack.pop())
        else:
          buildingStack.clear()
        self.actionsOfRound.append({
          'action': 'build',
          'player': player.initialIndex,
          'firm': firm,
          'amount': amount,
          'amountSink': amountSink
        })
        return True
    return False


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

  # def testBankAction(self):
  #   b = Board()
  #   gc = GameController(b)
  #   gc.prepareTurn()
  #   for player in gc.players:
  #     player.amount = 0
  #   # Doctor the board.
  #   b.bank = [2, 4, 6]
  #   for i in Firms:
  #     b.revenues[i] = 10  # Expect 5 from a "no action"
  #   self.assertTrue(gc.tryBank(gc.players[0]))
  #   self.assertFalse(gc.tryBank(gc.players[1]))  # Prefers the expected 5.
  #   for i in Firms:
  #     b.revenues[i] = 0  # Expect 0 from a "no action"
  #   self.assertTrue(gc.tryBank(gc.players[1]))
  #   self.assertTrue(gc.tryBank(gc.players[2]))
  #   self.assertFalse(gc.tryBank(gc.players[3]))
  #   self.assertEqual(6, gc.players[0].amount)
  #   self.assertEqual(4, gc.players[1].amount)
  #   self.assertEqual(2, gc.players[2].amount)
  #   self.assertEqual([
  #     {'action': 'bank', 'player': 0, 'amount': 6},
  #     {'action': 'bank', 'player': 1, 'amount': 4},
  #     {'action': 'bank', 'player': 2, 'amount': 2}
  #   ], gc.actionsOfRound)


  # def testGetRevenuesAction(self):
  #   b = Board()
  #   gc = GameController(b)
  #   for player in gc.players:
  #     player.amount = 0
  #   gc.prepareTurn()
  #   # Doctor the board.
  #   b.bank = [2, 4, 6]
  #   for i in Firms:
  #     b.revenues[i] = 20  # Expect 10 from a "no action"
  #   b.revenues[Resources.Glass] = 11
  #   b.revenues[Resources.Iron] = 10
  #   b.revenues[Resources.Brick] = 9
  #   self.assertFalse(gc.tryGetRevenues(gc.players[0]))
  #   for i in Firms:
  #     b.revenues[i] = 0  # Expect 6 from a "no action" (the bank)
  #   self.assertTrue(gc.tryGetRevenues(gc.players[0]))
  #   self.assertEqual(6, gc.players[0].amount)
  #   self.assertEqual(5, b.revenues[Resources.Glass])
  #   self.assertFalse(gc.tryGetRevenues(gc.players[1]))  # Prefers 6 from bank.
  #   b.bank = [2, 4]
  #   self.assertTrue(gc.tryGetRevenues(gc.players[1]))
  #   self.assertEqual(5, gc.players[1].amount)
  #   self.assertEqual(5, b.revenues[Resources.Iron])
  #   self.assertTrue(gc.tryGetRevenues(gc.players[2]))
  #   self.assertEqual(5, gc.players[2].amount)
  #   self.assertEqual(4, b.revenues[Resources.Brick])

  # def testUpgrade(self):
  #   b = Board()
  #   gc = GameController(b)
  #   gc.prepareTurn()
  #   for player in gc.players:
  #     player.amount = 0
  #   # Doctor the board a little.
  #   b.upgrades = [
  #     PlusLevelCard(2, Resources.Red),
  #     UpgradeCard(3, Resources.Red),
  #     UpgradeCard(1, Resources.Blue)
  #   ]
  #   self.assertTrue(gc.tryUpgrade(gc.players[0]))
  #   self.assertTrue(gc.tryUpgrade(gc.players[0]))
  #   self.assertTrue(gc.tryUpgrade(gc.players[0]))
  #   self.assertFalse(gc.tryUpgrade(gc.players[0]))
  #   self.assertEqual(4, gc.players[0].columns[Resources.Red].getLevel())
  #   self.assertEqual(1, gc.players[0].columns[Resources.Blue].getLevel())
  #   self.assertEqual([
  #     {'action': 'upgrade',
  #      'player': 0,
  #      'card': UpgradeCard(1, Resources.Blue)},
  #     {'action': 'upgrade',
  #      'player': 0,
  #      'card': UpgradeCard(3, Resources.Red)},
  #     {'action': 'upgrade',
  #      'player': 0,
  #      'card': PlusLevelCard(2, Resources.Red)}
  #   ], gc.actionsOfRound)

  # def testUpgrade(self):
  #   b = Board()
  #   gc = GameController(b)
  #   for player in gc.players:
  #     player.amount = 0
  #   gc.prepareTurn()
  #   # Doctor the board a little.
  #   b.investments = [
  #     EquipmentCard(1, Resources.Red, Resources.Glass),
  #     ShareCard(2, Resources.Green),
  #     DividendCard(4, Resources.Green)
  #   ]
  #   self.assertTrue(gc.tryInvestment(gc.players[0]))
  #   self.assertTrue(gc.tryInvestment(gc.players[0]))
  #   self.assertTrue(gc.tryInvestment(gc.players[1]))
  #   self.assertFalse(gc.tryInvestment(gc.players[2]))
  #   self.assertEqual(1, gc.players[1].columns[Resources.Red].getLevel())
  #   self.assertEqual(4, gc.players[0].columns[Resources.Green].getLevel())
  #   self.assertEqual([
  #     {'action': 'investment',
  #      'player': 0,
  #      'card': DividendCard(4, Resources.Green)},
  #     {'action': 'investment',
  #      'player': 0,
  #      'card': ShareCard(2, Resources.Green)},
  #     {'action': 'investment',
  #      'player': 1,
  #      'card': EquipmentCard(1, Resources.Red, Resources.Glass)}
  #   ], gc.actionsOfRound)

  # def testBuild(self):
  #   b = Board()
  #   gc = GameController(b)
  #   for player in gc.players:
  #     player.amount = 0
  #   gc.prepareTurn()
  #   # Doctor the board a little.
  #   # Set the roof stack to be used for the future building
  #   b.roofStack = [ RoofCard(2), RoofCard(4) ]
  #   firm = Resources.Red
  #   b.buildingStack[firm] = BuildingColumn(firm, [
  #     BuildingCard(20, firm, Resources.Bank),
  #     BuildingCard(20, firm, Resources.Bank),
  #     BuildingCard(6, firm, Resources.Bank),  # Third building
  #     BuildingCard(5, firm, Resources.Bank),  # Third building
  #     BuildingCard(2, firm, Resources.Iron),  # First/Third building
  #     BuildingCard(3, firm, Resources.Red),   # First/Third building
  #     BuildingCard(4, firm, Resources.Glass)  # First building
  #   ])
  #   b.buildingStack[firm].setRoof(RoofCard(3))
  #   firm = Resources.Green
  #   b.buildingStack[firm] = BuildingColumn(firm, [
  #     BuildingCard(20, firm, Resources.Bank),
  #     BuildingCard(2, firm, Resources.Glass),  # Second building
  #     BuildingCard(7, firm, Resources.Glass)  # Second building
  #   ])
  #   b.buildingStack[firm].setRoof(RoofCard(2))
  #   # Have an empty building in the mix, that can never be built.
  #   firm = Resources.Blue
  #   b.buildingStack[firm] = BuildingColumn(firm, [])
  #   for resource in FirmsOrGoods:
  #     b.revenues[resource] = 0

  #   # Have player 0 try and fail and then succeed to build the first building.
  #   gc.players[0].addCard(EquipmentCard(3, Resources.Red, Resources.Glass, 6))
  #   gc.players[0].amount = 7
  #   self.assertFalse(gc.tryBuild(gc.players[0]))
  #   gc.players[0].amount = 8
  #   self.assertTrue(gc.tryBuild(gc.players[0]))

  #   # Check player 0's red column.
  #   self.assertEqual(3, gc.players[0].columns[Resources.Red].getLevel())
  #   cards = gc.players[0].columns[Resources.Red].getCards()
  #   self.assertIn(ShareCard(1, Resources.Red, 2), cards)
  #   self.assertIn(ShareCard(2, Resources.Red), cards)

  #   # Check the revenue areas.
  #   self.assertEqual(4, b.revenues[Resources.Red])
  #   self.assertEqual(4, b.revenues[Resources.Iron])
  #   self.assertEqual(4, b.revenues[Resources.Glass])
  #   for resource in FirmsOrGoods:
  #     b.revenues[resource] = 0

  #   # Check share value.
  #   self.assertEqual(3, b.shareValue[Resources.Red])

  #   # Have player 0 try and fail and then succeed to build the second building.
  #   gc.players[0].amount = 11
  #   self.assertFalse(gc.tryBuild(gc.players[0]))
  #   gc.players[0].amount = 12
  #   self.assertTrue(gc.tryBuild(gc.players[0]))

  #   # Check player 0's green column.
  #   self.assertEqual(1, gc.players[0].columns[Resources.Green].getLevel())
  #   cards = gc.players[0].columns[Resources.Green].getCards()
  #   self.assertIn(ShareCard(1, Resources.Green, 4), cards)
  #   self.assertIn(ShareCard(1, Resources.Green), cards)

  #   # Check the revenue areas.
  #   self.assertEqual(14, b.revenues[Resources.Glass])
  #   for resource in FirmsOrGoods:
  #     b.revenues[resource] = 0

  #   # Check share value.
  #   self.assertEqual(2, b.shareValue[Resources.Green])

  #   # Have player 1 build the third building.
  #   gc.players[1].amount = 23
  #   self.assertFalse(gc.tryBuild(gc.players[1]))
  #   gc.players[1].amount = 24
  #   self.assertTrue(gc.tryBuild(gc.players[1]))

  #   # Check player 1's red column.
  #   self.assertEqual(3, gc.players[1].columns[Resources.Red].getLevel())
  #   cards = gc.players[1].columns[Resources.Red].getCards()
  #   self.assertIn(ShareCard(1, Resources.Red, 3), cards)
  #   self.assertIn(ShareCard(3, Resources.Red), cards)

  #   # Check the revenue areas.
  #   self.assertEqual(6, b.revenues[Resources.Red])
  #   self.assertEqual(6, b.revenues[Resources.Iron])
  #   for resource in FirmsOrGoods:
  #     b.revenues[resource] = 0

  #   # Check that the column card is cleared (no more roof card).
  #   self.assertEqual(0, b.buildingStack[Resources.Red].cardColumn.length())
  #   self.assertIsNone(b.buildingStack[Resources.Red].roof)

  #   # Check share value. (3 + 4)
  #   self.assertEqual(7, b.shareValue[Resources.Red])

  #   self.assertEqual([
  #     {'action': 'build',
  #      'player': 0,
  #      'firm': Resources.Red,
  #      'amount': 12,
  #      'amountSink': 0},
  #     {'action': 'build',
  #      'player': 0,
  #      'firm': Resources.Green,
  #      'amount': 14,
  #      'amountSink': 0},
  #     {'action': 'build',
  #      'player': 1,
  #      'firm': Resources.Red,
  #      'amount': 24,
  #      'amountSink': 12},
  #   ], gc.actionsOfRound)

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
    b.buildingStack[Resources.Red].setRoof(RoofCard(4, 4))
    b.buildingStack[Resources.Green].setRoof(RoofCard(2, 1))
    b.buildingStack[Resources.Blue].setRoof(FinalRoofCard(5))

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

def main():
    unittest.main()

if __name__ == '__main__':
    main()
