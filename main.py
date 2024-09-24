import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join


# Initialize the pygame module to get everything started
pygame.init()

# Set the title of the window
pygame.display.set_caption("Super ZEE")

# Define the width and height of the game window
WIDTH, HEIGHT = 1280, 800

# Frames per second setting
FPS = 60

# Velocity (speed) at which the player moves
PLAYER_VEL = 6

# Starting health for the player
STARTING_HEALTH = 200

# Create the game window with the defined width and height
window = pygame.display.set_mode((WIDTH, HEIGHT))
# Load Music and Sound Effects
pygame.mixer.init()
pygame.mixer.music.load('assets/sounds/background_music1.mp3')
pygame.mixer.music.play(-1)  # Loop background music
# Load sound effects
jump_sound = pygame.mixer.Sound(join("assets", "sounds", "jump.wav"))
hit_sound = pygame.mixer.Sound(join("assets", "sounds", "ohoh.mp3"))
land_sound = pygame.mixer.Sound(join("assets", "sounds", "landing.mp3"))
pick_up_sound = pygame.mixer.Sound(join("assets", "sounds", "pick_up.mp3"))
timer_sound = pygame.mixer.Sound(join("assets", "sounds", "timer.mp3"))
win_sound = pygame.mixer.Sound(join("assets", "sounds", "win.mp3"))
game_over_sound = pygame.mixer.Sound(join("assets", "sounds", "game_over.mp3"))


# Function to flip a list of sprites horizontally
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


# Function to load sprite sheets and return individual sprites
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)  # Set path to the sprite sheet directory
    # List all files (images) in the directory and store them in images
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}  # Dictionary to holds all the sprites from the folder

    for image in images:  # loop through the images in the folder
        # Load the sprite sheet and maintain its transparency
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []  # list that holds all the sprites from 1 sprite sheet
        # Loop through the sprite sheet to extract each sprite
        for i in range(sprite_sheet.get_width() // width):
            # Create a transparent surface with the desired size
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            # Define the area of the sprite on the sheet
            rect = pygame.Rect(i * width, 0, width, height)
            # Blit the sprite onto the surface
            surface.blit(sprite_sheet, (0, 0), rect)
            # Scale sprite & append
            sprites.append(pygame.transform.scale2x(surface))

        if direction:  # if we're told to flip the sprites
            # remove png extension and Store the sprites facing right
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            # Store the flipped sprites facing left
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:  # Store the sprites as is
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


# Function to get a single block image for the terrain
def get_block():
    path = join("assets", "Terrain", "Terrain1.png")  # Path to the block image
    image = pygame.image.load(path).convert_alpha()  # Load the block image
    return pygame.transform.scale2x(image)  # Scale the block and return it


# Define the Player class, inheriting from pygame.sprite.Sprite
class Player(pygame.sprite.Sprite):

    GRAVITY = 1  # Gravity constant for the player
    # Load ALL player sprites
    SPRITES = load_sprite_sheets("Main Character", "Super ZEE", 32, 32, True)
    ANIMATION_DELAY = 4  # Delay between animation frames

    def __init__(self, x, y, width, height):
        super().__init__()  # Call the parent class (Sprite) constructor
        self.rect = pygame.Rect(x, y, width, height)  # Create player's rect
        self.x_vel = 0  # Horizontal velocity
        self.y_vel = 0  # Vertical velocity
        self.mask = None  # Mask for collision detection
        self.direction = "left"  # Default direction
        self.animation_count = 0  # Animation frame counter
        self.fall_count = 0  # Fall counter to manage gravity
        self.jump_count = 0  # Jump counter to allow double jumps
        self.hit = False  # Flag to indicate if the player was hit
        self.hit_count = 0  # Counter to manage hit animation
        self.health = STARTING_HEALTH  # Set player's starting health

    def jump(self):
        self.y_vel = -self.GRAVITY * 8  # Set upward velocity for jumping
        self.animation_count = 0  # Reset the animation counter
        self.jump_count += 1  # Increment the jump counter
        jump_sound.play()  # Play jump sound effect

        if self.jump_count == 1:
            self.fall_count = 0  # Reset fall count if it's the first jump

    def move(self, dx, dy):
        self.rect.x += dx  # Move the player horizontally
        self.rect.y += dy  # Move the player vertically

    def make_hit(self):
        self.hit = True  # Set the player as hit
        hit_sound.play()  # Play hit sound effect
        self.health -= 10  # Decrease health by 10 when hit by trap

    def move_left(self, vel):
        self.x_vel = -vel  # Set velocity for moving left
        if self.direction != "left":
            self.direction = "left"  # Change direction to left
            self.animation_count = 0  # Reset animation counter

    def move_right(self, vel):
        self.x_vel = vel  # Set velocity for moving right
        if self.direction != "right":
            self.direction = "right"  # Change direction to right
            self.animation_count = 0  # Reset animation counter

    def loop(self, fps):
        # Apply gravity over time
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)  # Move the player based on velocity

        if self.hit:
            self.hit_count += 1  # Increment hit counter
        if self.hit_count > fps:  # Reset hit status after a certain time
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1  # Increment fall counter
        self.update_sprite()  # Update the player's sprite based on state

    def landed(self):
        self.fall_count = 0  # Reset fall counter when landing
        self.y_vel = 0  # Stop vertical movement
        self.jump_count = 0  # Reset jump counter

    def hit_head(self):
        self.fall_count = 0  # Reset fall counter if hitting the head
        self.y_vel *= -1  # Reverse the vertical velocity (to make it bounce)

    def update_sprite(self):
        sprite_sheet = "idle zee"  # Default sprite sheet is idle
        if self.hit:  # Use hit sprite sheet if the player was hit
            sprite_sheet = "hit zee"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump zee"  # Use jump sprite for the first jump
            elif self.jump_count == 2:  # Use double jump sprite for 2nd jump
                sprite_sheet = "double_jump zee"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall zee"  # Use fall sprite if falling
        elif self.x_vel != 0:
            sprite_sheet = "run zee"  # Use run sprite if moving horizontally

        # Determine the correct sprite sheet based on state and direction
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        # Get the sprite list for the current state
        sprites = self.SPRITES[sprite_sheet_name]
        # Calculate the sprite index based on the animation counter
        sp_idx = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sp_idx]  # Set the current sprite
        self.animation_count += 1  # Increment the animation counter
        self.update_rect_mask()  # Update the player's rect and mask

    def update_rect_mask(self):
        # Update rect with the new sprite size and the collision mask
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        # Draw the player sprite with offset for scrolling
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


# Define the Object class, a generic class for game objects
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()  # Call the parent class (Sprite) constructor
        self.rect = pygame.Rect(x, y, width, height)  # Define the obj rect
        # Create a transparent surface for the object
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width  # Set the object's width
        self.height = height  # Set the object's height
        self.name = name  # Set the object's name

    def draw(self, window, offset_x):
        # Draw the object on the screen with offset for scrolling
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))


# Define the Block class, a specific type of Object representing terrain blocks
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)  # Initialize as a generic Object
        block = get_block()  # Get the block image
        self.image.blit(block, (0, 0))  # Blit the block onto the obj image
        # Create a mask for collision detection
        self.mask = pygame.mask.from_surface(self.image)


class Checker(Object):
    ANIMATION_DELAY = 3  # Delay between animation frames

    def __init__(self, x, y, width, height):
        # Initialize as an Object with the name "checker"
        super().__init__(x, y, width, height, "checker")
        self.checker = load_sprite_sheets("Traps", "checker", width, height)
        # Create a mask for collision detection
        self.mask = pygame.mask.from_surface(self.image)
        # animation_count tracks how long obj animation has been running
        self.animation_count = 0
        self.animation_name = "checker sheet"  # set image as default

    def loop(self):
        # Get the appropriate sprites based on the checker's state
        sprites = self.checker[self.animation_name]
        # Calculate the sprite index
        sp_idx = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sp_idx]  # Set the current sprite
        self.animation_count += 1  # Increment the animation counter
        # Update rect with the new sprite size
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        # Update the collision mask
        self.mask = pygame.mask.from_surface(self.image)
        # Reset the animation counter if needed
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


# Define the kimba class, a specific type of Object representing kimba traps
class Kimba(Object):
    ANIMATION_DELAY = 5  # Delay between animation frames

    def __init__(self, x, y, width, height):
        # Initialize as a generic Object with the name "kimba"
        super().__init__(x, y, width, height, "kimba")
        self.fire = load_sprite_sheets("Traps", "kimba", width, height)
        # Create a mask for collision detection
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0  # Animation frame counter
        self.animation_name = "kimba sheet"  # Set kimba sheet as default

    def loop(self):
        # Get the appropriate sprites based on kimba's state
        # for V1 of this game, kimba will have only one state
        sprites = self.fire[self.animation_name]
        sp_idx = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sp_idx]  # Set the current sprite
        self.animation_count += 1  # Increment the animation counter
        # Update rect with the new sprite size
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)  # Update the mask
        # Reset the animation counter if needed
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    # function that Loads the background image and tiles it across screen
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()  # Get the dimensions of bg image
    tiles = []

    for i in range(WIDTH // width + 1):  # Tile the background horizontally
        pos = (i * width, 0)
        tiles.append(pos)  # Add each tile position to the list

    return tiles, image  # Return the tile positions and the background image


# Function to draw the game window
def draw(window, bg_tiles, bg_image, player, objects, offset_x):
    for tile in bg_tiles:
        window.blit(bg_image, tile)  # Draw each background tile

    for obj in objects:
        obj.draw(window, offset_x)  # Draw each object in the scene

    player.draw(window, offset_x)  # Draw the player


# Function to handle vertical collisions with objects
def check_vertical_collision(player, objects, dy):
    collided_objects = []  # List to store objects the player collided with
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):  # Check for collision
            if dy > 0:  # If player is falling, Position her on top of obj
                player.rect.bottom = obj.rect.top
                player.landed()  # Call the landed method to stop falling
            elif dy < 0:  # If player is jumping, Position her below the obj
                player.rect.top = obj.rect.bottom
                player.hit_head()  # Call the hit_head method

            collided_objects.append(obj)  # Add the object to collision list

    return collided_objects  # Return the list of collided objects


# Function to check for horizontal collisions with walls etc
def check_horizontal_collision(player, objects, dx):
    player.move(dx, 0)  # Move player horizontally by dx to test for collisions
    player.update_rect_mask()  # Update the player's rect and mask
    collided_object = None  # Initialize the collided object as None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):  # Check for collision
            collided_object = obj  # Store the collided object
            break  # Stop checking if a collision is found

        player.move(-dx, 0)  # Move the player back to the original position
        player.update_rect_mask()  # Update the player's rect and mask
        return collided_object  # Return the collided object (if any)


# Function to handle player movement and collisions
def handle_move(player, objects):
    keys = pygame.key.get_pressed()  # Get the pressed keys

    # Reset horizontal velocity ensuring the player doesn't move
    # unless input is detected
    player.x_vel = 0
    # Check for collision to the left. PLAYER_VEL is the player's speed
    # so PLAYER_VEL * 2 doubles the player's movement speed for this check
    collide_left = check_horizontal_collision(player, objects, -PLAYER_VEL * 2)
    # Check for collision to the right
    collide_right = check_horizontal_collision(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        # Move left if left arrow is pressed and no collision
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        # Move right if right arrow is pressed and no collision
        player.move_right(PLAYER_VEL)

    # Handle vertical collisions
    vertical_collide = check_vertical_collision(player, objects, player.y_vel)
    # List of objects to check for trap collision
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name in ("kimba", "checker"):
            player.make_hit()  # Set the player as hit if collision with trap


# Function to draw the start menu with an image
def draw_start_menu(window, start_image):
    window.fill((0, 0, 0))  # Fill the screen with black
    # Center the image on the screen
    start_image_rect = start_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    # Draw the start image at its top-left position
    window.blit(start_image, start_image_rect.topleft)
    pygame.display.update()  # Update the display

    return start_image_rect  # Return the rect for event handling


# Processes events like mouse clicks to start the game or quit
# makes the menu image clicable
def start_menu(window):
    # Load the start image
    path = join("assets", "start", "start.png")
    start_image = pygame.image.load(path).convert_alpha()
    start_game = False  # Variable to track when to start the game

    while not start_game:
        # Draw the start menu with the image while game hasn't started
        start_image_rect = draw_start_menu(window, start_image)

        for event in pygame.event.get():
            # quit game if the user pressed the exit button
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # check if mouse click happened within the bounds of the start img
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_image_rect.collidepoint(event.pos):
                    start_game = True  # Set the flag to start the game

    return


# define the exam class. What the player has to collect to gain points
class Exam(Object):

    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        # choose path and Load the exam image
        path = join("assets", "Items", "exams", "exam.png")
        self.image = pygame.image.load(path).convert_alpha()
        # Create a mask for collision detection
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, window, offset_x):
        # Draw the animated fruit with scrolling offset
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))


# Function to handle collection of exams
def handle_exam_collection(player, exams):
    collected_exams = []  # List to store collected exams
    for exam in exams:
        if pygame.sprite.collide_mask(player, exam):
            # Check for collision with exams and play sound
            pick_up_sound.play()
            collected_exams.append(exam)  # Add the exam to the collected list

    for exam in collected_exams:
        exams.remove(exam)  # Remove the collected exams from the list

    # Return the number of collected exams to calculate score later
    return len(collected_exams)


# Function to draw the score on the screen
def draw_score(window, font, score):
    # Create score text
    score_text = font.render(f"Score: {score}", True, (255, 255, 0))
    # Draw score at the top-left corner of the screen
    window.blit(score_text, (10, 10))


# Function to draw the health bar on the screen
def draw_health_bar(window, font, health):
    # Create health text
    health_text = font.render(f"Health: {health}", True, (255, 255, 100))
    window.blit(health_text, (10, 50))  # Draw health below the score


# Function to draw the end screen when the player dies
def draw_end_screen(window, font):
    window.fill((0, 0, 0))  # Fill the screen with black
    # Create end screen text
    txt = font.render("GAME OVER! Press 'R' to Restart", True, (255, 255, 255))
    # Center the text on the screen
    window.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 50))
    pygame.display.update()  # Update the display

    waiting = True
    while waiting:  # Wait for the player to press 'R' to restart the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # If the player presses 'R'
                    waiting = False  # Exit the loop to restart the game


# Function to draw the win screen when the player wins
def draw_win_screen(window, font):
    window.fill((255, 255, 255))  # Fill the screen with white
    # Create win screen text
    txt = font.render("LEVEL 1 COMPLETED :D", True, (255, 100, 180))
    # Center the text on the screen
    window.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 50))
    pygame.display.update()  # Update the display

    waiting = True
    while waiting:  # Wait for the player to click mouse to restart the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if window.collidepoint(event.pos):
                    waiting = False  # Exit the loop to restart the game


# Path to the box image
box_image_path = join("assets", "Items", "Box", "Idlebox.png")


# Box Class
class Box(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)  # Initialize as a generic Object
        self.image = pygame.image.load(box_image_path).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask


# Timer function draws timer on the screen
def draw_timer(window, font, start_ticks):
    # Calculate the seconds elapsed and convert millisecs to secs
    seconds = (pygame.time.get_ticks() - start_ticks) / 1000
    time_left = max(0, 60 - seconds)  # 60-second time limit
    # create text for the timer and color it Red for urgency
    timer_text = font.render(f"Time Left: {int(time_left)}", True, (255, 0, 0))
    # Position the timer in the top-right corner
    window.blit(timer_text, (WIDTH - 240, 50))
    return time_left  # to later determine if the player has run out of time


# Main game loop
def main(window):
    start_menu(window)  # Display the start menu before the game begins

    play_sound_once = 0  # ensures the ticking sound is only played once
    # Create a clock object to control the frame rate
    clock = pygame.time.Clock()
    # load pixel Font to display the text
    font = pygame.font.Font("Grand9K Pixel.ttf", 30)
    # Load the background image
    background, bg_image = get_background("skyline.png")

    block_size = 96  # Define the size of terrain blocks

    player = Player(100, 100, 70, 70)  # Create the player object

    # Create a list of traps at different positions
    traps = [
        Kimba(100, HEIGHT - block_size - 64, 28, 32),
        Checker(400, (HEIGHT - block_size * 2 - 64), 28, 32),
        Checker(600, (HEIGHT - block_size * 3 - 64), 28, 32),
        Checker(900, (HEIGHT - block_size * 4 - 64), 28, 32),
        Kimba(1200, HEIGHT - block_size - 64, 28, 32),
        Kimba(1500, HEIGHT - block_size - 64, 28, 32),
        Checker(1800, HEIGHT - block_size * 7 - 64, 28, 32),
        Checker(2100, HEIGHT - block_size * 2 - 64, 28, 32),
        Kimba(2400, HEIGHT - block_size - 64, 28, 32),
        Kimba(2700, HEIGHT - block_size - 64, 28, 32),
        Kimba(3000, HEIGHT - block_size - 64, 28, 32),  # Add traps
    ]

    # Create the floor with blocks
    floor = []
    for i in range(-WIDTH // block_size, (WIDTH * 5) // block_size):
        block = Block(i * block_size, HEIGHT - block_size, block_size)
        floor.append(block)
    # Remove some blocks to create gaps
    for i in range(5, 10):
        # Create a gap in the floor for the player to jump over
        floor.remove(floor[i])

    # Add wall blocks to force jumps and make navigation harder
    walls = [
        Block(400, HEIGHT - block_size * 2, block_size),  # Wall 1
        Block(800, HEIGHT - block_size * 3, block_size),  # Wall 2
        Block(1200, HEIGHT - block_size * 4, block_size),  # Wall 3
        Block(1600, HEIGHT - block_size * 5, block_size),  # Wall 4
        Block(2000, HEIGHT - block_size * 6, block_size),  # Wall 5
        Block(2400, HEIGHT - block_size * 7, block_size),  # Wall 6
        Block(2800, HEIGHT - block_size * 8, block_size),
    ]
    # add boxes for player to jump on to reach exams
    boxes = [
        Box(500, HEIGHT - block_size - 64, 64),
        Box(800, HEIGHT - block_size - 64, 64),
        Box(1100, HEIGHT - block_size * 2 - 64, 64),
        Box(1400, HEIGHT - block_size * 3 - 64, 64),
        Box(1700, HEIGHT - block_size * 4 - 64, 64),
        Box(2100, HEIGHT - block_size * 5 - 64, 64),
        Box(2300, HEIGHT - block_size * 6 - 64, 64),
    ]
    # create list of all objects created
    objects = [*floor, *walls, *traps, *boxes]

    # Adds exam objects at various locations
    # These exams are collectible items placed in challenging positions
    # to encourage exploration and skillful jumping
    exams = [
        Exam(300, HEIGHT - block_size * 2 - 90, 70),
        Exam(1000, HEIGHT - block_size * 3 - 90, 70),
        Exam(1500, HEIGHT - block_size * 5 - 90, 70),
        Exam(1800, HEIGHT - block_size * 6 - 90, 70),
        Exam(2100, HEIGHT - block_size * 4 - 90, 70),
        Exam(2400, HEIGHT - block_size * 5 - 90, 70),
        Exam(2700, HEIGHT - block_size * 6 - 90, 70),
    ]

    score = 0  # Initialize score to 0
    offset_x = 0  # Horizontal offset for scrolling
    # Defines how much the player can move before the screen starts scrolling
    scroll_area_width = 300
    # Get the number of ticks since pygame started
    start_ticks = pygame.time.get_ticks()
    run = True  # Variable to keep the game loop running
    while run:
        clock.tick(FPS)  # Limit the frame rate

        for event in pygame.event.get():  # Process all events
            if event.type == pygame.QUIT:  # Exit if close button is pressed
                run = False
                break

            if event.type == pygame.KEYDOWN:
                # Allow jumping when space is pressed
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)  # Update the player object

        for trap in traps:
            trap.loop()  # Update each trap

        handle_move(player, objects)  # Handle player movement and collision

        # Handle exam collection and update the score
        collected_exams = handle_exam_collection(player, exams)
        score += collected_exams * 10  # Increase the score

        if score >= 70:  # If the player has collected 70 points, win the game
            # background music stops and win sound plays
            pygame.mixer.music.stop()
            win_sound.play()
            draw_win_screen(window, font)  # Draw the win screen
            main(window)  # Restart the game

        # Check if player health is 0 and display the end screen
        if player.health <= 0:
            # background music stops and game-over sound plays
            pygame.mixer.music.stop()
            game_over_sound.play()
            draw_end_screen(window, font)
            main(window)  # Restart the game after the end screen

        draw(window, background, bg_image, player, objects, offset_x)

        # Draw exams
        for exam in exams:
            exam.draw(window, offset_x)  # Draw the exam

        # Draw the score
        draw_score(window, font, score)  # Display the score on the screen

        # Draw the health bar
        draw_health_bar(window, font, player.health)
        # Draw the timer and check if time ran out
        time_left = draw_timer(window, font, start_ticks)
        if play_sound_once == 0 and time_left < 11:
            # if the time is less than 11 seconds, play the ticking sound
            timer_sound.play()
            play_sound_once = 1
        if time_left == 0:  # If time runs out, the game ends
            # stop mixer and play game over sound
            pygame.mixer.music.stop()
            game_over_sound.play()
            draw_end_screen(window, font)
            main(window)  # Restart the game after drawing end_screen

        # Handle screen scrolling
        if (
            (player.x_vel > 0 and
             player.rect.right - offset_x >= WIDTH - scroll_area_width) or
            (player.x_vel < 0 and
             player.rect.left - offset_x <= scroll_area_width)
        ):
            offset_x += player.x_vel  # Adjust the horizontal offset

        # Update the display
        pygame.display.flip()

    pygame.quit()  # Quit pygame
    quit()  # Exit the program


# Run the game
if __name__ == "__main__":
    main(window)
