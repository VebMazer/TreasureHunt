from linesegmentintersections import bentley_ottman
import pygame

from random import random
from math import sqrt, dist
from copy import copy


# Returns True if two rectangle shaped objects are colliding.
def collision(obj1, obj2):
        if obj1['x'] <= obj2['x'] + obj2['image'].get_width():
            if obj2['x'] <= obj1['x'] + obj1['image'].get_width():
                if obj1['y'] <= obj2['y'] + obj2['image'].get_height():
                    if obj2['y'] <= obj1['y'] + obj1['image'].get_height():
                        return True
        return False


# Returns True if a rectangle shaped object is colliding with a polygon.
# A polygon is a list of points, between of which line segments are drawn.
def colliding_with_polygon(obj, polygon):

    # Return True if any of the line segments in the polygon collide with
    # the object.
    for i in range(0, len(polygon)):
        if colliding_with_line(obj, (polygon[i-1], polygon[i])): return True
    
    return False


# Returns True if a rectangle shaped object is colliding with a line segment.
def colliding_with_line(obj, line):

    # Coordinate values with added width and height.
    x2 = obj['x'] + obj['image'].get_width()
    y2 = obj['y'] + obj['image'].get_height()

    # Setup variables for all four points of the rectangle.
    p1 = (obj['x'], obj['y'])
    p2 = (x2,       obj['y'])
    p3 = (obj['x'], y2)
    p4 = (x2,       y2)
    
    # The input line itself is not necessarily neither horizontal or
    # vertical, but it needs to be tested with both sets of lines.
    # We cant test all the line segments at once because the vertical
    # and horizontal line segments of the square are always colliding.
    # with each other.
    horizontal_segments = [(p1, p2), (p3, p4), line]
    vertical_segments   = [(p1, p3), (p2, p4), line]

    # Test if either the horizontal or the vertical lines of
    # the square are colliding with the input line. Return
    # True if so.
    if colliding_line_segments(horizontal_segments): return True
    if colliding_line_segments(vertical_segments): return True

    return False


# Returns True if any of the line segments in the input list are crossing/colliding.
def colliding_line_segments(line_segments: list):
    
    # Bentley-Otman algorithm returns a list of all crossings in a set of
    # line segments. If any crossings are found: return True
    if bentley_ottman(line_segments): return True

    # If no crossings were found return False.
    return False


# Collect all the coins and escape before the monsters catch you.
class TreasureHunt:
    def __init__(self):
        pygame.init()

        self.game_font = pygame.font.SysFont("Arial", 24)

        self.initialize()

        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Treasure Hunt')

        self.load_images()
        self.level_loop()


    # Initializes the game.
    def initialize(self):
        
        # Game board dimensions.
        self.width  = 960
        self.height = 720
        
        # Movement speed of the player and the monsters.
        self.speed  = 3
        
        self.points = 0
        
        # Variables that control where the player is moving.
        self.moving_left  = False
        self.moving_right = False
        self.moving_up    = False
        self.moving_down  = False

        # Render point and level information texts.
        self.points_text = self.game_font.render(f'Points: {self.points}', True, (255, 0, 0))
        self.level_text = self.game_font.render('Level: 1', True, (255, 0, 0))


    # Loads the necessary images and places them in to the self.images variable.
    def load_images(self):
        self.images = {}
        folder_name = 'pictures'

        for name in ['coin', 'door', 'monster', 'robot']:
            self.images[name] = pygame.image.load(f'{folder_name}/{name}.png')


    # Main loop of the game that controls level generation and starts the
    # execution of each level.
    def level_loop(self):
        self.points = 0
        self.caught = False

        self.level = 1
        while self.level <= 12 and not self.caught:
            self.generate_level()
            self.play_level()

        self.game_over()


    # Generates a level based on the value of self.level
    def generate_level(self):

        # Initialize variables for the game objects.
        self.coins = []
        self.monsters = []
        self.rocks = []
        self.door = None

        # Create two or more rocks depending on the level.
        for i in range(2 + int(self.level / 3)):
            self.rocks.append(self.create_rock())

        self.player = self.create_object('robot')

        self.door   = self.create_object('door')

        # Create coins and monsters. The amount of coins is equal to the level.
        # while the amount of monsters is approximately half of the level.
        for i in range(self.level):

            if i % 2 == 0:
                monster = self.create_object('monster')
                self.monsters.append(monster)

            coin = self.create_object('coin')
            self.coins.append(coin)


    # Create the object with random coordinates on the game board. If spawning
    # the object on that position is not allowed then recreate the object until
    # one is created that can be spawned.
    def create_object(self, image):
        
        # Try to create the object 10^5 times or until one with an allowed
        # position is found.
        for i in range(10**5):
            obj = {
                'x': random() * (self.width  - self.images[image].get_width()),
                'y': random() * (self.height - self.images[image].get_height()),
                'image': self.images[image]
            }
            if self.spawning_allowed(obj):
                return obj

        # If 10^5 attempts to create the object failed then the game board is probably
        # too crowded with objects and an Exception is raised.
        raise Exception('Cannot spawn more objects because the game board is too crowded.')


    # Creates a rock polygon. Rocks can spawn on top of each other.
    def create_rock(self):
        
        # The amount of points added after the initial one.
        added_points = 2 + int(random() * 8)
        
        # Add first point to the points list.
        points = [(
            random() * self.width,
            random() * self.height
        )]

        # Generate the rest of the points.
        for i in range(added_points):
            x = -1
            y = -1

            # Repeat until the x value is inside the game board.
            while not 0 < x < self.width:
                # Set the x value to be between [0, 120] more or less than
                # that of the previous point.
                if int(random() * 2): x = points[-1][0] + random() * 120
                else:                 x = points[-1][0] - random() * 120

            # Repeat until the y value is inside the game board.
            while not 0 < y < self.height:

                # Set the y value to be between [0, 120] more or less than
                # that of the previous point.
                if int(random() * 2): y = points[-1][1] + random() * 120
                else:                 y = points[-1][1] - random() * 120

            points.append((x, y))

        # In the end the amount of points will be between [3, 11].
        return points


    # Checks whether spawning the object in to the specified coordinates is allowed.
    def spawning_allowed(self, obj):

        # Check if the object is too close to the player.
        if 'player' in dir(self):
            if self.too_close_to_player(obj): return False
        
        # Check if the object collides with existing game objects.

        if self.door and collision(self.door, obj): return False

        for monster in self.monsters:
            if collision(monster, obj): return False

        for coin in self.coins:
            if collision(coin, obj): return False

        # Check if the object is too close to a rock. 
        if self.too_close_to_a_rock(obj): return False

        return True


    # Checks if the object is too close to a rock to be spawned there.
    def too_close_to_a_rock(self, obj):
        for rock in self.rocks:

            # Check if the object is too close to any of the points in the rock polygon.
            for point in rock:
                coordinates = (obj['x'], obj['y'])
                if dist(point, coordinates) < 150: return True

        return False


    # Checks if the object is too close to the player to be spawned there.
    def too_close_to_player(self, obj):
        player_coords = (self.player['x'], self.player['y'])
        obj_coords = (obj['x'], obj['y'])

        if dist(player_coords, obj_coords) < 250: return True

        return False


    # Method that executes each level.
    def play_level(self):
        level = self.level

        # Loop that runs while a level is played.
        while level == self.level and not self.caught:
            self.check_events()
            self.update_game()
            self.draw_level()
            self.clock.tick(60)


    # Monitors pygame events and controls the movement of the player
    # based on the keys they are pressing.
    def check_events(self):
        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.moving_left  = True
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.moving_right = True
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.moving_up    = True
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.moving_down  = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.moving_left  = False
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.moving_right = False
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.moving_up    = False
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.moving_down  = False

            elif event.type == pygame.QUIT: exit()


    # Updates the state of the game to the next iteration.
    def update_game(self):
        player = self.player

        # The player is moved only if the player character stays within the game board
        # and does not collide with a rock as a result of their movement.

        if self.moving_right and player['x'] < self.width - player['image'].get_width():
            player['x'] += self.speed
            if self.colliding_with_rocks(player): player['x'] -= self.speed

        if self.moving_left and player['x'] > 0:
            player['x'] -= self.speed
            if self.colliding_with_rocks(player): player['x'] += self.speed

        if self.moving_down and player['y'] < self.height - player['image'].get_height():
            player['y'] += self.speed
            if self.colliding_with_rocks(player): player['y'] -= self.speed

        if self.moving_up and player['y'] > 0:
            player['y'] -= self.speed
            if self.colliding_with_rocks(player): player['y'] += self.speed

        # Points are awarded when the player collides with a coin and the indices of
        # the collected coins are collected into a list.
        removed_indices = []
        for i, coin in enumerate(self.coins):
            
            # Check if the coin collides with the player, add a point if it does and
            # save the index of the coin in the self.coins list.
            if collision(coin, self.player):
                removed_indices.append(i)
                self.points += 1
                self.points_text = self.game_font.render(f'Points: {self.points}', True, (255, 0, 0))
        
        # Reverse the indices so that the larger indices can be removed first.
        # so that the smaller ones still point to the right objects after their removal.
        removed_indices.reverse()
        
        # Remove the coin or coins that the player collided with.
        # Usually there will only be one or none, but in rare cases
        # there could be two or even three.
        for index in removed_indices: del self.coins[index]

        # Monsters are moved and if one of them collides with the player
        # after this the game is lost.
        for monster in self.monsters:
            self.move_monster(monster)

            if collision(self.player, monster):
                self.caught = True

        # If all the coins have been collected and the player has reached
        # the door, then the level is increased. This causes the play_level
        # loop to end, which causes the level_loop to create and start the next level.
        if not self.coins and collision(self.door, self.player):
            self.level += 1

            # Update the level number on the display.
            self.level_text = self.game_font.render(f'Level: {self.level}', True, (255, 0, 0))


    # Returns True if an object is colliding with any of the existing rocks.
    def colliding_with_rocks(self, obj):
        for rock in self.rocks:
            if colliding_with_polygon(obj, rock): return True
        return False


    # Moves a monster directly towards the player at a uniform speed.
    def move_monster(self, monster):
        # Differences in x and y coordinates between the monster and the player.
        a1 = self.player['x'] - monster['x']
        b1 = self.player['y'] - monster['y']

        # The movement speed of a monster is set to 25% of the players speed.
        velocity = (self.speed * 0.25)
        distance = sqrt(a1**2 + b1**2)

        # Then direct proportionality is used to infer and calculate how
        # much the x and y coordinates are supposed to change.

        # ((a2 / a1) = (velocity / distance)) implies:
        a2 = a1 * velocity / distance

        # ((b2 / b1) = (velocity / distance)) implies:
        b2 = b1 * velocity / distance

        monster['x'] += a2
        monster['y'] += b2


    # Draws the level into the game board.
    def draw_level(self):
        # Fill the board with white color.
        self.window.fill((240, 240, 240))

        # Draw the point and level information texts.
        self.window.blit(self.points_text, (self.width - self.points_text.get_width() - 20, 0))
        self.window.blit(self.level_text,  (20, 0))

        # Draw all the rocks.
        for rock in self.rocks:
            pygame.draw.polygon(self.window, (100, 100, 100), rock, 0)

        if self.door:
            # Draw the door.
            self.window.blit(self.images['door'],  (self.door['x'],   self.door['y']))

        # Draw all the coins.
        for coin in self.coins:
            self.window.blit(coin['image'],    (coin['x'],    coin['y'])   )
        
        # Draw all the monsters.
        for monster in self.monsters:
            self.window.blit(monster['image'], (monster['x'], monster['y']))

        if self.player:
            # Draw the player.
            self.window.blit(self.images['robot'], (self.player['x'], self.player['y']))

        pygame.display.flip()


    # End screen loop that runs when the game is over. Displays a message based on
    # whether the player won the game or not, and instructions on how to restart 
    # or exit the game. Then waits for the player to restart or exit.
    def game_over(self):
        
        # Create the ending text based on whether or not the player won or lost.
        end_text = self.game_font.render('Victory! You passed all levels.', True, (255, 0, 0))
        if self.caught:
            end_text = self.game_font.render('Game Over!', True, (255, 0, 0))

        help_text = self.game_font.render('Press SPACE to restart, or ESC to quit.', True, (255, 0, 0))

        # Wait for the player to exit or restart the game.
        new_game = False
        while not new_game:
            for event in pygame.event.get():
                if   event.type == pygame.KEYDOWN:
                    if   event.key == pygame.K_SPACE: new_game = True
                    elif event.key == pygame.K_ESCAPE: exit() # Exits the program

                elif event.type == pygame.QUIT: exit() # Exits the program

            # Display messages.
            self.window.fill((0, 0, 0))
            self.window.blit(end_text,  ((self.width - end_text.get_width()) / 2, (self.height - end_text.get_height()) / 2))
            self.window.blit(help_text, ((self.width - help_text.get_width()) / 2, 40 + (self.height - help_text.get_height()) / 2))
            pygame.display.flip()

        # Restarts the game.
        self.initialize()
        self.level_loop()



# Start the game if this file is run directly.
if __name__ == '__main__':
    TreasureHunt()
