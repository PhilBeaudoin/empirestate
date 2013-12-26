import unittest
from enum import enum

Resources = enum('Red', 'Green', 'Blue', 'Iron', 'Brick', 'Glass', 'Bank')
Firms = [Resources.Red, Resources.Green, Resources.Blue]
Goods = [Resources.Iron, Resources.Brick, Resources.Glass]
FirmsOrGoods = Firms + Goods

def isFirm(resource):
  return (resource >= 0 and resource <= 2);

def isGoods(resource):
  return (resource >= 3 and resource <= 5);

def nextFirm(firm):
  if not isFirm(firm):
    raise RuntimeError('Resource is not a firm ' +
                       Resources.reverse_mapping[firm])
  return (firm + 1) % 3;

def nextGoods(goods):
  if not isGoods(goods):
    raise RuntimeError('Resource is not a goods ' +
                       Resources.reverse_mapping[goods])
  return ((goods - 3) + 1) % 3 + 3;

def mainGoods(firm):
  if not isFirm(firm):
    raise RuntimeError('Resource is not a firm ' +
                       Resources.reverse_mapping[firm])
  return firm + 3;

class ResourceTests(unittest.TestCase):
  def testNextFirmFail(self):
    with self.assertRaises(RuntimeError):
      nextFirm(Resources.Glass);
    with self.assertRaises(RuntimeError):
      nextFirm(Resources.Bank);

  def testNextFirm(self):
    self.assertEqual(Resources.Red, nextFirm(Resources.Blue));
    self.assertEqual(Resources.Green, nextFirm(Resources.Red));
    self.assertEqual(Resources.Blue, nextFirm(Resources.Green));

  def testNextGoodsFail(self):
    with self.assertRaises(RuntimeError):
      nextGoods(Resources.Blue);
    with self.assertRaises(RuntimeError):
      nextGoods(Resources.Bank);

  def testNextFirm(self):
    self.assertEqual(Resources.Brick, nextGoods(Resources.Iron));
    self.assertEqual(Resources.Glass, nextGoods(Resources.Brick));
    self.assertEqual(Resources.Iron, nextGoods(Resources.Glass));

  def testMainGoodsFail(self):
    with self.assertRaises(RuntimeError):
      mainGoods(Resources.Iron);
    with self.assertRaises(RuntimeError):
      mainGoods(Resources.Bank);

  def testMainGoods(self):
    self.assertEqual(Resources.Glass, mainGoods(Resources.Blue));
    self.assertEqual(Resources.Iron, mainGoods(Resources.Red));
    self.assertEqual(Resources.Brick, mainGoods(Resources.Green));

def main():
    unittest.main()

if __name__ == '__main__':
    print(Resources.__repr__(1))
    main()
