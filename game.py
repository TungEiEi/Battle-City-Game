import pygame, random, uuid, json
from operator import itemgetter

class Timer():
	def __init__(self):
		self.timers = []

	def add(self, interval, f, repeat = -1):
		options = {
			"interval"	: interval, #ช่วงเวลา
			"callback"	: f,
			"repeat"		: repeat, # ทำซ้ำ
			"times"			: 0,
			"time"			: 0,
			"uuid"			: uuid.uuid4() #สุ่มค่า Item
		}
		self.timers.append(options) # เพิ่ม options ลงใน timers

		return options["uuid"]

	def destroy(self, uuid_nr):
		for timer in self.timers:
			if timer["uuid"] == uuid_nr:
				self.timers.remove(timer)
				return

	def update(self, time_passed):
		for timer in self.timers:
			timer["time"] += time_passed
			if timer["time"] > timer["interval"]:
				timer["time"] -= timer["interval"]
				timer["times"] += 1
				if timer["repeat"] > -1 and timer["times"] == timer["repeat"]:
					self.timers.remove(timer)
				try:
					timer["callback"]()
				except:
					try:
						self.timers.remove(timer)
					except:
						pass

class Castle():
	""" Player's castle/fortress """

	(STATE_STANDING, STATE_DESTROYED) = range(2)
 
	def __init__(self):

		global sprites

		# images
		self.img_undamaged = sprites.subsurface(0, 15*2, 16*2, 16*2)
		self.img_destroyed = sprites.subsurface(16*2, 15*2, 16*2, 16*2)

		# init position
		self.rect = pygame.Rect(12*16, 24*16, 32, 32)

		# set start 
		self.rebuild()

	def draw(self):
		""" Draw castle """
		global screen

		screen.blit(self.image, self.rect.topleft)

	def rebuild(self):
		""" Reset castle """
		self.state = self.STATE_STANDING 
		self.image = self.img_undamaged
		self.active = True  #ทำงาน

	def destroycastle(self):
		""" Destroy castle """
		self.state = self.STATE_DESTROYED
		self.image = self.img_destroyed
		self.active = False #ไม่ทำงาน

class Bonus():
	# bonus types
	(BONUS_GRENADE, BONUS_STAR, BONUS_TANK) = range(3)

	def __init__(self, level):

		global sprites

		# to know where to place
		self.level = level

		self.active = True

		# blinking state
		self.visible = True

		self.rect = pygame.Rect(random.randint(0, 416-32), random.randint(0, 416-32), 32, 32)

		self.bonus = random.choice([self.BONUS_GRENADE,self.BONUS_STAR,self.BONUS_TANK])
		if self.bonus == 0:
			self.image = sprites.subsurface(0, 32*2, 16*2, 15*2)
		elif self.bonus == 1:
			self.image = sprites.subsurface(16*2*3, 32*2, 16*2, 15*2)
		elif self.bonus == 2:
			self.image = sprites.subsurface(16*2*4, 32*2, 16*2, 15*2)

	def draw(self):
		""" draw bonus """
		global screen
		if self.visible:
			screen.blit(self.image, self.rect.topleft)

	def toggleVisibility(self):
		""" Toggle bonus visibility """
		self.visible = not self.visible

class Level():
	# tile constants
	(TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_GRASS, TILE_WATER) = range(5)
	# tile width/height in px
	TILE_SIZE = 16

	def __init__(self, level_number = None):

		global sprites

		# max number of enemies simultaneously  being on map
		self.max_active_enemies = 4

		tile_images = [
			pygame.Surface((8*2, 8*2)),
			sprites.subsurface(48*2, 64*2, 8*2, 8*2),
			sprites.subsurface(48*2, 72*2, 8*2, 8*2),
			sprites.subsurface(56*2, 72*2, 8*2, 8*2),
			sprites.subsurface(64*2, 64*2, 8*2, 8*2),
		]
		self.tile_empty = tile_images[0]
		self.tile_brick = tile_images[1]
		self.tile_steel = tile_images[2]
		self.tile_grass = tile_images[3]
		self.tile_water = tile_images[4]

		self.obstacle_rects = []

		level_number = 1 if level_number == None else level_number%5
		if level_number == 0:
			level_number = 5

		self.loadLevel(level_number)

		# tiles' rects on map, tanks cannot move over
		self.obstacle_rects = []

		# update these tiles
		self.updateObstacleRects()

	def hitTile(self, pos, power = 1, sound = False):
		
		global play_sounds, sounds

		for tile in self.mapr: # tile[0] type, tile[1] position
			if tile[1].topleft == pos:
				if tile[0] == self.TILE_BRICK:
					if play_sounds and sound:
						sounds["brick"].play()
					self.mapr.remove(tile)
					self.updateObstacleRects()
					return True
				elif tile[0] == self.TILE_STEEL:
					if play_sounds and sound:
						sounds["steel"].play()
					if power == 2:
						self.mapr.remove(tile)
						self.updateObstacleRects()
					return True
				else:
					return False

	def updateObstacleRects(self):
		
		global castle

		self.obstacle_rects = [castle.rect]

		for tile in self.mapr:
			if tile[0] in (self.TILE_BRICK, self.TILE_STEEL, self.TILE_WATER):
				self.obstacle_rects.append(tile[1])

	def loadLevel(self, level_number = 1):
		
		filename = "levels/"+str(level_number)
		f = open(filename, "r")
		data = f.read().split("\n")
		self.mapr = []
		x, y = 0, 0
		for row in data:
			for ch in row:
				if ch == "#":
					self.mapr.append((self.TILE_BRICK, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
				elif ch == "@":
					self.mapr.append((self.TILE_STEEL, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
				elif ch == "%":
					self.mapr.append((self.TILE_GRASS, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
				elif ch == "~":
					self.mapr.append((self.TILE_WATER, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
				x += self.TILE_SIZE
			x = 0
			y += self.TILE_SIZE
		return True
		

	def draw(self, tiles = None):
		""" Draw specified map on top of existing surface """

		global screen

		(TILE_BRICK, TILE_STEEL, TILE_GRASS, TILE_WATER) = range(4)

		if tiles == None:
			tiles = [TILE_BRICK, TILE_STEEL, TILE_GRASS, TILE_WATER]

		for tile in self.mapr:
			if tile[0] in tiles:
				if tile[0] == self.TILE_BRICK:
					screen.blit(self.tile_brick, tile[1].topleft)
				elif tile[0] == self.TILE_STEEL:
					screen.blit(self.tile_steel, tile[1].topleft)
				elif tile[0] == self.TILE_GRASS:
					screen.blit(self.tile_grass, tile[1].topleft)
				elif tile[0] == self.TILE_WATER:
					screen.blit(self.tile_water, tile[1].topleft)

class Bullet():
	# direction constants
	(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

	# bullet's stated
	(STATE_REMOVED, STATE_ACTIVE) = range(2)

	(OWNER_PLAYER, OWNER_ENEMY) = range(2)

	def __init__(self, level, position, direction, damage = 100, speed = 5):

		global sprites

		self.level = level
		self.direction = direction
		self.damage = damage
		self.owner = None
		self.owner_class = None

		# 1-regular everyday normal bullet
		# 2-can destroy steel
		self.power = 1

		self.image = sprites.subsurface(75*2, 74*2, 3*2, 4*2)

		# position is player's top left corner, so we'll need to
		# recalculate a bit. also rotate image itself.
		if direction == self.DIR_UP:
			self.rect = pygame.Rect(position[0] + 11, position[1] - 8, 6, 8)
		elif direction == self.DIR_RIGHT:
			self.image = pygame.transform.rotate(self.image, 270)
			self.rect = pygame.Rect(position[0] + 26, position[1] + 11, 8, 6)
		elif direction == self.DIR_DOWN:
			self.image = pygame.transform.rotate(self.image, 180)
			self.rect = pygame.Rect(position[0] + 11, position[1] + 26, 6, 8)
		elif direction == self.DIR_LEFT:
			self.image = pygame.transform.rotate(self.image, 90)
			self.rect = pygame.Rect(position[0] - 8 , position[1] + 11, 8, 6)

		self.speed = speed

		self.state = self.STATE_ACTIVE

	def draw(self):
		""" draw bullet """
		global screen
		if self.state == self.STATE_ACTIVE:
			screen.blit(self.image, self.rect.topleft)
	
	def destroybullet(self):
		self.state = self.STATE_REMOVED

	def update(self):
		global castle, players, enemies, bullets

		if self.state != self.STATE_ACTIVE:
			return

		""" move bullet """
		if self.direction == self.DIR_UP:
			self.rect.topleft = [self.rect.left, self.rect.top - self.speed]
			if self.rect.top < 0:
				if play_sounds and self.owner == self.OWNER_PLAYER:
					sounds["steel"].play()
				self.destroybullet()
				return
		elif self.direction == self.DIR_RIGHT:
			self.rect.topleft = [self.rect.left + self.speed, self.rect.top]
			if self.rect.left > (416 - self.rect.width):
				if play_sounds and self.owner == self.OWNER_PLAYER: # player fire
					sounds["steel"].play()
				self.destroybullet()
				return
		elif self.direction == self.DIR_DOWN:
			self.rect.topleft = [self.rect.left, self.rect.top + self.speed]
			if self.rect.top > (416 - self.rect.height):
				if play_sounds and self.owner == self.OWNER_PLAYER:
					sounds["steel"].play()
				self.destroybullet()
				return
		elif self.direction == self.DIR_LEFT:
			self.rect.topleft = [self.rect.left - self.speed, self.rect.top]
			if self.rect.left < 0:
				if play_sounds and self.owner == self.OWNER_PLAYER:
					sounds["steel"].play()
				self.destroybullet()
				return

		has_collided = False

		# check for collisions with walls. one bullet can destroy several (1 or 2)
		# tiles but explosion remains 1
		rects = self.level.obstacle_rects
		collisions = self.rect.collidelistall(rects)
		if collisions != []:
			for i in collisions:
				if self.level.hitTile(rects[i].topleft, self.power, self.owner == self.OWNER_PLAYER):
					has_collided = True
		if has_collided:
			self.destroybullet()
			return

		# check for collisions with other bullets
		for bullet in bullets:
			if self.state == self.STATE_ACTIVE and bullet.owner != self.owner and bullet != self and self.rect.colliderect(bullet.rect):
				self.destroybullet()
				return

		# check for collisions with player
		for player in players:
			if player.state == player.STATE_ALIVE and self.rect.colliderect(player.rect):
				if player.bulletImpact(self.owner == self.OWNER_PLAYER, self.damage, self.owner_class):
					self.destroybullet()
					return

		# check for collisions with enemies
		for enemy in enemies:
			if enemy.state == enemy.STATE_ALIVE and self.rect.colliderect(enemy.rect):
				if enemy.bulletImpact(self.owner == self.OWNER_ENEMY, self.damage, self.owner_class):
					self.destroybullet()
					return

		# check for collision with castle
		if castle.active and self.rect.colliderect(castle.rect):
			castle.destroycastle()
			self.destroybullet()
			return
	
class Tank():

	# possible directions
	(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

	# states
	(STATE_DEAD, STATE_ALIVE) = range(2)

	# sides
	(SIDE_PLAYER, SIDE_ENEMY) = range(2)

	def __init__(self, level, side, position = None, direction = None):

		global sprites

		# health. 0 health means dead
		self.health = 100

		# px per move
		self.speed = 2

		# how many bullets can tank fire simultaneously
		self.max_active_bullets = 1

		# friend or foe
		self.side = side

		# flashing state. 0-off, 1-on
		self.flash = 0

		# 0 - no superpowers
		# 1 - faster bullets
		# 2 - can fire 2 bullets
		# 3 - can destroy steel
		self.superpowers = 0

		# each tank can pick up 1 bonus
		self.bonus = None

		self.level = level

		if position != None:
			self.rect = pygame.Rect(position, (26, 26))
		else:
			self.rect = pygame.Rect(0, 0, 26, 26)

		if direction == None:
			self.direction = random.choice([self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT])
		else:
			self.direction = direction

		self.state = self.STATE_ALIVE
		
	def draw(self):
		""" draw tank """
		global screen
		if self.state == self.STATE_ALIVE:
			screen.blit(self.image, self.rect.topleft)

	def destroyTank(self):

		self.state = self.STATE_DEAD 

		if self.bonus:
			self.spawnBonus()

	def fire(self, forced = False):
		global bullets

		if self.state == self.STATE_DEAD:
			gtimer.destroy(self.timer_uuid_fire)
			return False

		if not forced:
			active_bullets = 0
			for bullet in bullets:
				if bullet.owner_class == self and bullet.state == bullet.STATE_ACTIVE:
					active_bullets += 1
			if active_bullets >= self.max_active_bullets: 
				return False 

		bullet = Bullet(self.level, self.rect.topleft, self.direction)

		# if superpower level is at least 1
		if self.superpowers > 0:
			bullet.speed = 8

		# if superpower level is at least 3
		if self.superpowers > 2:
			bullet.power = 2

		if self.side == self.SIDE_PLAYER:
			bullet.owner = self.SIDE_PLAYER
		else:
			bullet.owner = self.SIDE_ENEMY
			self.bullet_queued = False

		bullet.owner_class = self
		bullets.append(bullet)
		return True

	def rotate(self, direction, fix_position = True):
		""" Rotate tank
		rotate, update image and correct position
		"""
		self.direction = direction

		if direction == self.DIR_UP:
			self.image = self.image_up
		elif direction == self.DIR_RIGHT:
			self.image = self.image_right
		elif direction == self.DIR_DOWN:
			self.image = self.image_down
		elif direction == self.DIR_LEFT:
			self.image = self.image_left

		if fix_position:
			new_x = self.nearest(self.rect.left, 8) + 3
			new_y = self.nearest(self.rect.top, 8) + 3

			if (abs(self.rect.left - new_x) < 5):
				self.rect.left = new_x

			if (abs(self.rect.top - new_y) < 5):
				self.rect.top = new_y
	
	def nearest(self, num, base):
			""" Round number to nearest divisible """
			return int(round(num / (base * 1.0)) * base)

	def turnAround(self):
		""" Turn tank into opposite direction """
		if self.direction in (self.DIR_UP, self.DIR_RIGHT):
			self.rotate(self.direction + 2, False)
		else:
			self.rotate(self.direction - 2, False)

	def update(self):
		if self.state != self.STATE_ALIVE:
			self.state = self.STATE_DEAD
	
	def bulletImpact(self, friendly_fire = False, damage = 100, tank = None): 

		global play_sounds, sounds

		if not friendly_fire:
			self.health -= damage
			if self.health < 1:
				if self.side == self.SIDE_ENEMY:
					tank.trophies["enemy"+str(self.type)] += 1 #จำนวน enemy ที่ฆ่าได้
					points = (self.type+1) * 100 
					tank.score += points
					if play_sounds:
						sounds["explosion"].play()

				self.destroyTank()
			return True

		if self.side == self.SIDE_ENEMY:
			return False
		
	def givescore(self, tank = None):

		if self.state == self.STATE_DEAD:
			tank.trophies["enemy"+str(self.type)] += 1
			points = (self.type+1) * 100
			tank.score += points
			if play_sounds:
				sounds["explosion"].play()

class Player(Tank):

	def __init__(self, level, type, position = None, direction = None):

		Tank.__init__(self, level, type, position = None, direction = None)

		global sprites

		self.start_position = position
		self.start_direction = direction

		self.lives = 3

		# total score
		self.score = 0

		# store how many bonuses in this stage this player has collected
		self.trophies = {
			"bonus" : 0,
			"enemy0" : 0,
			"enemy1" : 0,
			"enemy2" : 0,
			"enemy3" : 0
		}

		self.image = sprites.subsurface(0, 0, 26, 26)
		self.image_up = self.image
		self.image_left = pygame.transform.rotate(self.image, 90)
		self.image_down = pygame.transform.rotate(self.image, 180)
		self.image_right = pygame.transform.rotate(self.image, 270)

		if direction == None:
			self.rotate(self.DIR_UP, False)
		else:
			self.rotate(direction, False)

	def move(self, direction):
		""" move player if possible """

		global players, enemies, bonuses

		if self.state == self.STATE_DEAD:
			return

		# rotate player
		if self.direction != direction:
			self.rotate(direction)

		# move player
		if direction == self.DIR_UP:
			new_position = [self.rect.left, self.rect.top - self.speed]
			if new_position[1] < 0: # y 
				return
		elif direction == self.DIR_RIGHT:
			new_position = [self.rect.left + self.speed, self.rect.top]
			if new_position[0] > (416 - 26): 
				return
		elif direction == self.DIR_DOWN:
			new_position = [self.rect.left, self.rect.top + self.speed]
			if new_position[1] > (416 - 26):
				return
		elif direction == self.DIR_LEFT:
			new_position = [self.rect.left - self.speed, self.rect.top]
			if new_position[0] < 0:
				return

		player_rect = pygame.Rect(new_position, [26, 26])

		# collisions with tiles
		if player_rect.collidelist(self.level.obstacle_rects) != -1:
			return

		# collisions with enemies
		for enemy in enemies:
			if player_rect.colliderect(enemy.rect) == True:
				return

		# collisions with bonuses
		for bonus in bonuses:
			if player_rect.colliderect(bonus.rect) == True:
				self.bonus = bonus

		#if no collision, move player
		self.rect.topleft = (new_position[0], new_position[1])

	def reset(self):
		""" reset player """
		self.rotate(self.start_direction, False)
		self.rect.topleft = self.start_position
		self.superpowers = 0
		self.max_active_bullets = 1
		self.health = 100
		self.pressed = [False] * 4
		self.state = self.STATE_ALIVE

class Enemy(Tank):

	(TYPE_BASIC, TYPE_FAST, TYPE_POWER, TYPE_ARMOR) = range(4)

	def __init__(self, level, type, position = None, direction = None):

		Tank.__init__(self, level, type, position = None, direction = None)

		global enemies, sprites

		# if true, do not fire
		self.bullet_queued = False

		# chose type on random
		if len(level.enemies_left) > 0:
			self.type = level.enemies_left.pop()
		else:
			self.state = self.STATE_DEAD
			return

		if self.type == self.TYPE_BASIC:
			self.speed = 1
		elif self.type == self.TYPE_FAST:
			self.speed = 3
		elif self.type == self.TYPE_POWER:
			self.superpowers = 1
		elif self.type == self.TYPE_ARMOR:
			self.health = 400

		# 1 in 5 chance this will be bonus carrier, but only if no other tank is
		if random.randint(1, 5) == 1:
			self.bonus = True
			for enemy in enemies:
				if enemy.bonus:
					self.bonus = False # ตัวอื่นเป็น False
					break

		images = [
			sprites.subsurface(32*2, 0, 13*2, 15*2),
			sprites.subsurface(48*2, 0, 13*2, 15*2),
			sprites.subsurface(64*2, 0, 13*2, 15*2),
			sprites.subsurface(80*2, 0, 13*2, 15*2),
			sprites.subsurface(32*2, 16*2, 13*2, 15*2),
			sprites.subsurface(48*2, 16*2, 13*2, 15*2),
			sprites.subsurface(64*2, 16*2, 13*2, 15*2),
			sprites.subsurface(80*2, 16*2, 13*2, 15*2)
		]

		self.image = images[self.type+0]

		self.image_up = self.image
		self.image_left = pygame.transform.rotate(self.image, 90)
		self.image_down = pygame.transform.rotate(self.image, 180)
		self.image_right = pygame.transform.rotate(self.image, 270)

		if self.bonus:
			self.image1_up = self.image_up
			self.image1_left = self.image_left
			self.image1_down = self.image_down
			self.image1_right = self.image_right

			self.image2 = images[self.type+4]
			self.image2_up = self.image2
			self.image2_left = pygame.transform.rotate(self.image2, 90)
			self.image2_down = pygame.transform.rotate(self.image2, 180)
			self.image2_right = pygame.transform.rotate(self.image2, 270)

		self.rotate(self.direction, False)

		if position == None:
			self.rect.topleft = self.SpawningPosition()
			if not self.rect.topleft:
				self.state = self.STATE_DEAD
				return

		# list of map coords where tank should go next
		self.path = self.generatePath(self.direction)

		# 1000 is duration between shots
		self.timer_uuid_fire = gtimer.add(1000, lambda :self.fire())

		# turn on flashing
		if self.bonus:
			self.timer_uuid_flash = gtimer.add(200, lambda :self.toggleFlash())

	def toggleFlash(self):
		""" Toggle flash state """
		if self.state != self.STATE_ALIVE:
			gtimer.destroy(self.timer_uuid_flash)
			return
		self.flash = not self.flash
		if self.flash:
			self.image_up = self.image2_up
			self.image_right = self.image2_right
			self.image_down = self.image2_down
			self.image_left = self.image2_left
		else:
			self.image_up = self.image1_up
			self.image_right = self.image1_right
			self.image_down = self.image1_down
			self.image_left = self.image1_left
		self.rotate(self.direction, False)

	def spawnBonus(self):
		""" Create new bonus if needed """
		global bonuses
		if len(bonuses) > 0:
			return
		
		bonus = Bonus(self.level)
		bonuses.append(bonus)
		bonus.draw()
		gtimer.add(500, lambda :bonus.toggleVisibility())
		gtimer.add(10000, lambda :bonuses.remove(bonus), 1)

	def SpawningPosition(self):

		global players, enemies

		spawn_positions = [[3,3],[195,3],[387,3]]

		random.shuffle(spawn_positions)

		for pos in spawn_positions:

			enemy_rect = pygame.Rect(pos, [26, 26])

			# collisions with other enemies
			collision = False
			for enemy in enemies:
				if enemy_rect.colliderect(enemy.rect):
					collision = True
					continue

			if collision:
				continue

			# collisions with players
			collision = False
			for player in players:
				if enemy_rect.colliderect(player.rect):
					collision = True
					continue

			if collision:
				continue

			return pos
		return False

	def move(self):
		""" move enemy if possible """

		global players, enemies, bonuses

		if self.state != self.STATE_ALIVE:
			return

		if self.path == []:
			self.path = self.generatePath(None, True)

		new_position = self.path.pop(0)

		# move enemy
		if self.direction == self.DIR_UP:
			if new_position[1] < 0:
				self.path = self.generatePath(self.direction, True)
				return
		elif self.direction == self.DIR_RIGHT:
			if new_position[0] > (416 - 26):
				self.path = self.generatePath(self.direction, True)
				return
		elif self.direction == self.DIR_DOWN:
			if new_position[1] > (416 - 26):
				self.path = self.generatePath(self.direction, True)
				return
		elif self.direction == self.DIR_LEFT:
			if new_position[0] < 0:
				self.path = self.generatePath(self.direction, True)
				return

		new_rect = pygame.Rect(new_position, [26, 26])

		# collisions with tiles
		if new_rect.collidelist(self.level.obstacle_rects) != -1:
			self.path = self.generatePath(self.direction, True)
			return

		# collisions with other enemies
		for enemy in enemies:
			if enemy != self and new_rect.colliderect(enemy.rect):
				self.turnAround()
				self.path = self.generatePath(self.direction)
				return

		# collisions with players
		for player in players:
			if new_rect.colliderect(player.rect):
				self.turnAround()
				self.path = self.generatePath(self.direction)
				return

		# collisions with bonuses
		for bonus in bonuses:
			if new_rect.colliderect(bonus.rect):
				bonuses.remove(bonus)

		# if no collision, move enemy
		self.rect.topleft = new_rect.topleft

	def update(self):
		if self.state != self.STATE_ALIVE:
			self.state = self.STATE_DEAD
		elif self.state == self.STATE_ALIVE:
			self.move()

	def generatePath(self, direction = None, fix_direction = False):
		""" If direction is specified, try continue that way, otherwise choose at random
		"""

		all_directions = [self.DIR_UP, self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT]

		if direction == None:
			if self.direction in [self.DIR_UP, self.DIR_RIGHT]:
				opposite_direction = self.direction + 2
			else:
				opposite_direction = self.direction - 2
			directions = all_directions
			random.shuffle(directions)
			directions.remove(opposite_direction)
			directions.append(opposite_direction)
		else:
			if direction in [self.DIR_UP, self.DIR_RIGHT]:
				opposite_direction = direction + 2
			else:
				opposite_direction = direction - 2

			if direction in [self.DIR_UP, self.DIR_RIGHT]:
				opposite_direction = direction + 2
			else:
				opposite_direction = direction - 2
			directions = all_directions
			random.shuffle(directions)
			directions.remove(opposite_direction)
			directions.remove(direction)
			directions.insert(0, direction)
			directions.append(opposite_direction)

		# at first, work with general units (steps) not px
		x = int(round(self.rect.left / 16))
		y = int(round(self.rect.top / 16))

		new_direction = None

		for direction in directions:
			if direction == self.DIR_UP and y > 1:
				new_pos_rect = self.rect.move(0, -8)
				if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
					new_direction = direction
					break
			elif direction == self.DIR_RIGHT and x < 24:
				new_pos_rect = self.rect.move(8, 0)
				if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
					new_direction = direction
					break
			elif direction == self.DIR_DOWN and y < 24:
				new_pos_rect = self.rect.move(0, 8) # ให้สี่เหลี่ยมเช็ค
				if new_pos_rect.collidelist(self.level.obstacle_rects) == -1: # ไม่ชน
					new_direction = direction
					break
			elif direction == self.DIR_LEFT and x > 1:
				new_pos_rect = self.rect.move(-8, 0)
				if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
					new_direction = direction
					break

		# if we can go anywhere else, turn around
		if new_direction == None:
			new_direction = opposite_direction

		# fix tanks position
		if fix_direction and new_direction == self.direction:
			fix_direction = False

		self.rotate(new_direction, fix_direction)

		positions = []

		x = self.rect.left
		y = self.rect.top

		if new_direction in (self.DIR_RIGHT, self.DIR_LEFT):
			axis_fix = self.nearest(y, 16) - y
		else:
			axis_fix = self.nearest(x, 16) - x
		axis_fix = 0

		pixels = self.nearest(random.randint(1, 12) * 32, 32) + axis_fix + 3

		if new_direction == self.DIR_UP:
			for px in range(0, pixels, self.speed):
				positions.append([x, y-px])
		elif new_direction == self.DIR_RIGHT:
			for px in range(0, pixels, self.speed):
				positions.append([x+px, y])
		elif new_direction == self.DIR_DOWN:
			for px in range(0, pixels, self.speed):
				positions.append([x, y+px])
		elif new_direction == self.DIR_LEFT:
			for px in range(0, pixels, self.speed):
				positions.append([x-px, y])

		return positions

class Game():

	# direction constants
	(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

	TILE_SIZE = 16

	def __init__(self):

		global screen, sprites, play_sounds, sounds

		if play_sounds:
			pygame.mixer.pre_init(44100, -16, 1, 512)

		pygame.init()

		pygame.display.set_caption("Battle City")

		size = 480, 416
		screen = pygame.display.set_mode(size)
		self.clock = pygame.time.Clock()

		sprites = pygame.transform.scale(pygame.image.load("images/sprites.gif"), [192, 224])
		
		pygame.display.set_icon(sprites.subsurface(0, 0, 13*2, 13*2))

		# load sounds
		if play_sounds:
			pygame.mixer.init(44100, -16, 1, 512)

			sounds["start"] = pygame.mixer.Sound("sounds/gamestart.ogg")
			sounds["end"] = pygame.mixer.Sound("sounds/gameover.ogg")
			sounds["score"] = pygame.mixer.Sound("sounds/score.ogg")
			sounds["bg"] = pygame.mixer.Sound("sounds/background.ogg")
			sounds["fire"] = pygame.mixer.Sound("sounds/fire.ogg")
			sounds["bonus"] = pygame.mixer.Sound("sounds/bonus.ogg")
			sounds["explosion"] = pygame.mixer.Sound("sounds/explosion.ogg")
			sounds["brick"] = pygame.mixer.Sound("sounds/brick.ogg")
			sounds["steel"] = pygame.mixer.Sound("sounds/steel.ogg")

		self.enemy_life_image = sprites.subsurface(81*2, 57*2, 7*2, 7*2)
		self.player_life_image = sprites.subsurface(89*2, 56*2, 7*2, 8*2)
		self.flag_image = sprites.subsurface(64*2, 49*2, 16*2, 15*2)

		# this is used in intro screen
		self.cursor_image = pygame.transform.rotate(sprites.subsurface(0, 0, 13*2, 13*2), 270)
		self.cursor = 1

		# load custom font
		self.font = pygame.font.Font("fonts/prstart.ttf", 16)
		self.title = pygame.font.Font("fonts/prstart.ttf", 48)
		self.credit = pygame.font.Font("fonts/prstart.ttf", 10)

		# pre-render game over text
		self.im_game_over = pygame.Surface((64, 40))
		self.im_game_over.set_colorkey((0,0,0))
		self.im_game_over.blit(self.font.render("GAME", False, (127, 64, 64)), [0, 0])
		self.im_game_over.blit(self.font.render("OVER", False, (127, 64, 64)), [0, 20])
		self.game_over_y = 416+40

		del players[:]
		del bullets[:]
		del enemies[:]
		del bonuses[:]

	def showMenu(self):
		global players, screen

		# stop game main loop (if any)
		self.running = False

		# clear all timers
		del gtimer.timers[:]

		# set current stage to 0
		self.stage = 0

		self.animateIntroScreen()

		main_loop = True
		while main_loop:
			time_passed = self.clock.tick(50)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quit()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_UP:
						if self.cursor == 2:
							self.cursor = 1
							self.drawIntroScreen()
						elif self.cursor == 3:
							self.cursor = 2
							self.drawIntroScreen()
					elif event.key == pygame.K_DOWN:
						if self.cursor == 1:
							self.cursor = 2
							self.drawIntroScreen()
						elif self.cursor == 2:
							self.cursor = 3
							self.drawIntroScreen()
					elif event.key == pygame.K_RETURN:
						if self.cursor == 1:
							main_loop = False
							del players[:] #delete all (score)
							self.nextLevel()
						if self.cursor == 2:
							self.scoreboard()
						if self.cursor == 3:
							quit()
	
	def drawIntroScreen(self, put_on_surface = True):
		""" Draw intro (menu) screen
		@param boolean put_on_surface If True, flip display after drawing
		@return None
		"""

		global screen

		screen.fill([0, 0, 0])

		if pygame.font.get_init():

			with open('score.json', 'r') as file:
				self.playerScore = json.load(file)
				
			screen.blit(self.title.render("BATTLE", True, pygame.Color('purple')), [96, 80])
			screen.blit(self.title.render("CITY", True, pygame.Color('purple')), [144, 160])

			screen.blit(self.font.render("PLAY", True, pygame.Color('white')), [208, 250])
			screen.blit(self.font.render("SCORE", True, pygame.Color('white')), [208, 290])
			screen.blit(self.font.render("EXIT", True, pygame.Color('white')), [208, 330])

			screen.blit(self.credit.render("BY 65010268 NAPAT WORATHUNYATHORN", True, pygame.Color('pink')), [75, 400])

		if self.cursor == 1:
			screen.blit(self.cursor_image, [168, 245])
		elif self.cursor == 2:
			screen.blit(self.cursor_image, [168, 285])
		elif self.cursor == 3:
			screen.blit(self.cursor_image, [168, 325])

		if put_on_surface:
			pygame.display.flip()
	
	def animateIntroScreen(self):
		
		global screen

		self.drawIntroScreen(False)
		screen_cp = screen.copy()

		screen.fill([0, 0, 0])

		y = 416
		while (y > 0):
			time_passed = self.clock.tick(50)
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						y = 0
						break

			screen.blit(screen_cp, [0, y])
			pygame.display.flip()
			y -= 5

		screen.blit(screen_cp, [0, 0])
		pygame.display.flip()
	

	def scoreboard(self):
		global screen

		screen.fill([0, 0, 0])
		screen.blit(self.font.render("SCOREBOARD", True, pygame.Color('purple')), [160, 40])

		with open('score.json', 'r') as file:
			playerScore = json.load(file)

		self.alltext = []
		for i,data in enumerate(playerScore):
			name = str(data[0])
			score = str(data[1])
			self.alltext.append([name,score])
			screen.blit(self.font.render(str(i+1)+'.', True, pygame.Color('lavender')), [50, 100+52*i])
			screen.blit(self.font.render(name, True, pygame.Color('white')), [82, 100+52*i])
			screen.blit(self.font.render(score.rjust(10), True, pygame.Color('lavender')), [260, 100+52*i])
		
		pygame.display.flip()
		
		while 1:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quit()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						self.showMenu()


	def triggerBonus(self, bonus, player):
		""" Execute bonus powers """

		global enemies, play_sounds, sounds

		if play_sounds:
			sounds["bonus"].play()

		player.trophies["bonus"] += 1
		player.score += 500

		if bonus.bonus == bonus.BONUS_GRENADE:
			for enemy in enemies:
				enemy.destroyTank()
				enemy.givescore(player)
				
		elif bonus.bonus == bonus.BONUS_STAR:
			player.superpowers += 1
			if player.superpowers == 2:
				player.max_active_bullets = 2
		elif bonus.bonus == bonus.BONUS_TANK:
			player.lives += 1
		bonuses.remove(bonus)

	def spawnEnemy(self):

		global enemies

		if len(enemies) >= self.level.max_active_enemies:
			return
		if len(self.level.enemies_left) < 1:
			return
		enemy = Enemy(self.level, 1)

		enemies.append(enemy) # add enemy
	
	def respawnPlayer(self, player, clear_scores = False):
		""" Respawn player """
		player.reset()

		if clear_scores:
			player.trophies = {
				"bonus" : 0, "enemy0" : 0, "enemy1" : 0, "enemy2" : 0, "enemy3" : 0
			}

	def draw(self):
		global screen, castle, players, enemies, bullets, bonuses

		screen.fill([0, 0, 0])

		self.level.draw([self.level.TILE_EMPTY, self.level.TILE_BRICK, self.level.TILE_STEEL, self.level.TILE_WATER])

		castle.draw()

		for enemy in enemies:
			enemy.draw()

		for player in players:
			player.draw()

		for bullet in bullets:
			bullet.draw()

		for bonus in bonuses:
			bonus.draw()

		self.level.draw([self.level.TILE_GRASS])

		if self.game_over:
			if self.game_over_y > 188:
				self.game_over_y -= 4
			screen.blit(self.im_game_over, [176, self.game_over_y]) # 176=(416-64)/2
 
		self.drawSidebar()

		pygame.display.flip()

	def drawSidebar(self):

		global screen, players, enemies

		x = 416
		y = 0
		screen.fill([100, 100, 100], pygame.Rect([416, 0], [64, 416]))

		xpos = x + 16
		ypos = y + 16

		# draw enemy lives
		for n in range(len(self.level.enemies_left) + len(enemies)):
			screen.blit(self.enemy_life_image, [xpos, ypos])
			if n % 2 == 1:
				xpos = x + 16
				ypos+= 17
			else:
				xpos += 17

		# players' lives
		if pygame.font.get_init():
			text_color = pygame.Color('black')

			screen.blit(self.font.render(str(players[0].lives), False, text_color), [x+31, y+215])
			screen.blit(self.player_life_image, [x+17, y+215])

			screen.blit(self.flag_image, [x+17, y+280])
			screen.blit(self.font.render(str(self.stage), False, text_color), [x+17, y+312])
	

	def nextLevel(self):
		""" Start next level """

		global castle, players, bullets, bonuses, play_sounds, sounds

		del bullets[:] # clear all 
		del enemies[:]
		del bonuses[:]
		castle.rebuild()
		del gtimer.timers[:]

		# load level
		self.stage += 1
		self.level = Level(self.stage)

		# set number of enemies by types (basic, fast, power, armor) according to level
		levels_enemies = [(18,2,0,0), (10,6,4,0), (8,6,4,2), (2,4,6,8), (0,4,6,10),]

		if self.stage <= 5:
			enemies_l = levels_enemies[self.stage - 1] #
		else:
			enemies_l = levels_enemies[4]

		self.level.enemies_left = [0]*enemies_l[0] + [1]*enemies_l[1] + [2]*enemies_l[2] + [3]*enemies_l[3]
		random.shuffle(self.level.enemies_left)

		if play_sounds:
			sounds["start"].play()
			gtimer.add(4330, lambda :sounds["bg"].play(-1), 1)
		
		if len(players) == 0: # เพิ่มตัวละครครั้งเดียว	

			x = 8 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
			y = 24 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2

			player = Player(self.level, 0, [x, y], self.DIR_UP)
			players.append(player)

		for player in players:
			player.level = self.level
			self.respawnPlayer(player,True) # clear trophies เมื่อไปด่านถัดไป

		gtimer.add(3000, lambda :self.spawnEnemy())

		# if True, start "game over" animation
		self.game_over = False

		# if False, game will end w/o "game over" bussiness
		self.running = True

		# if False, players won't be able to do anything
		self.active = True

		self.draw()

		while self.running: # run game

			time_passed = self.clock.tick(50)

			for event in pygame.event.get(): # read button
				if event.type == pygame.QUIT:
					quit()
				elif event.type == pygame.KEYDOWN and not self.game_over and self.active:

					if event.key == pygame.K_ESCAPE:
						self.running = False
						pygame.mixer.stop()
						self.showMenu()

					for player in players:
						if player.state == player.STATE_ALIVE:
							if event.key == pygame.K_SPACE:
								player.fire()
							elif event.key == pygame.K_UP: # up
								player.pressed[0] = True
							elif event.key == pygame.K_RIGHT:
								player.pressed[1] = True
							elif event.key == pygame.K_DOWN:
								player.pressed[2] = True
							elif event.key == pygame.K_LEFT:
								player.pressed[3] = True
					
				elif event.type == pygame.KEYUP and not self.game_over and self.active:
					for player in players:
						if player.state == player.STATE_ALIVE:
							if event.key == pygame.K_UP: # up
								player.pressed[0] = False
							elif event.key == pygame.K_RIGHT:
								player.pressed[1] = False
							elif event.key == pygame.K_DOWN:
								player.pressed[2] = False
							elif event.key == pygame.K_LEFT:
								player.pressed[3] = False

			for player in players: # move player
				if player.state == player.STATE_ALIVE and not self.game_over and self.active:
					if player.pressed[0] == True:
						player.move(self.DIR_UP)
					elif player.pressed[1] == True:
						player.move(self.DIR_RIGHT)
					elif player.pressed[2] == True:
						player.move(self.DIR_DOWN)
					elif player.pressed[3] == True:
						player.move(self.DIR_LEFT)
				player.update()

			for bullet in bullets:
				if bullet.state == bullet.STATE_REMOVED:
					bullets.remove(bullet)
				else:
					bullet.update()

			for enemy in enemies:
				if enemy.state == enemy.STATE_DEAD and not self.game_over and self.active:
					enemies.remove(enemy)
					if len(self.level.enemies_left) == 0 and len(enemies) == 0:
						self.finishLevel()
				else:
					enemy.update()

			if not self.game_over and self.active:
				for player in players:
					if player.state == player.STATE_ALIVE:
						if player.bonus != None and player.side == player.SIDE_PLAYER:
							self.triggerBonus(bonus, player)
							player.bonus = None
					elif player.state == player.STATE_DEAD:
						self.superpowers = 0
						player.lives -= 1
						if player.lives > 0:
							self.respawnPlayer(player)
						else:
							self.gameOver()

			for bonus in bonuses:
				if bonus.active == False:
					bonuses.remove(bonus)

			if not self.game_over:
				if not castle.active:
					self.gameOver()

			gtimer.update(time_passed)

			self.draw()
	
	def finishLevel(self):
		""" Finish current level
		Show earned scores and advance to the next stage
		"""

		global play_sounds, sounds

		if play_sounds:
			sounds["bg"].stop()

		self.active = False
		gtimer.add(3000, lambda :self.showScores(), 1)
	
	def gameOver(self):
		""" End game and return to menu """

		global play_sounds, sounds

		# print "Game Over"
		if play_sounds:
			for sound in sounds:
				sounds[sound].stop()
			sounds["end"].play()

		self.game_over_y = 416+40

		self.game_over = True
		gtimer.add(3000, lambda :self.showScores(), 1)

	def showScores(self):
		""" Show level scores """

		global screen, sprites, players, play_sounds, sounds

		# stop game main loop (if any)
		self.running = False

		# clear all timers
		del gtimer.timers[:]

		if play_sounds:
			for sound in sounds:
				sounds[sound].stop()

		img_tanks = [
			sprites.subsurface(32*2, 0, 13*2, 15*2),
			sprites.subsurface(48*2, 0, 13*2, 15*2),
			sprites.subsurface(64*2, 0, 13*2, 15*2),
			sprites.subsurface(80*2, 0, 13*2, 15*2)
		]

		img_arrows = [
			sprites.subsurface(81*2, 48*2, 7*2, 7*2),
			sprites.subsurface(88*2, 48*2, 7*2, 7*2)
		]

		screen.fill([0, 0, 0])

		# colors
		black = pygame.Color("black")
		white = pygame.Color("white")
		purple = pygame.Color(127, 64, 64)
		pink = pygame.Color(191, 160, 128)

		screen.blit(self.font.render("STAGE"+str(self.stage).rjust(3), False, white), [170, 65])

		screen.blit(self.font.render("I-PLAYER", False, purple), [25, 95])

		#player 1 global score
		screen.blit(self.font.render(str(players[0].score).rjust(8), False, pink), [25, 125])

		# tanks and arrows
		for i in range(4):
			screen.blit(img_tanks[i], [226, 160+(i*45)])
			screen.blit(img_arrows[0], [206, 168+(i*45)])

		screen.blit(self.font.render("TOTAL", False, white), [70, 335])

		# total underline
		pygame.draw.line(screen, white, [170, 330], [307, 330], 4)

		pygame.display.flip()

		self.clock.tick(2)

		interval = 5

		# points and kills
		for i in range(4):

			# total specific tanks
			tanks = players[0].trophies["enemy"+str(i)]

			for n in range(tanks+1):
				if n > 0 and play_sounds:
					sounds["score"].play()

				# erase previous text
				screen.blit(self.font.render(str(n-1).rjust(2), False, black), [170, 168+(i*45)])
				# print new number of enemies
				screen.blit(self.font.render(str(n).rjust(2), False, white), [170, 168+(i*45)])
				# erase previous text
				screen.blit(self.font.render(str((n-1) * (i+1) * 100).rjust(4)+" PTS", False, black), [25, 168+(i*45)])
				# print new total points per enemy
				screen.blit(self.font.render(str(n * (i+1) * 100).rjust(4)+" PTS", False, white), [25, 168+(i*45)])
				pygame.display.flip()
				self.clock.tick(interval)

			self.clock.tick(interval)

		# total tanks
		tanks = sum([i for i in players[0].trophies.values()]) - players[0].trophies["bonus"]
		screen.blit(self.font.render(str(tanks).rjust(2), False, white), [170, 335])

		pygame.display.flip()

		# do nothing for 2 seconds
		self.clock.tick(1)
		self.clock.tick(1)

		if self.game_over:
			self.gameOverScreen()
		else:
			self.nextLevel()
	
	def gameOverScreen(self):
		""" Show game over screen """

		global screen, sprites
		
		self.name = ''
		arrow = sprites.subsurface(88*2, 48*2, 7*2, 7*2)

		while 1:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					quit()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_BACKSPACE:
						self.name = self.name[:-1]
					elif event.key == pygame.K_RETURN:
						if self.name != '':

							with open('score.json', 'r') as file:
								playerScore = json.load(file)
							
							playerScore.append([self.name.upper(),int(players[0].score)])
							playerScore = sorted(playerScore,reverse = True, key = itemgetter(1))
							if len(playerScore) > 5:
								playerScore.pop()
								
							with open('score.json', 'w+') as file:
								json.dump(playerScore,file)
	
							self.showMenu()

					else:
						self.name += event.unicode
						if len(self.name) >= 13:
							self.name = self.name[:-1]

			screen.fill([0, 0, 0])
			screen.blit(self.title.render("GAME", True, pygame.Color('crimson')), [144, 80])
			screen.blit(self.title.render("OVER", True, pygame.Color('crimson')), [144, 160])
			screen.blit(self.font.render("ENTER YOUR NAME", True, pygame.Color('orange')), [120, 240])
			screen.blit(arrow, [120, 280])
			screen.blit(self.font.render(self.name.upper(), True, pygame.Color('white')), [152, 280])
			pygame.display.flip()

if __name__ == "__main__":

	gtimer = Timer()

	sprites = None
	screen = None
	players = []
	enemies = []
	bullets = []
	bonuses = []

	play_sounds = True
	sounds = {}

	game = Game()
	castle = Castle()
	game.showMenu()
