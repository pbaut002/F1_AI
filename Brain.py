import tensorflow as tf
import numpy as np
import pygame
import random as rand
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten, Conv2D
from tensorflow.keras.optimizers import Adam
from pygame import Vector2
from Line import Line
from math import sqrt


class Brain():

    def __init__(self, car, brain_file=None,):
        self.score = 0
        self.car = car
        self.neural_network = None
        self.move_dict = {pygame.K_LEFT:False, pygame.K_UP:False, pygame.K_DOWN: False, pygame.K_RIGHT: False}
        self.move_labels = [pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT]
        self.move_list = tf.convert_to_tensor([[1, 2,
                                               3,4]])
        print("BRAIN INITIALIZED BEEP BOOP")

    def reset_available(self):
        self.move_dict = {pygame.K_LEFT:False, pygame.K_UP:False, pygame.K_DOWN: False, pygame.K_RIGHT: False}

    def createAgent(self):
        model = Sequential()
        # model.add(Conv2D(100, (5,5), input_shape=(30,4)))##PLACEHOLDER))
        model.add(Dense(4,input_shape=(4,)))
        model.add(Dense(2, activation='relu'))
        model.add(Dense(4, activation='relu'))
        model.compile(loss="mse", optimizer=Adam(lr=0.001), metrics=['accuracy'])
        self.neural_network = model
        test_input = tf.convert_to_tensor([[1.0,2.0,3.0,4.0]])

        self.neural_network.evaluate(test_input, np.array(self.move_list))

    def move(self, walls=None, checkpoints=None):
        
        self.reset_available()
        # Look at Car position
        car_position = self.car.position
        
        # Load wall positions and checkpoints
        collision_points = self.see(walls)
        next_checkpoint = self.see([Line(checkpoints[0][0], checkpoints[0][1])], checkpoint=True)
        print(collision_points, next_checkpoint)
        # # Convert the inputs into some sort of tensor
        test_input = tf.convert_to_tensor(([[rand.randrange(12.0),rand.randrange(12.0),rand.randrange(12.0),rand.randrange(12.0)]]))
       
        # # Create a prediction
        prediction = self.neural_network.predict(test_input)
        self.move_dict[self.move_labels[np.argmax(prediction)]] = True
        return self.move_dict

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
                if col_point and (checkpoint or distance(self.car.position, col_point) < 150):
                    if checkpoint:
                        # Draw the checkpoints as a red dot
                        pygame.draw.circle(self.car.game, (0, 255, 0), col_point, 5)
                    else:
                        # Draw the checkpoints as a green dot
                        pygame.draw.circle(self.car.game, (255, 0, 0), col_point, 5)
                    closest_points.append((col_point.x, col_point.y))
        return closest_points
