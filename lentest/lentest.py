from random import shuffle
from random import random

def mprint(c):
	pass
	#print c

init_black = [8, 17, 23, 31, 40]#, 50]
init_crash = [5, 7, 10, 15, 20]#, 25]

sumturn = 0
sumnbcrashpergame = 0
sumnbcrash = {}
sumcrashspace = {}

for black in init_black:
	sumnbcrash[black] = 0
	sumcrashspace[black] = 0

nb = 0.0
for i in xrange(500):
	red_tiles = [1,1,1,1,1,2,2,2,2,3,3,3]
	red_discard = []
	blue_tiles = [4,4,4,4,4,5,5,5,5,6,6,6]
	blue_discard = []
	green_tiles = [7,7,7,7,7,8,8,8,8,9,9,9]
	green_discard = []
	black_tiles = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
	black_discard = []

	shuffle(red_tiles)
	shuffle(blue_tiles)
	shuffle(green_tiles)

	bag = []
	bag.append(red_tiles.pop())
	bag.append(red_tiles.pop())
	bag.append(blue_tiles.pop())
	bag.append(blue_tiles.pop())
	bag.append(green_tiles.pop())
	bag.append(green_tiles.pop())
	bag.append(black_tiles.pop())
	bag.append(black_tiles.pop())

	next_black = init_black[:]
	next_crash = init_crash[:]

	red = 0
	blue = 0
	green = 0
	black = next_black.pop(0)
	crash = next_crash.pop(0)

	turn = 0
	nbplayer = 4
	nbtokens = [0,0,0,0,0]
	crashpergame = 0
	while True:
		player = turn % nbplayer
		mprint("P" + str(player) + "  " + str(red) + ", " + str(blue) + ", " + str(green) + ", " + str(black))
		if not bag:
			draw = -1
		else:
			shuffle(bag)
			draw = bag.pop()
			if draw < 0:
				black_discard.append(draw)
			elif draw <= 3:
				red_discard.append(draw)
			elif draw <= 6:
				blue_discard.append(draw)
			else:
				green_discard.append(draw)
		if draw < 0:
			black += 1
			if black == next_black[0]:
				mprint("no crash")
				sumcrashspace[next_black[0]] += black
				black = next_black.pop(0)
				crash = next_crash.pop(0)
				if not next_black:
					break
		elif draw <= 3:
			red += draw
			if (red >= black):
				mprint("red crash")
				red = black
				red -= crash
				crashpergame += 1
				sumnbcrash[next_black[0]] += 1
				sumcrashspace[next_black[0]] += black
				black = next_black.pop(0)
				crash = next_crash.pop(0)
				if not next_black:
					break
		elif draw <= 6:
			blue += draw - 3
			if (blue >= black):
				mprint("blue crash")
				blue = black
				blue -= crash
				crashpergame += 1
				sumnbcrash[next_black[0]] += 1
				sumcrashspace[next_black[0]] += black
				black = next_black.pop(0)
				crash = next_crash.pop(0)
				if not next_black:
					break
		else:
			green += draw - 6
			if (green >= black):
				mprint("green crash")
				green = black
				green -= crash
				crashpergame += 1
				sumnbcrash[next_black[0]] += 1
				sumcrashspace[next_black[0]] += black
				black = next_black.pop(0)
				crash = next_crash.pop(0)
				if not next_black:
					break

		r = random()
		if nbtokens[player] == 0 and r < 0.8:
			# 80% of chances of planning
			mprint("Add stuff to the bag.")
			if not red_tiles:
				red_tiles = red_discard
				shuffle(red_tiles)
				red_discard = []
			if not blue_tiles:
				blue_tiles = blue_discard
				shuffle(blue_tiles)
				blue_discard = []
			if not green_tiles:
				green_tiles = green_discard
				shuffle(green_tiles)
				green_discard = []
			if not black_tiles:
				black_tiles = black_discard
				black_discard = []
			if red_tiles:
				bag.append(red_tiles.pop())
			if blue_tiles:
				bag.append(blue_tiles.pop())
			if green_tiles:
				bag.append(green_tiles.pop())
			if black_tiles:
				bag.append(black_tiles.pop())
		elif nbtokens[player] > 0 and r < 0.8:
			# 80% of chances of using a tile
			print "Use a tile."
			nbtokens[player] -= 1

		turn += 1

	sumnbcrashpergame += crashpergame
	sumturn += turn
	nb += 1.0

print "Nb turns: " + str(sumturn / nb)
print "Nb crash per game: " + str(sumnbcrashpergame / nb)
print "Nb crash:"
for key, value in sumnbcrash.iteritems():
	print str(key) + " = " + str(value / nb)

print "Crash space:"
for key, value in sumcrashspace.iteritems():
	print str(key) + " = " + str(value / nb)



