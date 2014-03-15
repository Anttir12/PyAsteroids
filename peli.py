import pygame, sys, math, random
import re
from pygame.locals import * 

fps = 60
width = 1920
height = 1080

	
class game():

	def __init__(self):
		pygame.init()
		self.clock = pygame.time.Clock()
		global width, height
		infoObject = pygame.display.Info()
		width, height = (infoObject.current_w, infoObject.current_h)#Get players resolution
		pygame.display.set_mode((0,0),pygame.FULLSCREEN)#set to fullscreen
		pygame.display.set_caption("Peli testausta")
		self.screen = pygame.display.get_surface()
		self.background = pygame.image.load("Tausta.png").convert()#Load background
		self.player = Player(50,50,width,height)
		self.score = 0
		self.font = pygame.font.SysFont(None, 36)#Set font
		self.allsprites = pygame.sprite.RenderUpdates(self.player)
		self.allasteroids = pygame.sprite.Group()#create a group of sprites for asteroids
		self.allBullets = pygame.sprite.Group()#create a group of sprites for bullets
		self.rate_of_fire = 0
		self.createAsteroid = False
		self.settings = Settings(self.screen,width,height)
		self.menu = Menu(self.screen, self.settings,width,height)
		
		
	def run(self):
		firing = False
		onmenu = True
		while True: #show menu
			if onmenu:
				self.menu.drawMenu()
				onmenu = False
			self.clock.tick(fps)#set max fps
			
			
			for event in pygame.event.get():#Event handling
				if event.type == QUIT:
					sys.exit(0)
					
					#..........KEY DOWNS.......#
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_LEFT:
						self.player.rotatespeed(1, True)	#rotate
					elif event.key == pygame.K_RIGHT:
						self.player.rotatespeed(-1, False)#rotate
					elif event.key == pygame.K_UP:
						self.player.accelerate(-1)	#Accelerate
					elif event.key == pygame.K_DOWN:
						self.player.accelerate(1)	
					elif event.key == pygame.K_r:	#Reset
						if self.player.alive():
							self.player.resetpos()
							self.allasteroids.empty()
							self.score = 0
						else:
							self.player = Player(width/2,height/2,width,height)
							self.allasteroids.empty()
							self.allsprites.add(self.player)
							self.score = 0
							
					elif event.key == pygame.K_c:	#Shield
						if self.player.check_shield_CD() == True:
							self.player.shield()
					
					elif event.key == pygame.K_SPACE:	#Fire
						if self.player.alive():
							firing = True
							self.rate_of_fire = 10
							
					elif event.key == pygame.K_z:	#Spawn an extra asteroid
						self.createAsteroid = True
					
						
					elif event.key == pygame.K_ESCAPE:	#open menu
						onmenu = True		

					
					#..........KEY UPS........#
				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_LEFT:
						self.player.rotatespeed(0, True)
					elif event.key == pygame.K_RIGHT:
						self.player.rotatespeed(0, False)
					elif event.key == pygame.K_UP:
						self.player.accelerate(0)
					elif event.key == pygame.K_DOWN:
						self.player.accelerate(0)
					elif event.key == pygame.K_SPACE:
						firing = False
			
			self.fire(firing)	#If space is down -> pewpew
			self.checkAsteroids()#Check if new asteroids needs to be made
			
			
			#call update() of every sprite	
			self.allsprites.update()			
			self.allasteroids.update(self.player.rect.x, self.player.rect.y)
			
			#Checks if pewpews hits anything and kills the bullet and asteroid if it does hit
			for bullet in self.allBullets:
				asteroid_hit_list = pygame.sprite.spritecollide(bullet, self.allasteroids, True)
				
				for asteroid in asteroid_hit_list:
					self.allBullets.remove(bullet)
					self.allsprites.remove(bullet)
					self.score += 1
					
					
			#Checks if player gets hit by an asteroid
			osuma = pygame.sprite.spritecollide(self.player, self.allasteroids, True)
			if (len(osuma) > 0 and not self.player.check_shield()):
				self.player.kill()
				self.allsprites.remove(self.player)
			
			self.screen.blit(self.background,(0,0))
			if pygame.font:#Blit score text
				self.score_text = self.font.render("Score: %d" %(self.score) ,2, (255, 255, 225))
				self.screen.blit(self.score_text, (width-200,height-75))
			
			self.allsprites.draw(self.screen)#draw player and bullets on the screen
			self.allasteroids.draw(self.screen)
			
			
			pygame.display.flip()
		
			
	def checkAsteroids(self):#Spawns asteroids if less than x(10) ammount alive
		tmp = self.allasteroids.sprites()
		speed = self.settings.getSpeed()#get the speed set for the asteroids
		AmmountofAsteroids = self.settings.getSettings()#get the ammount of asteroids set in the settings
		if len(tmp) < AmmountofAsteroids or self.createAsteroid:#If there is less than X asteroids spawn a new one, or if player wants to create one automatically
			self.createAsteroid = False
			while True:
				x = random.randrange(10,width-20)#Random position for the new asteroid
				y = random.randrange(10,height-20)
				if((x < self.player.rect.x - 100 or x > self.player.rect.x + 100) and ( y < self.player.rect.y - 100 or y > self.player.rect.y + 100)):#make sure the new asteroid wont spawn on top of player
					self.asteroid = Asteroid(x,y,width, height,speed)
					self.allasteroids.add(self.asteroid)
					break
	
	
	def fire(self, firing):#if space is down -> fire bullets
		self.rate_of_fire += 1
		if (self.rate_of_fire > 5 and firing and self.player.alive()):
			self.bullet = Bullet(self.player.rect.center, self.player.xVelocity, self.player.yVelocity, self.player.dir,width,height)
			self.allBullets.add(self.bullet)
			self.allsprites.add(self.bullet)
			self.rate_of_fire = 0
			
class Player(pygame.sprite.Sprite):



	def __init__(self,x,y,width,height):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("pelaaja.png").convert()
		self.imageMaster = self.image
		self.rect = self.image.get_rect()
		self.width = width
		self.height = height
		self.xVelocity = 0
		self.yVelocity = 0
		self.xAcceleration = 0
		self.yAcceleration = 0
		self.rect.y = y
		self.rect.x = x
		self.dir = 0
		self.image.set_colorkey((255,255,255))
		self.rotateacc = 0
		self.tmp = 0
		self.acceleration = 0
		self.shieldtime = 0
		self.shieldCD = 0
		self.rad = 0 # radians
		
	#set the rate how fast the sprite rotates		
	def rotatespeed(self, x, testi):
		if (x == 0 and self.tmp == testi):
			self.rotateacc = 0
		elif (x == 0 and self.tmp == testi):
			self.rotateacc = 0
		elif (x != 0):
			self.tmp = testi		#so KEY UP left wont interrupt KEY DOWN RIGHT
			self.rotateacc = fps/10 * x
	
	def check_shield_CD(self):
		tmp = False
		if self.shieldCD == 0:
			tmp = True
		return tmp
		
	def check_shield(self):
		tmp = True
		if self.shieldtime == 0:
			tmp = False
		return tmp	
		
	#set acceleration	
	def accelerate(self,x):
		self.acceleration = x/2;
	
	#resets position and stops the movement
	def resetpos(self):
		self.rect.y = self.height/2
		self.rect.x = self.width/2
		self.xAcceleration = 0
		self.yAcceleration = 0
		self.xVelocity = 0
		self.yVelocity = 0
		
		
		
	def update(self):
		#rotate sprite
		self.rotate()
		#change speed
		self.direction()
		self.changespeed()
		
		#manage shield
		if self.shieldtime > 0:
			self.shieldtime = self.shieldtime-1
		if self.shieldCD > 0:
			self.shieldCD = self.shieldCD-1
		#set the position of the sprite
		self.rect.y += self.yVelocity
		self.rect.x += self.xVelocity
		self.boundarys()
		#debug
		#print(self.rect.x,"   ", self.rect.y,"   dir:",self.dir,"   ",self.acceleration)
	
		#calculates values for acceleration
	def direction(self):
		self.rad = math.pi*self.dir/180
		self.xAcceleration = math.sin(self.rad) * self.acceleration
		self.yAcceleration = math.cos(self.rad) * self.acceleration
		
		
	def changespeed(self):
		#increase/decrease speed
		self.xVelocity += self.xAcceleration
		self.yVelocity += self.yAcceleration
		
		#set max speed
		if self.yVelocity > 7: self.yVelocity = 7
		if self.yVelocity < -7: self.yVelocity = -7
		if self.xVelocity > 7: self.xVelocity = 7
		if self.xVelocity < -7: self.xVelocity = -7
		
		
			
		#rotates the sprite
	def rotate(self):
		self.dir += self.rotateacc
		
		if(self.dir > 360): self.dir = 0
		if(self.dir < 0): self.dir = 360
		oldCenter = self.rect.center
		self.image = pygame.transform.rotate(self.imageMaster, self.dir)
		self.rect = self.image.get_rect()
		self.rect.center = oldCenter
	
	#wont let player to fly off screen
	def boundarys(self):
		if self.rect.x > self.width-50:
			self.rect.x = self.width-50
			self.xAcceleration = 0
			self.xVelocity = 0
		if self.rect.x < 0:
			self.rect.x = 0
			self.xAcceleration = 0
		if self.rect.y > self.height-50:
			self.rect.y = self.height-50
			self.yAcceleration = 0
			self.yVelocity = 0
		if self.rect.y < 0:
			self.rect.y = 0
			self.yAcceleration = 0
		
		#when shield is used, sets cooldown to 900/fps	
	def shield(self):
		self.shieldtime = 150
		self.shieldCD = 900
		
		
class Asteroid(pygame.sprite.Sprite):
	def __init__(self, x, y,width, height, speed = 0):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("asteroid.png").convert()
		self.imageMaster = self.image
		self.rect = self.image.get_rect()
		self.Velocity = random.randint(1+speed,2+speed)#set speed
		self.dir = 0
		self.rotation = random.randint(0,180)
		self.rotation_speed = random.randint(2,2)
		self.rect.center = (x, y)
		self.image = pygame.transform.rotate(self.image, self.dir)
		self.image.set_colorkey((255,255,255))
		self.width = width
		self.height = height
	
	
	def update(self, playerX, playerY):
		self.rotate(playerX, playerY)
		if(self.Velocity < 8):
			self.Velocity += self.Velocity*0.002#slightly increase speed over time
		self.rect.x += self.xVelocity
		self.rect.y += self.yVelocity
		self.boundarys()
		
	def rotate(self, playerX, playerY):
		
		#sets asteroids direction towards player
		self.dir = math.atan2(self.rect.y - playerY, self.rect.x - playerX)*(180/math.pi)-90
		
		#calculates x and y velocity
		rad = math.pi*self.dir/180
		self.xVelocity = math.sin(rad) * self.Velocity
		self.yVelocity = -math.cos(rad) * self.Velocity
		
		#spins the asteroid 
		self.rotation -= self.rotation_speed
		oldCenter = self.rect.center
		self.image = pygame.transform.rotate(self.imageMaster, self.rotation)
		self.rect = self.image.get_rect()
		self.rect.center = oldCenter	
		self.image.set_colorkey((255,255,255))
	
	#wont let asteroids to fly off screen
	def boundarys(self):
		if self.rect.x > self.width-25:
			self.rect.x = self.width-25

		if self.rect.x < 0:
			self.rect.x = 0

		if self.rect.y > self.height-25:
			self.rect.y = self.height-25

		if self.rect.y < 0:
			self.rect.y = 0

class Bullet(pygame.sprite.Sprite):

	def __init__(self,center, xspeed, yspeed, dir, width, height):
		pygame.sprite.Sprite.__init__(self)
		self.width = width
		self.height = height
		self.image = pygame.image.load("pewpew.png").convert()
		self.rect = self.image.get_rect()
		self.dir = dir
		rad = math.pi*self.dir/180#convert degrees to radians
		self.xVelocity = math.sin(rad) * 15#calculate velocity in x and y axis
		self.yVelocity = math.cos(rad) * 15
		self.rect.center = center
		self.image = pygame.transform.rotate(self.image, self.dir)
		self.image.set_colorkey((255,255,255))
	
	def update(self):
		self.rect.y -= self.yVelocity
		self.rect.x -= self.xVelocity
		self.check()
		
		#if bullet exits screen, kill it
	def check(self):
		if self.rect.x > self.width+100: self.kill()
		if self.rect.x < 0: self.kill()
		if self.rect.y > self.height+100: self.kill()
		if self.rect.y < 0: self.kill()
		
class Menu():
	
	def __init__(self, screen, settings,width,height):
		pygame.init()
		self.height = height
		self.width = width
		self.screen = screen
		self.settings = settings
		self.clock = pygame.time.Clock()
		self.items = ("Start game","Settings","Exit")
		self.font = pygame.font.SysFont(None, 36)
		self.white = (255,255,255)
		self.menuloop = True
		
	def drawMenu(self):
		self.menuloop = True
		while self.menuloop:
			self.screen.fill((0,0,0))
			self.clock.tick(50)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit(0)
				if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # 1 = Left button
					self.checkClick(event)

			if pygame.font:
				self.start = self.font.render("Start game" ,2, (255, 255, 225))		##### MUUTA MENU ITEMIT SPRITEIKSI
				self.sets = self.font.render("Settings" ,2, (255, 255, 225))
				self.quit = self.font.render("Quit" ,2, (255, 255, 225))
				posW = (self.width/2)-100
				self.screen.blit(self.start, (posW,200))
				self.screen.blit(self.sets, (posW,300))
				self.screen.blit(self.quit, (posW,400))
				
				
			
			pygame.display.flip()
			
		return
		
	def checkClick(self,event):
		w, h = event.pos
		if w > self.width/2-200 and w < self.width/2:
			if h > 150 and h < 250:
				self.menuloop = False
			if h > 250 and h < 350:
				self.settings.drawSettings()
			if h > 350 and h < 450:
				sys.exit(0)
	
		
"""
TODO

Use sprites for text fields to make it easier to handle. 
"""
class Settings:
	def __init__(self, screen,width,height):
		pygame.init()
		self.width = width
		self.height = height
		self.screen = screen
		self.clock = pygame.time.Clock()
		self.font = pygame.font.SysFont(None, 36)
		self.white = (255,255,255)
		self.settingsloop = True
		self.ammountOfAsteroids = 10;
		self.speed = 0
	
	def drawSettings(self):
		self.settingsloop = True#stay in settings menu until player clicks "Back"
		while self.settingsloop:
			self.screen.fill((0,0,0))
			self.clock.tick(50)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit(0)
				if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # 1 = Left button
					self.settingsloop = self.checkClick(event)
					
			if pygame.font:
				self.asteroids = self.font.render("Number of asteroids %d" %(self.ammountOfAsteroids) ,2, (255, 255, 225))
				self.sets = self.font.render("-                +" ,2, (255, 255, 225))
				self.quit = self.font.render("Back" ,2, (255, 255, 225))
				self.speedtext = self.font.render("Speed of asteroids %d (0=default, if < 0 weird things happen)" %(self.speed) ,2, (255, 255, 225)) 
				self.setspeed = self.font.render("-                +" ,2, (255, 255, 225))
				posW = (self.width / 2)-100
				self.screen.blit(self.asteroids, (posW,200))
				self.screen.blit(self.sets, (posW,300))
				self.screen.blit(self.speedtext, (posW,400))
				self.screen.blit(self.setspeed, (posW,500))
				self.screen.blit(self.quit, (posW,600))
				
				
			pygame.display.flip()
			### Change to sprites, fixed coordinates are meh..
	def checkClick(self,event):
		w, h = event.pos
		tmp = True
		print((self.width / 2)+100)
		if w > (self.width / 2)-200 and w < (self.width / 2)+100:
			if h > 250 and h < 350 and w < (self.width / 2)-50:#- asteroids
				self.ammountOfAsteroids -= 1
			if h > 250 and h < 350 and w > (self.width / 2)-50:#add asteroids
				self.ammountOfAsteroids += 1
			if h > 350 and h < 450:#		speedsettext
				pass
			if h > 450 and h < 550 and w < (self.width / 2)-50:#decrease speed
				self.speed -= 1
			if h > 450 and h < 550 and w > (self.width / 2)-50:#increase speed
				self.speed += 1
			if h > 550 and h < 650:#back
				tmp = False
				
		return tmp
		
	def getSettings(self):
		return self.ammountOfAsteroids
	def getSpeed(self):
		return self.speed			

		
def main():
	game().run()
	
if __name__=="__main__":
	main()
		
	