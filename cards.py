import json
from resources import Resources


def _cardToDict(card):
  d = card.__dict__.copy()
  resourceFields = ['column', 'resource'];
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
  def __init__(self, level, column, resource):
    self.level = level
    self.column = column
    self.resource = resource
    self.type = 'building'
  def flip(self):
    return ShareCard(1, self.column, -(-self.level/2))  # To do "ceil"

class RoofCard(Card):
  def __init__(self, level, progress = 0):
    self.level = level
    self.progress = progress if progress else level
    self.type = 'roof'

class ShareCard(Card):
  def __init__(self, level, column, multiplicity = 1):
    self.level = level
    self.column = column
    self.multiplicity = multiplicity
    self.type = 'share'
  def payoff(self, level):
    return 0

class FactoryCard(Card):
  def __init__(self, level, column, resource, amount = 0):
    self.level = level
    self.column = column
    self.resource = resource
    self.amount = amount
    self.type = 'factory'
  def payoff(self, level):
    self.amount += level
    return 0

class DividendCard(Card):
  def __init__(self, level, column, divisor = 1):
    self.level = level
    self.column = column
    self.divisor = divisor
    self.type = 'dividend'
  def payoff(self, level):
    return -((-level)/self.divisor)  # Trick to round up.

class PlusLevelCard(Card):
  def __init__(self, level, column, plusLevel = 1):
    self.level = level
    self.column = column
    self.plusLevel = plusLevel
    self.type = 'plusLevel'
  def payoff(self, level):
    return 0

class UpgradeCard(Card):
  def __init__(self, level, column):
    self.level = level
    self.column = column
    self.type = 'upgrade'
  def payoff(self, level):
    return 0


