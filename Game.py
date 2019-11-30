import pygame
import math
import csv
from pygame import Vector2
from Car import Car
from math import floor, ceil
from Line import Line
from Brain import Brain
from Brain import NeatManager

TRACK_WIDTH = 10


class Game():

	def __init__(self):
		pygame.init()
		self.infoObject = pygame.display.Info()
		pygame.display.set_caption('CPSC 481 Project')

		self.display_width, self.display_height = self.getDisplay(self.infoObject)
		self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))
		self.display_size = [self.display_width, self.display_height]

		# Colors
		self.black = (0, 0, 0)
		self.white = (255, 255, 255)
		self.red = (255, 0, 0)

		# Time-related
		self.clock = pygame.time.Clock()  # Game self.clock, in charge of frame rate

		self.draw_mode = False
		self.first_point = False

		# Car object initialization
		self.car = Car(self.gameDisplay, self.display_size)
		self.ai_mode = False
		self.crashed = False

		# AI Handling
		self.brain = None
		
		# Game Collision Handling
		self.current_line = []
		self.lines = []

		self.checkpoints = []
		self.create_checkpoint = False
		self.start_point = []
		self.end_point = []
		self.temp_point = []

		self.collision_points = []
		self.next_checkpoint = []
		self.counter = 0

		self.generation_size = 50
		self.reset_position = self.display_width / 2, self.display_height / 2
		self.angle = 0


	def run_game(self,ai_track=None):
		time_elapsed = 0

		for c in self.brain.generation:
			c.car.time = time_elapsed
			c.car.prev_pos = c.car.getCarPos()
		while not self.crashed and self.brain.all_dead == False:
			for event in pygame.event.get():
				if(ai_track):
					event = pygame.event.Event(pygame.KEYDOWN)
					event.key = pygame.K_l
				if event.type == pygame.QUIT:
					self.crashed = True
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_d:
						# Enter Draw Mode
						self.draw_mode = not self.draw_mode
						if self.draw_mode:
							pygame.mouse.set_cursor(*pygame.cursors.broken_x)
						else:
							pygame.mouse.set_cursor(*pygame.cursors.arrow)
							first_point = False
					if event.key == pygame.K_b and self.draw_mode:
						self.create_checkpoint = True
					if (pygame.key.get_pressed()[pygame.K_b] and pygame.key.get_pressed()[pygame.K_LSHIFT] and self.lines):
						if not self.ai_mode:
							self.brain = NeatManager(self.gameDisplay, self.display_size, self.reset_position, self.generation_size)
							self.brain.createGeneration()
							self.ai_mode = True
						else:
							self.brain = None
							self.ai_mode = False
							self.car = Car(self.gameDisplay, self.display_size)

					if event.key == pygame.K_c:
						# Clear self.lines
						self.lines = []
						self.collision_points = []
						self.checkpoints = []
						self.next_checkpoint = []
					if event.key == pygame.K_a:
						# Retrieve Car Angles
						print(self.car.getCarAngle())
					if event.key == pygame.K_s:
						# Print slope of self.lines
						self.printSlopes(self.lines)
					if event.key == pygame.K_r:
						# Reset Car
						self.car.reset(self.reset_position)
						event.key = pygame.K_l
						time_elapsed = 0
					if event.key == pygame.K_p:
						self.saveTrack(self.lines, self.checkpoints, self.car)
					if event.key == pygame.K_t:
						self.car.teleportCar(pygame.mouse.get_pos())
					if ai_track == True or event.key == pygame.K_l:
						self.reset_position, self.lines, self.checkpoints = self.loadTrack()
						if self.brain:
							self.brain.start_position = self.reset_position
						self.collision_points = []
						self.next_checkpoint = []
						for line in self.lines:
							self.buildWall(line, self.collision_points)
						if self.reset_position:
							self.car.reset(Vector2(self.reset_position))
							self.car.angle = self.angle
						self.time_elapsed = 0
						self.car.score = 0
					if event.key == pygame.K_q:
						if self.temp_point:
							self.temp_point.append(pygame.mouse.get_pos())
							self.start_point = pygame.Rect(
								self.temp_point[0], (self.temp_point[1][0] - self.temp_point[0][0], self.temp_point[1][1] - self.temp_point[0][1]))
							self.temp_point = []
						else:
							self.temp_point.append(pygame.mouse.get_pos())

				if event.type == pygame.MOUSEBUTTONDOWN:
					# Check if draw mode and if user left clicks
					if self.draw_mode:
						if event.button == 1:
							# Get first point from player
							if self.first_point == False:
								self.first_point = True
								self.current_line.append(
									Vector2(pygame.mouse.get_pos()))
								break
							else:
								self.current_line.append(
									Vector2(pygame.mouse.get_pos()))
								if self.current_line[1].x < self.current_line[0].x:
									temp = self.current_line[0]
									self.current_line[0] = self.current_line[1]
									self.current_line[1] = temp
								if self.current_line[1].x - self.current_line[0].x < 10:
									self.current_line[1].x = self.current_line[0].x
								if self.create_checkpoint:
									print("Creating new checkpoint")
									self.checkpoints.append(self.current_line)
								else:
									self.lines.append(self.current_line)
									self.buildWall(self.current_line, self.collision_points)

						self.draw_mode = False
						self.create_checkpoint = False
						self.first_point = False
						pygame.mouse.set_cursor(*pygame.cursors.arrow)
						self.current_line = []
				if ai_track:
					for c in self.brain.generation:
						c.car.position.update(self.reset_position)
				ai_track = False

			self.gameDisplay.fill(self.white)
			self.displayTime(self.gameDisplay, self.clock, self.display_size, time_elapsed)
			
			# Move based on if the game is in AI Mode
			if not self.ai_mode:
				self.displayScore(self.gameDisplay, self.display_size, self.car.score)
			else:
				if time_elapsed > 0:
					if len(self.brain.generation) > 0: 
						self.displayScore(self.gameDisplay, self.display_size, max(self.brain.generation, key=lambda c: Brain.getScore(c,time_elapsed)))
			
			# Draw the tracks and checkpoints
			self.drawTrack(self.gameDisplay, self.lines, self.black)
			self.drawCheckpoints(self.gameDisplay, self.checkpoints)

			if self.start_point:
				pygame.draw.rect(self.gameDisplay, self.red, self.start_point)

			if self.draw_mode and self.current_line:
				pygame.draw.line(
					self.gameDisplay, self.black, self.current_line[0], pygame.mouse.get_pos(), TRACK_WIDTH)
			
			if self.temp_point:
				rect = pygame.Rect(self.temp_point[0],
								   pygame.mouse.get_pos()[0] - self.temp_point[0][0],
								   pygame.mouse.get_pos()[1] - self.temp_point[0][1])
				pygame.draw.rect(self.gameDisplay, self.red, rect)
			
			if self.ai_mode:
				self.brain.makeMoves(self.collision_points, self.checkpoints, time_elapsed)
			else:
				if not self.car.crashed:
					self.car.update(pygame.key.get_pressed(), self.collision_points,
						   self.checkpoints, time_elapsed)
			if self.ai_mode:
				for c in self.brain.generation:
					c.car.show()
				if self.brain.all_dead:
					print("Culling")
					self.brain.cullTheWeak()
			else:
				self.car.show()


			pygame.display.update()
			self.gameDisplay.fill(self.white)
			time_elapsed += self.clock.tick(120)
			
	
	def quit(self):
		pygame.quit()
		quit()

	def displayTime(self,gameDisplay, clock, display, time_elapsed):

		seconds = int(time_elapsed / 1000)
		minutes = int(seconds / 60)
		if seconds >= 60:
			seconds = int(seconds % 60)

		text_to_display = "Time:{:02d}:{:02d}".format(minutes, seconds)
		time_font = pygame.font.SysFont('consolas', int(display[1] / 20))
		time = time_font.render(text_to_display, 1, (0, 0, 0))
		self.gameDisplay.blit(
			time, (display[0] - time_font.size(text_to_display)[0], 0))


	def displayScore(self,gameDisplay, display, score):
		text_to_display = "Score: {}".format(score)
		score_font = pygame.font.SysFont('consolas', int(display[1] / 20))
		score = score_font.render(text_to_display, 1, (0, 0, 0))
		self.gameDisplay.blit(score, (display[0] - score_font.size(text_to_display)[
						 0], display[1] - score_font.size(text_to_display)[1]))


	def getDisplay(self,pygameInfo):
		return 1280, 720


	def drawTrack(self,display,lines, black):
		for line in self.lines:
			pygame.draw.line(display, black, line[0], line[1], TRACK_WIDTH)


	def printSlopes(self,lines):
		for line in self.lines:
			print((line[1].y - line[0].y) / (line[1].x - line[0].x))


	def drawCheckpoints(self, display,checkpoints):
		color = (0, 0, 255)
		for c in range(len(self.checkpoints)):
			pygame.draw.line(display, color, self.checkpoints[c][0], self.checkpoints[c][1], TRACK_WIDTH)


	def buildWall(self,line, collisionPoints):
		collisionPoints.append(Line(Vector2(line[0]), Vector2(line[1])))


	def saveTrack(self,lines, checkpoints,car):
		print("save Track")
		with open("./trackFile.csv", "w") as csv_file:
			writer = csv.writer(csv_file, delimiter=',', lineterminator='\r')
			for line in lines:
				writer.writerow(
					("Wall: ", line[0].x, line[0].y, line[1].x, line[1].y))
			for c in checkpoints:
				writer.writerow(("Checkpoint: ", c[0].x, c[0].y, c[1].x, c[1].y))
			writer.writerow(
				("Starting Position: ", car.getCarPos()[0], car.getCarPos()[1],car.angle))


	def loadTrack(self,):
		self.car_pos = None
		with open("./trackFile.csv",'rU') as csv_file:
			writer = csv.reader(csv_file, delimiter=',', lineterminator='\r')
			self.current_line = []
			self.lines = []
			self.checkpoints = []
			for row in writer:
				if "Position" in row[0]:
					self.car_pos = Vector2(float(row[1]), float(row[2]))
					self.angle = float(row[3])
				else:
					self.current_line.append(Vector2(float(row[1]), float(row[2])))
					self.current_line.append(Vector2(float(row[3]), float(row[4])))

					if "Wall" in row[0]:
						self.lines.append(self.current_line)
					if "Che" in row[0]:
						self.checkpoints.append(self.current_line)
					self.current_line = []

			return self.car_pos, self.lines, self.checkpoints


	def initiateBrain(self):
		self.brain = NeatManager(self.gameDisplay, self.display_size, self.reset_position, self.generation_size)
		self.ai_mode = True