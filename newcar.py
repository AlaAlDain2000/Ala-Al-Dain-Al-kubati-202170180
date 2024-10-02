# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)

import math #access to mathematical functions.
import random #used to generate random numbers.
import sys #providing access to system-specific parameters and functions, used to exit the program
import os #interacting with the operating system

import neat #NEAT (NeuroEvolution of Augmenting Topologies) is a library used for evolving artificial neural networks using a genetic algorithm
import pygame #Pygame is a cross-platform library used for developing video games and other multimedia applications

# Constants
# WIDTH = 1600
# HEIGHT = 880

WIDTH = 1920
HEIGHT = 1080

CAR_SIZE_X = 60    
CAR_SIZE_Y = 60

BORDER_COLOR = (255, 255, 255, 255) # Color To Crash on Hit

current_generation = 0 # Generation counter

class Car:

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('car.png').convert() # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite 

        # self.position = [690, 740] # Starting Position
        self.position = [830, 920] # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False # Flag For Default Speed Later on

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2] # Calculate Center 

        self.radars = [] # List For Sensors / Radars
        self.drawing_radars = [] # Radars To Be Drawn

        self.alive = True # Boolean To Check If Car is Crashed

        self.distance = 0 # Distance Driven
        self.time = 0 # Time Passed

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position) # Draw Sprite
        self.draw_radar(screen) #OPTIONAL FOR SENSORS

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1) 
            #self.center: The starting point of the line, which is likely the car's center.
            #position: The end point of the line (where the radar reaches an objec
            #1: The width of the line, which is set to 1 pixel.
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, game_map): 
        # Checks if any corner of the car has hit the border color on the map.
        #  If any corner is on the border, the car is considered crashed (alive = False).
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                #If any corner touches a boundary (i.e., the pixel color at that point matches BORDER_COLOR),
                #the car's alive status is set to False
                self.alive = False
                break

    def check_radar(self, degree, game_map):
        #degree is the angle in which we want to check the radar relative to the car’s direction.
        #game_map represents the map or environment the car is navigating.
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
        #The coordinates (x, y) are calculated using trigonometric functions (cos and sin) to convert the angle degree to coordinates.
        #length is multiplied by the value from cos and sin to get the point along the radar.

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        #Extend the Radar Until Collision
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            # retrieves the color of the pixel at the coordinates (x, y).
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
            #The distance between the center (self.center) and the point (x, y) is calculated using the Pythagorean theorem

        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
    
    def update(self, game_map): #Updating Car's Position and State
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True #Sets a flag (speed_set) to indicate that the speed has been initialized.

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle) 
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed 
        #updates the car's x-position based on the current angle and speed
        self.position[0] = max(self.position[0], 20) #Keeping the Car Within Boundaries
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed #Increases the total distance traveled by adding the current speed.

        self.time += 1
        
        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        # Calculate Four Corners
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X #length is set to half of the car's width (CAR_SIZE_X) to determine how far from the center the corners are.
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map) #This helps the car "see" in multiple directions.

    def get_data(self): # Provides sensor data for the neural network. This data includes distances to obstacles detected by the car’s radars
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0] # Initializes an array of zeros to hold the data. This implies there are five radar directions.
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_alive(self):
        # Basic Alive Function
        return self.alive #True means the car is still operational; False means it has crashed.

    def get_reward(self): #Provides a reward value to assess the car's performance, which is used by the neural network to evolve
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)

    def rotate_center(self, image, angle): #Rotates the car image around its center, allowing for smooth and realistic turning.
        # Rotate The Rectangle
        rectangle = image.get_rect() # Gets the bounding rectangle of the original image.
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


def run_simulation(genomes, config): #function is responsible for running one generation of the simulation
    
    # Empty Collections For Nets and Cars
    nets = [] #nets: Holds the neural network controlling each car.
    cars = [] #cars: Holds the car instances that will be simulated.

    # Initialize PyGame And The Display
    pygame.init() #nitializes all imported Pygame modules.
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  


    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes: #genomes is a list of tuples where each tuple contains an index and a genome
        net = neat.nn.FeedForwardNetwork.create(g, config) #This neural network will be used to control a car's behavior.
        nets.append(net) #adds the neural network to the list nets
        g.fitness = 0

        cars.append(Car()) #creates an instance of the Car class and adds it to the cars list

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load('map.png').convert() # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1
    # Keeps track of the number of generations that have been run so far

    counter = 0 #This counter is used to limit how long the simulation runs, preventing it from going on indefinitely.

    while True:
        # Exit On Quit Event
        for event in pygame.event.get(): #This loop checks for any Pygame events, such as clicking the "close" button on the window.
            if event.type == pygame.QUIT:
                sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data()) #gets the output from the neural network based on the car’s radar data.
            choice = output.index(max(output)) # selects the action with the highest output value.
            if choice == 0: #The car can turn left, turn right, slow down, or speed up depending on the output of the neural network.
                car.angle += 10 # Left
            elif choice == 1:
                car.angle -= 10 # Right
            elif choice == 2:
                if(car.speed - 2 >= 12):
                    car.speed -= 2 # Slow Down
            else:
                car.speed += 2 # Speed Up
        
        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars): #If the car is alive, still_alive is incremented.
            if car.is_alive():
                still_alive += 1
                car.update(game_map) #updates the car’s position and checks for collisions.
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1

        if counter == 30 * 40: # Time Limit: The counter limits the time for each generation to roughly 20 seconds (30 frames/second * 40).
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0)) #draws the map onto the screen.
        for car in cars:
            if car.is_alive():
                car.draw(screen)
        
        # Display Info
        text = generation_font.render("Generation: " + str(current_generation), True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        screen.blit(text, text_rect)

        pygame.display.flip() #updates the display with everything that has been drawn, making it visible on the screen.
        clock.tick(60) # limits the simulation to 60 frames per second to ensure consistent performance and prevent it from running too fast.

if __name__ == "__main__":
    
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create Population And Add Reporters
    population = neat.Population(config) #The population represents an initial set of neural network candidates that will be evolved over generations.
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter() # Collects statistics like fitness over generations to analyze the progress of the evolution.
    population.add_reporter(stats)
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)
