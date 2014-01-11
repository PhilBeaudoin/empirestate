import json
from resources import Resources
from cardtypes import CardTypes

def _cardToDict(card):
  d = card.__dict__.copy()
  resourceFields = ['firm', 'resource'];
  for resourceField in resourceFields:
    try: d[resourceField] = Resources.reverse_mapping[d[resourceField]]
    except: pass
  return d

def cardToJson(card):
  return json.dumps(card, default=_cardToDict)

class Card:
  def __eq__(self, other):
    return self.__dict__ == other.__dict__
  def __ne__(self, other):
    return self.__dict__ != other.__dict__
  def __repr__(self):
    return str(self.__dict__)

class BuildingCard(Card):
  def __init__(self, level, firm, resource):
    self.level = level
    self.firm = firm
    self.resource = resource
    self.name = 'building'
    self.type = CardTypes.Building
  def flip(self):
    return ShareCard(self.firm, -(-self.level/2))  # To do "ceil"

class RoofCard(Card):
  def __init__(self, cardCount, progress, regress):
    self.cardCount = cardCount
    self.progress = progress
    self.regress = regress
    self.name = 'roof'
    self.type = CardTypes.Roof
  def flip(self):
    return LevelCard(self.cardCount)

class FinalRoofCard(Card):
  def __init__(self, progress, regress):
    self.progress = progress
    self.regress = regress
    self.name = 'finalRoof'
    self.type = CardTypes.Roof

class LevelCard(Card):
  def __init__(self, level):
    self.level = level
    self.name = 'level'
    self.type = CardTypes.Level

class ConfidenceDecreaseCard(Card):
  def __init__(self):
    self.name = 'confidenceDecrease'
    self.type = CardTypes.ConfidenceDecrease

class ShareCard(Card):
  def __init__(self, firm, multiplicity):
    self.firm = firm
    self.multiplicity = multiplicity
    self.regress = 0
    self.upkeep = 0
    self.finalPayoff = 0
    self.name = 'share'
    self.type = CardTypes.Upgrade
  def payoff(self, level, bonusCards):
    return 0

def _extraFrom(name, bonusCards):
  extra = 0
  for card in bonusCards:
    if card.name == name:
      extra += card.bonus
  return extra

class FactoryCard(Card):
  def __init__(self, resource, bonus, upkeep, finalPayoff, amount = 0):
    self.resource = resource
    self.bonus = bonus
    self.regress = 0
    self.upkeep = upkeep
    self.finalPayoff = finalPayoff
    self.amount = amount
    self.name = 'factory'
    self.type = CardTypes.Upgrade
  def payoff(self, level, bonusCards):
    self.amount += level + self.bonus + _extraFrom('bonusFactory', bonusCards)
    return 0

class WorkforceCard(Card):
  def __init__(self, bonus, upkeep, finalPayoff):
    self.bonus = bonus
    self.regress = 0
    self.upkeep = upkeep
    self.finalPayoff = finalPayoff
    self.name = 'workforce'
    self.type = CardTypes.Upgrade
  def payoff(self, level, bonusCards):
    return level + self.bonus + _extraFrom('bonusWorkforce', bonusCards)

class EquipmentCard(Card):
  def __init__(self, bonus, upkeep, finalPayoff):
    self.bonus = bonus
    self.regress = 0
    self.upkeep = upkeep
    self.finalPayoff = finalPayoff
    self.name = 'equipment'
    self.type = CardTypes.Upgrade
  def payoff(self, level, bonusCards):
    return level + self.bonus + _extraFrom('bonusEquipment', bonusCards)

class PlusLevelCard(Card):
  def __init__(self, plusLevel, upkeep, finalPayoff):
    self.plusLevel = plusLevel
    self.regress = 0
    self.upkeep = upkeep
    self.finalPayoff = finalPayoff
    self.name = 'plusLevel'
    self.type = CardTypes.Upgrade
  def payoff(self, level, bonusCards):
    return 0

class LoanGoodsCard(Card):
  def __init__(self, resource, amount, upkeep, finalPayoff):
    self.resource = resource
    self.amount = amount
    self.regress = 1
    self.upkeep = upkeep
    self.finalPayoff = finalPayoff
    self.name = 'loanGoods'
    self.type = CardTypes.Loan
  def payoff(self, level, bonusCards):
    return 0

class LoanCard(Card):
  def __init__(self, amount, upkeep, finalPayoff):
    self.amount = amount
    self.regress = 1
    self.upkeep = upkeep
    self.finalPayoff = finalPayoff
    self.name = 'loan'
    self.type = CardTypes.Loan
  def payoff(self, level, bonusCards):
    return 0

class EmergencyLoanCard(Card):
  def __init__(self, upkeep, finalPayoff):
    self.amount = 0
    self.regress = 1
    self.upkeep = upkeep
    self.finalPayoff = finalPayoff
    self.name = 'emergencyLoan'
    self.type = CardTypes.Loan
  def payoff(self, level, bonusCards):
    return 0

class MoneyForLevelCard(Card):
  def __init__(self, minLevel, bonus, upkeep, finalPayoff):
    self.minLevel = minLevel
    self.bonus = bonus
    self.regress = 0
    self.upkeep = upkeep
    self.finalPayoff = finalPayoff
    self.name = 'moneyForLevel'
    self.type = CardTypes.Upgrade
  def payoff(self, level, bonusCards):
    return self.bonus if level >= self.minLevel else 0

class FinalMoneyCard(Card):
  def __init__(self, upkeep, finalPayoff):
    self.regress = 0
    self.upkeep = upkeep
    self.finalPayoff = finalPayoff
    self.name = 'finalMoney'
    self.type = CardTypes.Upgrade
  def payoff(self, level, bonusCards):
    return 0

class UpgradeCard(Card):
  def __init__(self, upkeep):
    self.regress = 0
    self.upkeep = upkeep
    self.name = 'upgrade'
    self.type = CardTypes.Upgrade
  def payoff(self, level, bonusCards):
    return 0

class BonusTokenCard(Card):
  def __init__(self, minLevel, minRound, tokenNumber, upkeep, finalPayoff):
    self.minLevel = minLevel
    self.minLevel = minRound
    self.minLevel = tokenNumber
    self.regress = 0
    self.upkeep = upkeep
    self.finalPayoff = finalPayoff
    self.name = 'bonusToken'
    self.type = CardTypes.Action
  def payoff(self, level, bonusCards):
    return 0

class ActionCard(Card):
  def __init__(self):
    self.regress = 0
    self.upkeep = 0
    self.finalPayoff = 0
    self.name = 'action'
    self.type = CardTypes.Action
  def payoff(self, level, bonusCards):
    return 0

class BonusFactoryCard(Card):
  def __init__(self, bonus):
    self.bonus = bonus
    self.name = 'bonusFactory'
    self.type = CardTypes.Bonus

class BonusWorkforceCard(Card):
  def __init__(self, bonus):
    self.bonus = bonus
    self.name = 'bonusWorkforce'
    self.type = CardTypes.Bonus

class BonusEquipmentCard(Card):
  def __init__(self, bonus):
    self.bonus = bonus
    self.name = 'bonusEquipment'
    self.type = CardTypes.Bonus
