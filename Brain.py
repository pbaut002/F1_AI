import numpy as np
import pygame
import random as rand
import neat 
import os
import copy

from collections import namedtuple, OrderedDict
from pygame import Vector2
from Car import Car
from Line import Line
from math import sqrt, ceil, floor

class NeatManager():
	def __init__(self, gd, size, start_position, number):
		self.generation = []
		self.gameDisplay = gd
		self.displaySize = size
		self.number_dead = 0
		self.all_dead = False
		self.start_position = start_position
		self.generation_size = number
		self.generation_number = 0
		self.nets = []
		self.ge = []
		self.angle = 0
		local_dir = os.path.dirname(__file__)
		config_path = os.path.join(local_dir, 'neat_config.txt')
		self.config_file = config_path

	def createGeneration(self,angle, genome=None,config=None):
		# print("Generation: ", self.generation_number)
		# 
		def mutate(moves):
			mutate_rate = .2
			mutat = 0
			for i in range(len(moves)):
				rand_ = rand.random()
				if rand_ < mutate_rate:
					moves[i] = rand.randint(0,2)
					mutat += 1
			print("Number of moves: ",len(moves),"Mutated Moves: ", mutat)
			return moves
		self.all_dead = False
		self.number_dead = 0
		generation = []

		self.angle = angle

		while(len(generation) < self.generation_size):
			if rand.random() < .1 or len(self.generation) == 0:
				br = Brain(Car(self.gameDisplay, self.displaySize))
				br.car.angle = angle
				br.car.position.update(self.start_position)
				generation.append(br)
			elif len(generation) > 2:
				br = Brain(Car(self.gameDisplay, self.displaySize))
				br.car.angle = angle
				br.car.position.update(self.start_position)
				br.move_list = mutate(self.generation[rand.randint(0,1)].move_list)
				generation.append(br)
			else:
				br = Brain(Car(self.gameDisplay, self.displaySize))
				br.car.angle = angle
				br.car.position.update(self.start_position)
				br.move_list = self.generation[rand.randint(0,1)].move_list
				generation.append(br)

		self.generation = generation

	def makeMoves(self, walls, checkpoints,time):
		def distance(p1, p2):
			return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
		if self.number_dead >= len(self.generation):
			return
		i = 0
		for c in self.generation:
			if not c.car.crashed:
				move = c.move(time,walls=walls,checkpoints=checkpoints)
				if move:
					c.car.update(move, walls,
						   checkpoints,time)
				if time - c.car.time > 1500 and distance(c.car.prev_pos, c.car.getCarPos()) < 125:
					c.car.crashed = True
					c.fitness -= 1000
				if c.car.crashed:
					self.number_dead += 1
					c.fitness = c.car.getScore(time)
				if c.car.prev_pos != c.car.getCarPos():
					c.car.prev_pos = c.car.getCarPos()
					c.car.time = time
				i+=1

		if self.number_dead >= len(self.generation):
			# print("Everyone dead boy")
			self.all_dead = True
			self.cullTheWeak()



	def cullTheWeak(self):
		self.generation_number += 1
		# for c in self.generation:
		#     # print(c.car.score)
		self.number_dead = 0
		
		def getCar(c):
			return c.fitness
		self.generation.sort(key=getCar,reverse=True)
		
		self.generation = self.generation[:2]
		for c in self.generation:
			c.move_index=0



class Brain():

	def __init__(self, car, brain_file=None,):
		self.car = car
		self.neural_network = None
		self.move_dict = {pygame.K_LEFT:False, pygame.K_UP:False, pygame.K_DOWN: False, pygame.K_RIGHT: False}
		self.move_labels = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP]
		self.genome = None 
		self.ge = None
		self.move_list = []
		self.move_index = 0
		self.fitness = 0
		
	def __repr__(self):
		return str(self.car.score)

	def setGenomeNet(self,genome, nn):
		self.neural_network = nn
		self.genome = genome

	def reset_available(self):
		self.move_dict = {pygame.K_LEFT:False, pygame.K_UP:False, pygame.K_DOWN: False, pygame.K_RIGHT: False}

	def availableMoves(self, choice):
		if choice == 1:
			return {pygame.K_LEFT:True, pygame.K_UP:True, pygame.K_DOWN: False, pygame.K_RIGHT: False}
		elif choice == 2:
			return {pygame.K_LEFT:False, pygame.K_UP:True, pygame.K_DOWN: False, pygame.K_RIGHT: True}
		elif choice == 0:
			return {pygame.K_LEFT:False, pygame.K_UP:True, pygame.K_DOWN: False, pygame.K_RIGHT: False}
		elif choice == 3:
			return {pygame.K_LEFT:False, pygame.K_UP:False, pygame.K_DOWN: True, pygame.K_RIGHT: False}

	def createAgent(self):
		pass

	def getScore(self,time):
		return self.car.getScore(time)

	def move(self, time, walls=None, checkpoints=None):

		try:
			choice = self.move_list[self.move_index]
			self.move_index += 1
		except:
			choice = self.move_list.append(rand.randint(0,2))

		return self.availableMoves(choice)
		
		# def distance(p1,p2):
		# 	return sqrt((p1[0]-p2[0])**2 + 	(p1[1]-p2[1])**2)			
		# # Load wall positions and checkpoints
		# collision_points = self.see(walls)
		
		# network_input = []
		# for c in collision_points:
		# 	dist = distance(c,[self.car.position.x, self.car.position.y])
		# 	network_input.append(dist)		
		# while(len(network_input) < 15):
		# 	network_input.append(-5)
		
		# output = 0
		# if collision_points:
		# 	output = self.neural_network.activate(network_input)
		# 	output = output.index(max(output))
		
		# if not self.car.crashed:
		# 	return self.availableMoves(output)


	def checkStatus(self):
		if self.car.crashed:
			print("IM A BAD BOI :C")

	def see(self, walls, checkpoint=False):
		def distance(p1, p2):
			return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

		car_points = self.car.getCarLines()
		closest_points = []

		# Look at the walls/checkpoints and see the point where the car and the wall collide
		for point in car_points:
			line = Line(Vector2(point[0]), Vector2(point[1]))
			for w in walls:
				col_point = line.intersect(w)
				if col_point and distance(self.car.position, col_point) < 125:
					if checkpoint:
						# Draw the checkpoints as a red dot
						pygame.draw.circle(self.car.game, (0, 255, 0), col_point, 5)

					else:
						# Draw the checkpoints as a green dot
						# pygame.draw.circle(self.car.game, (255, 0, 0), col_point, 5)
						pygame.draw.line(self.car.game,(255,0,0) ,point[0],col_point,4)
						closest_points.append((col_point.x, col_point.y))

		return closest_points
