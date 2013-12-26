from resources import Resources
from cards import *

class MixedCardsError:
  def __init__(self, column, card):
    self.column = column
    self.card = card
  def __str__(self):
    return "Stack or column with mixed cards. Expected " + \
           Resources.reverse_mapping[self.column] + \
           " but got " + Resources.reverse_mapping[self.card.column] + \
           " on card " + cardToJson(self.card)
