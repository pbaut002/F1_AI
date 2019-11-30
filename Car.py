import pygame
import numpy
from math import tan, radians, degrees, copysign, ceil, sqrt, sin, cos, floor
from pygame import Vector2
from Line import Line


class Car():

    def __init__(self, game, display, brain=None):
        self.score = 0
        self.time_alive = 0
        self.name = None
        # Car Attributes
        self.car_length = int(ceil(display[0] * 47 / 1120))
        self.car_width = int(ceil(display[1] * 13 / 480))
        carImg = pygame.image.load('renault.png')
        self.carImg = pygame.transform.scale(
            carImg, (self.car_width, self.car_length))
        self.red = (255, 0, 0)
        self.display = display

        # Starting position
        x = (display[0] * 0.45)
        y = (display[1] * 0.8)

        # PyGame instance
        self.game = game
        self.game.blit(self.carImg, (x, y))

        # Max acceleration, velocity and friction
        self.max_acceleration = .9
        self.max_braking_power = .4
        if display[0] < 800:
            self.max_velocity = 15  # 3.5 Temp
        else:
            self.max_velocity = 5
        self.friction = .04

        # Car position and velocity
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.angular_velocity = 0
        self.crashed = False

        # Steering
        self.steering = 0
        self.angle = .15
        self.length = self.car_length
        self.max_steering = 40

        self.rotated = pygame.transform.rotate(self.carImg, self.angle)
        self.car_rect = self.rotated.get_rect(center=(self.getCarPos(
        ).x + self.car_width / 2, self.getCarPos().y + self.car_length / 2))

        self.player_control = True
        self.checkpoints = None
        self.next_checkpoint = None
        self.time = None
        self.prev_pos = None
        # print(self.car_rect.topleft)
        # print(self.car_rect.topright)
        # print(self.car_rect.bottomleft)
        # print(self.car_rect.bottomright)

    def check_border(self):

        if self.position.x < 0:
            self.position.x = 0
            self.velocity.update(0, 0)
            return True
        if self.position.x > self.display[0] - self.car_length:
            self.position.x = self.display[0] - self.car_length
            self.velocity.update(0, 0)
            return True
        if self.position.y < 0:
            self.position.y = 0
            self.velocity.update(0, 0)
            return True
        if self.position.y > self.display[1] - self.car_length:
            self.position.y = self.display[1] - self.car_length
            self.velocity.update(0, 0)
            return True

    def collide(self, points, collisionPoints):
        return collisionPoints.get('{0}:{1}'.format(round(points[0]), round(points[1])))

    def getline(self, p1, p2):
        slope = (p[1].y - p[0].y) / (p[1].x - p[0].x)
        intercept = round(p[1].y - (slope * p[1].x))
        return

    def checkCorners(self):
        if (270 < self.angle < 360) or (90 < self.angle < 180):
            return [self.car_rect.topright, self.car_rect.bottomleft,
                    self.car_rect.midtop, self.car_rect.midleft,
                    ]
        if (0 < self.angle < 90) or (180 < self.angle < 270):
            return [self.car_rect.topleft, self.car_rect.bottomright,
                    self.car_rect.midtop, self.car_rect.midleft,
                    ]
        else:
            return [self.car_rect.midtop, self.car_rect.midbottom, self.car_rect.midright, self.car_rect.midleft]

    def checkCollision(self, collisionPoints):
        # get slope intercept formula for each line and plug in car_pos

        if self.check_border():
            return True

        def distance(p1, p2):
            return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

        # Use line intersection formula
        car_points = self.checkCorners()
        current_line = Line(Vector2(car_points[0]), Vector2(car_points[1]))
        current_line2 = Line(Vector2(car_points[2]), Vector2(car_points[3]))
        
        car_points = current_line.points_on_line()
        car_points.extend(current_line2.points_on_line())


        current_collision_points = []
        for line in collisionPoints:
            collision_point = []
            if current_line.intersect(line) != None:
                collision_point.append(current_line.intersect(line))
            if current_line2.intersect(line) != None:
                collision_point.append(current_line2.intersect(line))
            if len(collision_point) > 0:
                for p in collision_point:
                    if distance(p, self.position) <= 150:
                        current_collision_points.append(p)

        if current_collision_points:
            for collision_point in current_collision_points:
                for p in car_points:
                    # print("Car Point: {0} Collision: {1}".format(p, collision_point))
                    if self.velocity.magnitude() > 0 and distance(p, collision_point) / (self.velocity.magnitude()) < .3:
                        return True

    def teleportCar(self, position):
        self.position.update(position)

    def getScore(self, time):
        def distance(p1, p2):
            return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        if self.crashed:
            return (self.score/11)*10 - 20
        else:
            return (self.score/11)*10

    def getCarAngle(self):
        return self.angle

    def getCarPos(self):
        return Vector2(self.position)

    def getCarLines(self):
        return [[self.car_rect.topright, self.car_rect.bottomleft],
                [self.car_rect.topleft, self.car_rect.bottomright],
                [self.car_rect.midleft, self.car_rect.midright],
                [self.car_rect.midtop, self.car_rect.midbottom+Vector2(1.0,1.0)],
                ]

    def reset(self, position):
        self.crashed = False
        self.position.update(position)
        self.angle = 0
        self.score = 0
        self.checkpoints = None

    def update(self, direction, collisionPoints, checkpoints, time):
        if self.checkpoints == None:
            self.checkpoints = checkpoints.copy()
        if direction[pygame.K_LEFT]:
            self.steering -= 5
        elif direction[pygame.K_RIGHT]:
            self.steering += 5
        else:
            self.steering = 0

        self.steering = max(-self.max_steering,
                            min(self.steering, self.max_steering))
        # Car velocity update.
        # Up to accelerate. Down to reverse/brake
        if self.crashed == False:
            if direction[pygame.K_UP]:
                self.velocity.y = max(-self.max_velocity, (self.velocity.y +
                                                           min(self.acceleration.y - .09, self.max_acceleration)))
            if direction[pygame.K_DOWN] and self.velocity.y != 0:
                self.velocity.y = min(self.max_velocity, self.velocity.y +
                                      min(self.acceleration.y + .09, self.max_braking_power))
        # Handle steering
        if self.steering:
            turning_radius = self.car_length / tan(radians(self.steering))
            self.angular_velocity = self.velocity.y / turning_radius
        else:
            self.angular_velocity = 0

        # If there is a velocity, then apply friction to it
        if self.velocity.y != 0:
            self.velocity.y += -copysign(self.friction, self.velocity.y)
            if abs(self.velocity.y) < 0.03:
                self.velocity.y = 0

        original_pos = self.position

        # Once velocity and angle of car has been calculated,
        # update position and angle
        self.position += self.velocity.rotate(-self.angle)

        if self.checkCollision(collisionPoints):
            self.position.update(original_pos)
            self.velocity.update(0, 0)
            self.crashed = True
            self.score = round(self.score + (1/time) * 1000,2)
            self.checkpoints = None

        if self.checkpoints:
            self.next_checkpoint = [Line(self.checkpoints[0][0], self.checkpoints[0][1])]
            if self.checkCollision(self.next_checkpoint):
                self.checkpoints.pop(0)
                self.score += 1
                self.next_checkpoint.pop(0)
        
        self.angle = self.angle % 360
        self.angle += degrees(self.angular_velocity)

        self.rotated = pygame.transform.rotozoom(self.carImg, self.angle, 1)
        self.car_rect = self.rotated.get_rect(center=((self.getCarPos().x + self.car_length / 2) - self.rotated.get_rect().width / 2,
                                                      self.getCarPos().y + self.rotated.get_rect().height / 2))
        # print("X: {0}, Y: {1}".format(self.position.x,self.position.y))

    def show(self):
        self.game.blit(self.rotated, self.car_rect)
