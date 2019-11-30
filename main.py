from Game import Game
from Brain import NeatManager
import neat
import pickle

start = Game()

start.initiateBrain()
start.loadTrack()
while(True):
	start.brain.createGeneration(start.angle)
	start.run_game(ai_track=True)
# config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
# 							neat.DefaultSpeciesSet, neat.DefaultStagnation,
# 							start.brain.config_file)

# manager = neat.Population(config)
# manager.add_reporter(neat.StdOutReporter(True))
# start.loadTrack()
# def eval_genomes(genome, config):
# 	start.brain.createGeneration(start.angle, genome=genome, config=config)
# 	start.run_game(ai_track=True)

# winner = manager.run(eval_genomes,15000)

# pickle.dump(winner, open("best.pickle","wb"))

start.quit()