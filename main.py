from Game import Game
from Brain import NeatManager
import neat
import pickle

start = Game()
start.initiateBrain()

config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
							neat.DefaultSpeciesSet, neat.DefaultStagnation,
							start.brain.config_file)

manager = neat.Population(config)
manager.add_reporter(neat.StdOutReporter(True))


def eval_genomes(genome, config):
	start.brain.createGeneration(genome=genome, config=config)
	start.run_game(ai_track=True)
	start.brain.time_allowed = min(45000, start.brain.time_allowed + 3000)
winner = manager.run(eval_genomes,100)

pickle.dump(winner, open("best.pickle","wb"))


start.quit()