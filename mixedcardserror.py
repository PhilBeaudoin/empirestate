from resources import Resources
from cards import *

class MixedCardsError:
  def __init__(self, firm, card):
    self.firm = firm
    self.card = card
  def __str__(self):
    return "Stack or column with mixed cards. Expected " + \
           Resources.reverse_mapping[self.firm] + \
           " but got " + Resources.reverse_mapping[self.card.firm] + \
           " on card " + cardToJson(self.card)
