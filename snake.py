import pygame
import random
import numpy as np

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 480

BLOCK = 30
TITLE = 'Snakes'

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 100)

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()


class Snakes:
	def __init__(self, FPS=None):
		self.max_width = int(WINDOW_WIDTH/BLOCK)
		self.max_height = int(WINDOW_HEIGHT/BLOCK)
		self.observation_space = self.max_height * self.max_width
		self.action_space = (0, 1, 2, 3)
		self.state = np.zeros((self.max_height, self.max_width), dtype=np.float16)
		self.FPS = FPS


	#reinitializes the game 
	def reset(self):
		self.done = False
		self.score = 0

		#initial possitions
		self.headX = 10
		self.headY = 10
		self.bodyX = [9, 8, 7]
		self.bodyY = [10, 10, 10]

		#prev head pos
		self.tempX = self.headX
		self.tempY = self.headY

		#0 = up, 1 = left, 2 = bottom, 3 = right
		self.direction = 3
		#initial randoom food postion
		self.foodX, self.foodY = self._randomFood()

		self.distance = 999
		return self._getState()


	#draws snake body block/ food
	def _drawBlock(self, x, y, color = WHITE):
		rect = pygame.Rect(x * BLOCK, y * BLOCK, BLOCK, BLOCK)
		#draw snake
		if (color == WHITE):
			pygame.draw.rect(screen, color, rect)
		#draw food
		else:
			pygame.draw.ellipse(screen, color, rect)


	def render(self):

		#draw food 
		self._drawBlock(self.foodX, self.foodY, YELLOW)

		#draw head
		self._drawBlock(self.headX, self.headY)

		#draw body
		for x,y in zip(self.bodyX, self.bodyY):
			self._drawBlock(x, y)

		pygame.display.flip()
		screen.fill(BLACK)
		if self.FPS:
			clock.tick(self.FPS)


	def move(self, action):
		#doen't allow movement in reverse direction
		if action == 0 and (self.headY != self.bodyY[0]+1): 
			self.direction = 0

		elif action == 1 and (self.headX != self.bodyX[0]+1): 
			self.direction = 1

		elif action == 2 and (self.headY != self.bodyY[0]-1): 
			self.direction = 2

		elif action == 3 and (self.headX != self.bodyX[0]-1): 
			self.direction = 3

		#if no new valid action, repeat earlier action
		if self.direction == 0:
			self.headY -= 1
		elif self.direction == 1:
			self.headX -= 1
		elif self.direction == 2:
			self.headY += 1
		elif self.direction == 3:
			self.headX += 1


	def _detectCollisions(self):
		#collides with boundries
		if (self.headX == -1 or self.headY == -1 or self.headX == self.max_width or self.headY == self.max_height):
			return True

		#collides with itself
		if (self.headX, self.headY) in zip(self.bodyX, self.bodyY):
			return True

		return False


	def _eatFood(self):
		#checks if snake head has the same loc as food
		if self.headX == self.foodX and self.headY == self.foodY:
			#incrementing body length
			self.bodyX.insert(0, self.tempX)
			self.bodyY.insert(0, self.tempY)
			self.headX = self.foodX
			self.headY = self.foodY
			#new random food
			self.foodX, self.foodY = self._randomFood()

			self.score += 1
			return True
		return False


	def _updatePos(self):
		n = len(self.bodyX)
		for i in range(n-2, -1, -1):
			self.bodyX[i+1] = self.bodyX[i]	
			self.bodyY[i+1] = self.bodyY[i]

		self.bodyX[0] = self.tempX
		self.bodyY[0] = self.tempY


	def print(self):
		print('h ', self.headX, self.headY)
		print('t ', self.tempX, self.tempY)

		for i in range(len(self.bodyX)):
			print('b ', self.bodyX[i], self.bodyY[i])
		print()


	#generate food in new random location
	def _randomFood(self):
		allowedX = set(range(0, int(WINDOW_WIDTH/BLOCK))) - set([self.headX]) - set(self.bodyX)
		allowedY = set(range(0, int(WINDOW_HEIGHT/BLOCK))) -set([self.headY]) - set(self.bodyY)
		return random.choice(list(allowedX)), random.choice(list(allowedY))


	#get next game state
	def _getState(self):
		if self.done:
			return self.state

		self.state.fill(0)
		for x,y in zip(self.bodyX, self.bodyY):
			self.state[y][x] = 1

		self.state[self.headY][self.headX] = 2
		self.state[self.foodY][self.foodX] = 3
		return self.state.flatten()


	def _calcReward(self):
		if self.done:
			return -1

		if self.eat:
			return 1
		
		distance = abs(self.headX - self.foodX) + abs(self.headY - self.foodY)
		if distance	<= self.distance:
			self.distance = distance
			return 1/(self.distance + 1)

		return 0


	def step(self, action):
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT:
				self.close()

		self.move(action)

		self.eat = False
		if self._eatFood():
			self.eat = True
		else:
			self._updatePos()

		if self._detectCollisions():
			self.done = True

		self.tempX = self.headX
		self.tempY = self.headY

		self.render()
		return self._getState(), self._calcReward(), self.done, self.score


	def close(self):
		pygame.quit()
		exit(0)


# Comment the below code
env = Snakes(60)
env.reset()
reward = 0
for _ in range(1000):
	env.render()
	state, reward, done, score = env.step(random.randint(0,3))
	print('Reward:', reward)
	if done:
		env.reset()