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


def start():

    pygame.init()
    infoObject = pygame.display.Info()
    pygame.display.set_caption('CPSC 481 Project')

    display_width, display_height = getDisplay(infoObject)
    gameDisplay = pygame.display.set_mode((display_width, display_height))
    display_size = [display_width, display_height]

    # Colors
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)

    # Time-related
    clock = pygame.time.Clock()  # Game clock, in charge of frame rate
    time_elapsed = 0

    draw_mode = False
    first_point = False

    # Car object initialization
    car = Car(gameDisplay, display_size)
    ai_mode = False
    crashed = False

    # AI Handling
    brain = None
    
    # Game Collision Handling
    current_line = []
    lines = []

    checkpoints = []
    create_checkpoint = False
    start_point = []
    end_point = []
    temp_point = []

    collision_points = []
    next_checkpoint = []
    counter = 0

    reset_position = display_width / 2, display_height / 2
    generation_size = 50

    while not crashed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    # Enter Draw Mode
                    draw_mode = not draw_mode
                    if draw_mode:
                        pygame.mouse.set_cursor(*pygame.cursors.broken_x)
                    else:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        first_point = False
                if event.key == pygame.K_b and draw_mode:
                    create_checkpoint = True
                if pygame.key.get_pressed()[pygame.K_b] and pygame.key.get_pressed()[pygame.K_LSHIFT] and lines:
                    if not ai_mode:
                        brain = NeatManager(gameDisplay, display_size, reset_position, generation_size)
                        brain.createGeneration()
                        ai_mode = True
                    else:
                        brain = None
                        ai_mode = False
                        car = Car(gameDisplay, display_size)

                if event.key == pygame.K_c:
                    # Clear lines
                    lines = []
                    collision_points = []
                    checkpoints = []
                    next_checkpoint = []
                if event.key == pygame.K_a:
                    # Retrieve Car Angles
                    print(car.getCarAngle())
                if event.key == pygame.K_s:
                    # Print slope of lines
                    printSlopes(lines)
                if event.key == pygame.K_r:
                    # Reset Car
                    car.reset(reset_position)
                    event.key = pygame.K_l
                    time_elapsed = 0
                if event.key == pygame.K_p:
                    saveTrack(lines, checkpoints, car)
                if event.key == pygame.K_t:
                    car.teleportCar(pygame.mouse.get_pos())
                if event.key == pygame.K_l:
                    reset_position, lines, checkpoints = loadTrack()
                    collision_points = []
                    next_checkpoint = []
                    for line in lines:
                        buildWall(line, collision_points)
                    if reset_position:
                        car.reset(Vector2(reset_position))
                    time_elapsed = 0
                    car.score = 0
                if event.key == pygame.K_q:
                    if temp_point:
                        temp_point.append(pygame.mouse.get_pos())
                        start_point = pygame.Rect(
                            temp_point[0], (temp_point[1][0] - temp_point[0][0], temp_point[1][1] - temp_point[0][1]))
                        temp_point = []
                    else:
                        temp_point.append(pygame.mouse.get_pos())

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if draw mode and if user left clicks
                if draw_mode:
                    if event.button == 1:
                        # Get first point from player
                        if first_point == False:
                            first_point = True
                            current_line.append(
                                Vector2(pygame.mouse.get_pos()))
                            break
                        else:
                            current_line.append(
                                Vector2(pygame.mouse.get_pos()))
                            if current_line[1].x < current_line[0].x:
                                temp = current_line[0]
                                current_line[0] = current_line[1]
                                current_line[1] = temp
                            if current_line[1].x - current_line[0].x < 10:
                                current_line[1].x = current_line[0].x
                            if create_checkpoint:
                                print("Creating new checkpoint")
                                checkpoints.append(current_line)
                            else:
                                lines.append(current_line)
                                buildWall(current_line, collision_points)

                    draw_mode = False
                    create_checkpoint = False
                    first_point = False
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
                    current_line = []

        gameDisplay.fill(white)
        displayTime(gameDisplay, clock, display_size, time_elapsed)
        if not ai_mode:
            displayScore(gameDisplay, display_size, car.score)
        else:
            displayScore(gameDisplay, display_size, max(brain.generation, key=lambda c: Brain.getScore(c)))
        drawTrack(gameDisplay, lines, black)
        drawCheckpoints(gameDisplay, checkpoints)

        if start_point:
            pygame.draw.rect(gameDisplay, red, start_point)

        if draw_mode and current_line:
            pygame.draw.line(
                gameDisplay, black, current_line[0], pygame.mouse.get_pos(), TRACK_WIDTH)
        
        if temp_point:
            rect = pygame.Rect(temp_point[0],
                               pygame.mouse.get_pos()[0] - temp_point[0][0],
                               pygame.mouse.get_pos()[1] - temp_point[0][1])
            pygame.draw.rect(gameDisplay, red, rect)
        
        if ai_mode:
            brain.makeMoves(collision_points, checkpoints, time_elapsed)
        else:
            if not car.crashed:
                car.update(pygame.key.get_pressed(), collision_points,
                       checkpoints, time_elapsed)
        if ai_mode:
            for c in brain.generation:
                c.car.show()
            if brain.all_dead:
                print("Culling")
                brain.cullTheWeak()
                brain.createGeneration()
        else:
            car.show()


        pygame.display.update()
        gameDisplay.fill(white)
        time_elapsed += clock.tick(60)

    pygame.quit()
    quit()


def displayTime(gameDisplay, clock, display, time_elapsed):

    seconds = int(time_elapsed / 1000)
    minutes = int(seconds / 60)
    if seconds >= 60:
        seconds = int(seconds % 60)

    text_to_display = "Time:{:02d}:{:02d}".format(minutes, seconds)
    time_font = pygame.font.SysFont('consolas', int(display[1] / 20))
    time = time_font.render(text_to_display, 1, (0, 0, 0))
    gameDisplay.blit(
        time, (display[0] - time_font.size(text_to_display)[0], 0))


def displayScore(gameDisplay, display, score):

    text_to_display = "Score: {}".format(score)
    score_font = pygame.font.SysFont('consolas', int(display[1] / 20))
    score = score_font.render(text_to_display, 1, (0, 0, 0))
    gameDisplay.blit(score, (display[0] - score_font.size(text_to_display)[
                     0], display[1] - score_font.size(text_to_display)[1]))


def getDisplay(pygameInfo):
    return 1280, 720


def drawTrack(display, lines, black):
    for line in lines:
        pygame.draw.line(display, black, line[0], line[1], TRACK_WIDTH)


def printSlopes(lines):
    for line in lines:
        print((line[1].y - line[0].y) / (line[1].x - line[0].x))


def drawCheckpoints(display, checkpoints):
    color = (0, 0, 255)
    for c in range(len(checkpoints)):
        pygame.draw.line(display, color, checkpoints[c][0], checkpoints[c][1], TRACK_WIDTH)


def buildWall(line, collisionPoints):
    collisionPoints.append(Line(Vector2(line[0]), Vector2(line[1])))


def saveTrack(lines, checkpoints, car):
    print("save Track")
    with open("./trackFile.csv", "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=',', lineterminator='\r')
        for line in lines:
            writer.writerow(
                ("Wall: ", line[0].x, line[0].y, line[1].x, line[1].y))
        for c in checkpoints:
            writer.writerow(("Checkpoint: ", c[0].x, c[0].y, c[1].x, c[1].y))
        writer.writerow(
            ("Starting Position: ", car.getCarPos()[0], car.getCarPos()[1]))


def loadTrack():
    car_pos = None
    with open("./trackFile.csv",'rU') as csv_file:
        writer = csv.reader(csv_file, delimiter=',', lineterminator='\r')
        current_line = []
        lines = []
        checkpoints = []
        for row in writer:
            if "Position" in row[0]:
                car_pos = Vector2(float(row[1]), float(row[2]))
            else:
                current_line.append(Vector2(float(row[1]), float(row[2])))
                current_line.append(Vector2(float(row[3]), float(row[4])))

                if "Wall" in row[0]:
                    lines.append(current_line)
                if "Che" in row[0]:
                    checkpoints.append(current_line)
                current_line = []

        return car_pos, lines, checkpoints
