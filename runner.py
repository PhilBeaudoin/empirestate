from gamecontroller import GameController
from resources import Resources, Firms
from board import Board
import numpy

def printHisto(name, bins, range, stats):
  print name
  histos = [ numpy.histogram(turn, bins=bins, range=range)
             for turn in stats[name] ]
  print "  " + str([int(h) for h in histos[0][1]])
  for histo in histos:
    print "  " + str(list(histo[0]))

stats = []
actions = []
for i in xrange(100):
  gc = GameController(Board())
  gc.playGame()
  stats.append(gc.statistics)
  actions.append(gc.actionsOfGame)

actionNames = ['getCard-factory', 'getCard-workforce', 'getCard-equipment',
               'getCard-plusLevel', 'getCard-loanGoods', 'getCard-loan',
               'getCard-moneyForLevel', 'getCard-bonusToken', 'getCard-upgrade',
               'getCard-action', 'getCard-finalMoney',
               'getCard', 'getMoneyOnGoods', 'invest',
               'build', 'sellShare', 'payLoan', 'skip']
actionStats = { name: [[] for i in range(6)] for name in actionNames }
for game in actions:
  for turn in game:
    turnIndex = turn['turnIndex']
    turnStats = { name: 0 for name in actionNames }
    for turnAction in turn['turnActions']:
      for action in turnAction['roundActions']:
        name = action['action']
        turnStats[name] += 1
        if name == 'getCard':
          name += '-' + action['card'].name
          turnStats[name] += 1
    for name in actionNames:
      actionStats[name][turnIndex].append(turnStats[name])

statsData = [
  { 'name': 'amountPerPlayer', 'bins': 10, 'range': (0, 100) },
  { 'name': 'levelPerPlayer', 'bins': 10, 'range': (0, 10) },
  { 'name': 'incomePerPlayer', 'bins': 20, 'range': (0, 20) },
  { 'name': 'factoryIncomePerPlayer', 'bins': 20, 'range': (0, 20) },
  { 'name': 'interestsPerPlayer', 'bins': 20, 'range': (0, 20) },
  { 'name': 'cumuledIncomePerPlayer', 'bins': 25, 'range': (-10, 40) },
  { 'name': 'shareScore', 'bins': 25, 'range': (0, 50) },
  { 'name': 'shareValue', 'bins': 20, 'range': (0, 20) },
  { 'name': 'confidenceMarker', 'bins': 25, 'range': (0, 50) },
  { 'name': 'interests', 'bins': 5, 'range': (0, 5) },
  { 'name': 'rankPerPlayer-0', 'bins': 4, 'range': (0, 4) },
  { 'name': 'rankPerPlayer-1', 'bins': 4, 'range': (0, 4) },
  { 'name': 'rankPerPlayer-2', 'bins': 4, 'range': (0, 4) },
  { 'name': 'rankPerPlayer-3', 'bins': 4, 'range': (0, 4) },
]
extraStatsData = []
for data in statsData:
  if data['name'].endswith('PerPlayer'):
    for i in range(4):
      extraData = data.copy()
      extraData['name'] += '-' + str(i)
      extraStatsData.append(extraData)
statsData += extraStatsData

statsResult = {
  data['name']: [[] for i in range(7)] for data in statsData
}

finalShareScore = [ [[] for i in range(60)] for j in range(6) ]
maxShareScore = [ [[] for i in range(60)] for j in range(6) ]

for stat in stats:
  for turnStat in stat:
    turnIndex = turnStat['turnIndex']
    amounts = [(i, amount) for i, amount in turnStat['amountPerPlayer'].items()]
    amounts.sort(key = lambda x: -x[1])
    for i, amount in enumerate(amounts):
      statsResult['rankPerPlayer-' + str(amount[0])][turnIndex].append(i)
    for data in statsData:
      try:
        dataList = turnStat[data['name']].values()
      except AttributeError:
        dataList = turnStat[data['name']]
      except KeyError:  # Probably an per-player data
        continue
      statsResult[data['name']][turnIndex].append(dataList)
      if data['name'].endswith('PerPlayer'):
        for key, value in turnStat[data['name']].items():
          statsResult[data['name'] + '-' + str(key)][turnIndex].append(value)

    if turnIndex < 6:
      for firm in Firms:
        maxValue = max([stat[i]['shareScore'][firm]
                        for i in range(turnIndex, 6)])
        finalShareScore[turnIndex][turnStat['shareScore'][firm]].append(
            stat[-1]['shareScore'][firm])
        maxShareScore[turnIndex][turnStat['shareScore'][firm]].append(maxValue)

finalShareScore = [ [numpy.mean(values) if values else None for values in turn]
                    for turn in finalShareScore ]
maxShareScore = [ [numpy.mean(values) if values else None for values in turn]
                    for turn in maxShareScore ]

for turn in finalShareScore:
  prevValue = 0
  for i, value in enumerate(turn):
    turn[i] = turn[i] if turn[i] else prevValue
    prevValue = turn[i]

for turn in maxShareScore:
  prevValue = 0
  for i, value in enumerate(turn):
    turn[i] = turn[i] if turn[i] else prevValue
    prevValue = turn[i]

print finalShareScore
print
print maxShareScore

for data in statsData:
  printHisto(data['name'], data['bins'], data['range'], statsResult)

for name in actionNames:
  printHisto(name, 20, (0, 20), actionStats)
