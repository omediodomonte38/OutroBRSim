import random
import sys
import csv


#-----------------------------------------
#variables - magic numbers!
hideVal = 2
findVal = 66

searchThresh = 40
restThresh = 60
attackThresh = 95
#-----------------------------------------



def attempt(nameKiller, nameKilled):
	print(nameKiller+" intentou matar a "+nameKilled+" pero non deu e ambos escaparon vivos")

def killMsg(nameKiller, nameKilled):
	print(nameKiller+" matou a "+nameKilled)

def pickUp(self, item):
	print(self.name+" atopou "+item.name+" que lle da: HP: "+str(item.hp)+" ATK: "+str(item.atk)+" DEF: "+str(item.deff))
	strItems = ""
	for i in self.itemLst:
		strItems = strItems +" "+i.name+","
	strItems = strItems[:-1] #cutre
	if not strItems == "":	
		print("	En total ten:"+strItems)


def hidMsg(name):
	print(name+" escondeuse")

def failedToAttack(nameKiller, nameKilled):
	print(nameKiller+" tentou matar a "+nameKilled+" pero non deu con el")

def chill(name):
	print(name+" descansou para recuperar folgos")

def slacks(name):
	print(name+" non deu feito nada con xeito en todo o día")

def failedToFind(name):
	print(name+" explorou pero non atopou nada")

def failedToKill(nameKiller, nameKilled):
	print(nameKiller+" tentou matar a algúen pero so atopou cadáveres")

def betterNot(name):
	print(name+" pensou en atacar pero recapacitou ao verse ferido")



def scrambled(orig):
	dest = orig[:]
	random.shuffle(dest)
	return dest



class GameMaster:
	def __init__(self, masterLst, playerLst):
		self.masterLst = masterLst
		self.playerLst = playerLst

class Item:
	def __init__(self, name, hp, deff, atk):
		self.name = name
		self.hp = hp
		self.deff = deff
		self.atk = atk


class Player:

	# Initializer / Instance Attributes
	def __init__(self, name, hp, deff, atk, neighbours,GameMaster):
		self.name = name
		self.maxHP = hp
		self.hp = hp
		self.deff = deff
		self.atk = atk
		self.neighbours = neighbours
		self.itemLst = []
		self.preStatus = 0 #0 normal, 1 hiding
		self.GameMaster = GameMaster
		self.wasAttacked = 0

	def equipItem(self, item):
		self.itemLst.append(item)
		self.hp = self.hp + item.hp
		self.deff = self.deff + item.deff
		self.atk = self.atk + item.atk
		pickUp(self, item)

	def resetAttacked(self):
		self.wasAttacked = 0

	def broadCast(self, lst, killed):

		for i in lst:
			neighLst = [x for x in GM.playerLst if x.name == i]
			if len(neighLst) > 0:
				item = neighLst[0] #hacky
				item.neighbours.remove(killed)
				item.neighbours.append(self.name) if self.name not in item.neighbours else item.neighbours



	def attack(self, neighbour): #the attacking player has the initiative, attacks first
		
		neighLst = [x for x in GM.playerLst if x.name == neighbour]
		if not len(neighLst) == 0:
			neighbour = neighLst[0] #hacky

			if neighbour.preStatus == 1: #enemy hidden, bad luck
				failedToAttack(self.name, neighbour.name)
			else:
				if (self.atk - neighbour.deff) >= neighbour.hp:
					if (neighbour.atk - self.deff) > self.hp:
						self.hp = 1
					else:
						self.hp = self.hp -  (neighbour.atk - self.deff)
					
					neighbour.neighbours = list(filter((self.name).__ne__, neighbour.neighbours))

					self.neighbours.remove(neighbour.name)
					self.neighbours = list(set(self.neighbours + neighbour.neighbours))
					self.broadCast(neighbour.neighbours, neighbour.name)

					self.GameMaster.playerLst.remove(neighbour)
					killMsg(self.name, neighbour.name)

				elif (neighbour.atk - self.deff) >= self.hp:

					if (self.atk - neighbour.deff) > neighbour.hp:
						neighbour.hp = 1
					else:
						neighbour.hp = neighbour.hp -  (self.atk - neighbour.deff)

					neighbour.neighbours.remove(self.name)
					self.neighbours = list(filter((neighbour.name).__ne__, self.neighbours))
					neighbour.neighbours = list(set(neighbour.neighbours + self.neighbours)) #valores unicos
					neighbour.broadCast(self.neighbours, self.name)

					self.GameMaster.playerLst.remove(self)
					killMsg(neighbour.name, self.name)


				else:
					self.hp = self.hp -  (neighbour.atk - self.deff)
					neighbour.hp = neighbour.hp -  (self.atk - neighbour.deff)
					neighbour.wasAttacked = 1
					self.wasAttacked = 1
					attempt(self.name, neighbour.name)



	def setPreStatus(self):
		num = random.randint(0, 9)
		if num < hideVal:
			self.preStatus = 1 #hidden
			hidMsg(self.name)
		else:
			self.preStatus = 0

	def doAction(self):
		if self.preStatus == 0:
			num = random.randint(0, 100)
			if num < searchThresh: #search for stuff
				n2 = random.randint(0, 100)
				if num < findVal:
					n2 = random.randint(0, len(GM.masterLst)-1)
					self.equipItem(GM.masterLst[n2])
				else:
					failedToFind(self.name)
			elif num < restThresh: #rest
				self.hp = self.maxHP
				chill(self.name)
			elif num < attackThresh: #attack
				if self.wasAttacked == 0:
					n2 = random.randint(0, len(self.neighbours)-1)
					self.attack(self.neighbours[n2])
				else:
					betterNot(self.name)
			else: #do nothing
				slacks(self.name)

# Game Master
GM = GameMaster([],[])

#read and create items
with open('items.csv') as items_csv:
	csv_reader = csv.reader(items_csv, delimiter=',')
	line_count = 0
	for row in csv_reader:
		if line_count > 0:
			GM.masterLst.append(Item(row[0], int(row[1]),int(row[2]),int(row[3])))
		line_count += 1

print("Engadidos " +str(line_count-1)+ " items",)


# Read and create players
with open('players.csv') as players_csv:
	csv_reader = csv.reader(players_csv, delimiter=',')
	line_count = 0
	for row in csv_reader:
		if line_count > 0:
			tokens = row[4].split(';')
			for i in tokens: #seguridade
				i.strip()
			GM.playerLst.append(Player(row[0], int(row[1]),int(row[2]),int(row[3]),tokens,GM))
		line_count += 1

print("Engadidos " +str(line_count-1)+ " xogadores",)


#print to file
sys.stdout = open("res.txt", "w")

#main loop
counter = 0
while True:
	GM.playerLst = scrambled(GM.playerLst) #aleatorizar orde, non beneficiar a naide
	print("\nDía ",counter)
	for i in GM.playerLst:
		i.resetAttacked()
		i.setPreStatus()
	for i in GM.playerLst:
		i.doAction()
		if(len(GM.playerLst) == 1):
			print(GM.playerLst[0].name+" gañou!!")
			exit(0)
		
	counter += 1




