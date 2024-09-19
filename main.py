import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join


# Initialize the pygame modules to get everything started
pygame.init()

# Set the title of the window
pygame.display.set_caption("Super ZEE")

# Define the width and height of the game window
WIDTH, HEIGHT = 1800, 1080  # Adjusted window size

# Frames per second setting
FPS = 60

# Velocity (speed) at which the player moves
PLAYER_VEL = 5

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
game_over_sound = pygame.mixer.Sound(join("assets", "sounds", "game_over.mp3"))

# Function to flip a list of sprites horizontally
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

# Function to load sprite sheets and return individual sprites
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)  # Set the path to the sprite sheet folder
    images = [f for f in listdir(path) if isfile(join(path, f))]  # List all files in the directory

    all_sprites = {}  # Dictionary to hold the sprites

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()  # Load the sprite sheet

        sprites = []
        for i in range(sprite_sheet.get_width() // width):  # Loop through the sprite sheet and extract each sprite
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)  # Create a transparent surface
            rect = pygame.Rect(i * width, 0, width, height)  # Define the area of the sprite on the sheet
            surface.blit(sprite_sheet, (0, 0), rect)  # Blit the sprite onto the surface
            sprites.append(pygame.transform.scale2x(surface))  # Scale the sprite and add it to the list

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites  # Store the sprites facing right
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)  # Store the flipped sprites facing left
        else:
            all_sprites[image.replace(".png", "")] = sprites  # Store the sprites without direction

    return all_sprites

# Function to get a single block image for the terrain
def get_block():
    path = join("assets", "Terrain", "Terrain5.png")  # Path to the terrain image
    image = pygame.image.load(path).convert_alpha()  # Load the terrain image
    # surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)  # Create a transparent surface for the block
    # rect = pygame.Rect(96, 0, size, size)  # Define the area of the block on the terrain sheet
    # surface.blit(image, (0, 0), rect)  # Blit the block onto the surface
    return pygame.transform.scale2x(image)  # Scale the block and return it

def get_checker():
    path = join("assets", "Traps", "checker.png")  # Path to the terrain image
    image = pygame.image.load(path).convert_alpha()  # Load the terrain image
    return pygame.transform.scale2x(image)

# Define the Player class, inheriting from pygame.sprite.Sprite
class Player(pygame.sprite.Sprite):
    # COLOR = (255, 0, 0)  # Default color (not used here)
    GRAVITY = 1  # Gravity constant for the player
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)  # Load player sprites
    ANIMATION_DELAY = 3  # Delay between animation frames

    def __init__(self, x, y, width, height):
        super().__init__()  # Call the parent class (Sprite) constructor
        self.rect = pygame.Rect(x, y, width, height)  # Create the player's rectangle
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
        self.health -= 5  # Decrease health by 10 when hit by fire
        
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
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)  # Apply gravity over time
        self.move(self.x_vel, self.y_vel)  # Move the player based on velocity

        if self.hit:
            self.hit_count += 1  # Increment hit counter
        if self.hit_count > fps * 2:  # Reset hit status after a certain time
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1  # Increment fall counter
        self.update_sprite()  # Update the player's sprite based on state

    def landed(self):
        self.fall_count = 0  # Reset fall counter when landing
        self.y_vel = 0  # Stop vertical movement
        self.jump_count = 0 # Reset jump counter

    def hit_head(self):
        self.fall_count = 0  # Reset fall counter if hitting the head
        self.y_vel *= -1  # Reverse the vertical velocity (bounce)

    def update_sprite(self):
        sprite_sheet = "idle zee final"  # Default sprite sheet is idle
        if self.hit:
            sprite_sheet = "hitzee"  # Use hit sprite sheet if the player was hit
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump zee"  # Use jump sprite for the first jump
            elif self.jump_count == 2:
                sprite_sheet = "double_jump zee"  # Use double jump sprite for the second jump
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall zee"  # Use fall sprite if falling
        elif self.x_vel != 0:
            sprite_sheet = "run zee"  # Use run sprite if moving horizontally

        sprite_sheet_name = sprite_sheet + "_" + self.direction  # Determine the correct sprite sheet based on state
        sprites = self.SPRITES[sprite_sheet_name]  # Get the sprite list for the current state
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)  # Calculate the sprite index
        self.sprite = sprites[sprite_index]  # Set the current sprite
        self.animation_count += 1  # Increment the animation counter
        self.update()  # Update the player's rect and mask

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))  # Update rect with the new sprite size
        self.mask = pygame.mask.from_surface(self.sprite)  # Update the collision mask

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))  # Draw the player sprite with offset for scrolling


# Define the Object class, a generic class for game objects
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()  # Call the parent class (Sprite) constructor
        self.rect = pygame.Rect(x, y, width, height)  # Define the object's rectangle
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  # Create a transparent surface for the object
        self.width = width  # Set the object's width
        self.height = height  # Set the object's height
        self.name = name  # Set the object's name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))  # Draw the object with offset for scrolling


# Define the Block class, a specific type of Object representing terrain blocks
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)  # Initialize as a generic Object
        block = get_block()  # Get the block image
        self.image.blit(block, (0, 0))  # Blit the block onto the object's image
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask for collision detection

# class Checker(Object):
    # def __init__(self, x, y, size):
        # super().__init__(x, y, size, size)  # Initialize as a generic Object
        # self.image = get_checker()  # Load the box image
        # self.mask = pygame.mask.from_surface(self.image)  # Create a mask for collision detection
class Checker(Object):
    ANIMATION_DELAY = 5  # Delay between animation frames

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "checker")  # Initialize as a generic Object with the name "fire"
        self.checker = load_sprite_sheets("Traps", "checker", width, height)  # Load fire sprites
        # self.image = self.fire["off"][0]  # Set the initial fire sprite (off)
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask for collision detection
        self.animation_count = 0  # Animation frame counter
        # self.animation_name = "off"  # Start with the fire off

    def on(self):
        self.animation_name = "checker sheet"  # Turn the fire on

    # def off(self):
        # self.animation_name = "off"  # Turn the fire off

    def loop(self):
        sprites = self.checker[self.animation_name]  # Get the appropriate sprites based on the fire's state
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)  # Calculate the sprite index
        self.image = sprites[sprite_index]  # Set the current sprite
        self.animation_count += 1  # Increment the animation counter

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))  # Update rect with the new sprite size
        self.mask = pygame.mask.from_surface(self.image)  # Update the collision mask

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):  # Reset the animation counter if needed
            self.animation_count = 0


# Define the Fire class, a specific type of Object representing fire traps
class Fire(Object):
    ANIMATION_DELAY = 5  # Delay between animation frames

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")  # Initialize as a generic Object with the name "fire"
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)  # Load fire sprites
        # self.image = self.fire["off"][0]  # Set the initial fire sprite (off)
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask for collision detection
        self.animation_count = 0  # Animation frame counter
        # self.animation_name = "off"  # Start with the fire off

    def on(self):
        self.animation_name = "kimba2"  # Turn the fire on

    # def off(self):
        # self.animation_name = "off"  # Turn the fire off

    def loop(self):
        sprites = self.fire[self.animation_name]  # Get the appropriate sprites based on the fire's state
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)  # Calculate the sprite index
        self.image = sprites[sprite_index]  # Set the current sprite
        self.animation_count += 1  # Increment the animation counter

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))  # Update rect with the new sprite size
        self.mask = pygame.mask.from_surface(self.image)  # Update the collision mask

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):  # Reset the animation counter if needed
            self.animation_count = 0


# Function to load and tile the background image
# def get_background(name):
    # image = pygame.image.load(join("assets", "Background", name))  # Load the background image
    # _, _, width, height = image.get_rect()  # Get the dimensions of the background image
    # tiles = []

    # for i in range(WIDTH // width + 1):  # Tile the background horizontally
        # for j in range(HEIGHT // height + 1):  # Tile the background vertically
            # pos = (i * width, j * height)
            # tiles.append(pos)  # Add each tile position to the list

    # return tiles, image  # Return the tile positions and the background image

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))  # Load the background image
    _, _, width, height = image.get_rect()  # Get the dimensions of the background image
    tiles = []

    for i in range(WIDTH // width + 1):  # Tile the background horizontally
        pos = (i * width, 0)
        tiles.append(pos)  # Add each tile position to the list

    return tiles, image  # Return the tile positions and the background image

# Function to draw the game window
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)  # Draw each background tile

    for obj in objects:
        obj.draw(window, offset_x)  # Draw each object in the scene

    player.draw(window, offset_x)  # Draw the player

    pygame.display.update()  # Update the display to show the new frame

# Function to handle vertical collisions with objects
def handle_vertical_collision(player, objects, dy):
    collided_objects = []  # List to store objects the player collides with
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):  # Check for collision using masks
            if dy > 0:
                player.rect.bottom = obj.rect.top  # Position the player on top of the object if falling
                player.landed()  # Call the landed method to stop falling
            elif dy < 0:
                player.rect.top = obj.rect.bottom  # Position the player below the object if hitting the head
                player.hit_head()  # Call the hit_head method to reverse velocity

            collided_objects.append(obj)  # Add the object to the collision list

    return collided_objects  # Return the list of collided objects

# Function to check for collision in a specific direction
def collide(player, objects, dx):
    player.move(dx, 0)  # Move the player horizontally by dx
    player.update()  # Update the player's rect and mask
    collided_object = None  # Initialize the collided object as None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):  # Check for collision using masks
            collided_object = obj  # Store the collided object
            break  # Stop checking if a collision is found

        player.move(-dx, 0)  # Move the player back to the original position
        player.update()  # Update the player's rect and mask
        return collided_object  # Return the collided object (if any)

# Function to handle player movement and collisions
def handle_move(player, objects):
    keys = pygame.key.get_pressed()  # Get the current state of all keyboard keys

    player.x_vel = 0  # Reset horizontal velocity
    collide_left = collide(player, objects, -PLAYER_VEL * 2)  # Check for collision to the left
    collide_right = collide(player, objects, PLAYER_VEL * 2)  # Check for collision to the right

    if keys[pygame.K_LEFT] and not collide_left:  # Move left if left arrow is pressed and no collision
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:  # Move right if right arrow is pressed and no collision
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)  # Handle vertical collisions
    to_check = [collide_left, collide_right, *vertical_collide]  # List of objects to check for fire collision

    for obj in to_check:
        if obj and obj.name in ("fire", "checker"):  # Check if the player collided with a fire object
            player.make_hit()  # Set the player as hit

# Function to draw the start menu with an image as a button
def draw_start_menu(window, start_image):
    window.fill((0, 0, 0))  # Fill the screen with black
    start_image_rect = start_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # Center the image on the screen
    window.blit(start_image, start_image_rect.topleft)  # Draw the start image at its top-left position
    pygame.display.update()  # Update the display

    return start_image_rect  # Return the rect for event handling


# Function to handle the start menu with the clickable image
def start_menu(window):
    start_image = pygame.image.load(join("assets","start","starting1.png")).convert_alpha()  # Load your start image
    start_game = False  # Variable to track when to start the game

    while not start_game:
        start_image_rect = draw_start_menu(window, start_image)  # Draw the start menu with the image

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_image_rect.collidepoint(event.pos):  # Check if the click is on the image
                    start_game = True  # Set the flag to start the game

    return
# Define the Checkpoint class
# class Checkpoint(Object):
    # def __init__(self, x, y, width, height):
        # super().__init__(x, y, width, height)
        # self.image = pygame.image.load(join("assets","Items", "checkpoints","Checkpoint","Checkpoint (No Flag).png")).convert_alpha()  # Load checkpoint image
        # self.mask = pygame.mask.from_surface(self.image)  # Mask for collision detection

class Fruit(Object):
    # ANIMATION_DELAY = 5  # Frames to delay before switching to the next frame

    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        # Load the fruit sprite sheet with multiple frames
        self.image = pygame.image.load(join("assets","Items", "Fruits", "exam.png"))  # Load your apple sprite sheet
        # self.sprites = []
        # sprite_width = fruit_spritesheet.get_width() // 16  # Assuming there are 16 frames in the sprite sheet
        # for i in range(16):  # Loop through the 16 frames of the sprite sheet
            # surface = pygame.Surface((sprite_width, fruit_spritesheet.get_height()), pygame.SRCALPHA, 32)
            # rect = pygame.Rect(i * sprite_width, 0, sprite_width, fruit_spritesheet.get_height())
            # surface.blit(fruit_spritesheet, (0, 0), rect)
            # self.sprites.append(pygame.transform.scale(surface, (size, size)))  # Scale the sprites

        # self.animation_count = 0  # Animation counter for cycling through frames
        # self.image = self.sprites[0]  # Start with the first sprite
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask for collision detection

    # def loop(self):
        # Cycle through the frames of the animation
        # self.animation_count += 1
        # if self.animation_count >= len(self.sprites) * self.ANIMATION_DELAY:
            # self.animation_count = 0  # Reset animation count after the last frame
        # Set the correct frame from the sprite sheet
        # self.image = self.sprites[self.animation_count // self.ANIMATION_DELAY]  # Update the sprite based on the counter
        # self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))  # Update the rect to match the new image size
        # self.mask = pygame.mask.from_surface(self.image)  # Update the mask for collision detection

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))  # Draw the animated fruit with scrolling


# Function to handle collection of fruits
def handle_fruit_collection(player, fruits):
    collected_fruits = []  # List to store collected fruits
    for fruit in fruits:
        if pygame.sprite.collide_mask(player, fruit):
            # Check for collision with fruits
            pick_up_sound.play()
            collected_fruits.append(fruit)  # Add the fruit to the collected list

    for fruit in collected_fruits:
        fruits.remove(fruit)  # Remove the collected fruits from the list

    return len(collected_fruits)  # Return the number of collected fruits

# Function to draw the score on the screen
def draw_score(window, font, score):
    score_text = font.render(f"Score: {score}", True, (255, 255, 100))  # Create score text
    window.blit(score_text, (10, 10))  # Draw score at the top-left corner of the screen

# Function to draw the health bar on the screen
def draw_health_bar(window, font, health):
    health_text = font.render(f"Health: {health}", True, (255, 255, 100))  # Create health text
    window.blit(health_text, (10, 50))  # Draw health below the score

# Function to draw the end screen when the player dies
def draw_end_screen(window, font):
    window.fill((0, 0, 0))  # Fill the screen with black
    end_text = font.render("Game Over! Press 'R' to Restart", True, (255, 255, 255))  # Create end screen text
    window.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - 50))  # Center the text
    pygame.display.update()  # Update the display
    pygame.mixer.stop()
    pygame.mixer.init()
    game_over_sound.play()
    pygame.mixer.stop()

    waiting = True
    while waiting:  # Wait for the player to press 'R' to restart the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False  # Exit the loop to restart the game
box_image_path = join("assets", "Items", "Boxes","Box1","Idle box.png")  # Path to the box image

# Box Class
class Box(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)  # Initialize as a generic Object
        self.image = pygame.image.load(box_image_path).convert_alpha()  # Load the box image
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask for collision detection

# Timer function
def draw_timer(window, font, start_ticks):
    # Calculate the seconds elapsed
    seconds = (pygame.time.get_ticks() - start_ticks) / 1000  # Convert milliseconds to seconds
    time_left = max(0, 120 - seconds)  # 60-second time limit
    timer_text = font.render(f"Time Left: {int(time_left)}", True, (255, 255, 100))  # Red color for urgency
    window.blit(timer_text, (WIDTH - 300, 50))  # Position the timer in the top-right corner
    return time_left

# Main game loop with health and end screen
def main(window):
    start_menu(window)  # Display the start menu before the game begins

    clock = pygame.time.Clock()  # Create a clock object to control the frame rate
    font = pygame.font.Font("Grand9K Pixel.ttf", 30)
    # font = pygame.font.SysFont(Grand9KCraft, 50)  # Font for displaying the score and health
    background, bg_image = get_background("skyline3.png")  # Load the background image

    block_size = 96  # Define the size of terrain blocks

    player = Player(100, 100, 60, 60)  # Create the player object

    # Create a list of fire traps at different positions
    fires = [
    Fire(100, HEIGHT - block_size - 64, 28, 32),
    Checker(400, (HEIGHT - block_size * 2 - 64), 28, 32),
    Checker(600, (HEIGHT - block_size * 3 - 64), 28, 32),
    Checker(900, (HEIGHT - block_size * 4 - 64), 28, 32),
    Fire(1200, HEIGHT - block_size - 64, 28, 32),
    Fire(1500, HEIGHT - block_size - 64, 28, 32),  # More fires for harder difficulty
    Checker(1800, HEIGHT - block_size * 7 - 64, 28, 32),
    Checker(2100, HEIGHT - block_size * 2 - 64, 28, 32),
    Fire(2400, HEIGHT - block_size - 64, 28, 32),
    Fire(2700, HEIGHT - block_size - 64, 28, 32),
    Fire(3000, HEIGHT - block_size - 64, 28, 32),  # Add more fire traps for increased challenge
]
    for fire in fires:
        fire.on()  # Turn the fire traps on

    # Create gaps in the floor to increase difficulty
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, (WIDTH * 5) // block_size)]
    # Remove some blocks to create gaps
    for i in range(5, 10):
        floor.remove(floor[i])  # Create a gap in the floor for the player to jump over

    # Add wall blocks to force jumps and make navigation harder
    walls = [
    Block(400, HEIGHT - block_size * 2, block_size),  # Wall 1
    Block(800, HEIGHT - block_size * 3, block_size),  # Wall 2
    Block(1200, HEIGHT - block_size * 4, block_size),  # Wall 3
    Block(1600, HEIGHT - block_size * 5, block_size),  # Wall 4
    Block(2000, HEIGHT - block_size * 6, block_size),  # Wall 5
    Block(2400, HEIGHT - block_size * 7, block_size),  # Wall 6
    Block(2800, HEIGHT - block_size * 8, block_size),  # Add more walls for complexity
]
    boxes = [
    Box(500, HEIGHT - block_size - 64, 64),  # Box placed on the floor
    Box(800, HEIGHT - block_size - 64, 64),  # Another box on the floor
    Box(1100, HEIGHT - block_size * 2 - 64, 64),  # Box on higher ground
    Box(1400, HEIGHT - block_size * 3 - 64, 64),  # Box near fire trap
    Box(1700, HEIGHT - block_size * 4 - 64, 64),  # Box in harder-to-reach position
    Box(2100, HEIGHT - block_size * 5 - 64, 64),  # Box near fire trap
    Box(2300, HEIGHT - block_size * 6 - 64, 64),  # Add more boxes for higher difficulty
]
    # Combine floor and walls into one list of objects
    objects = [*floor, *walls, *fires, *boxes]

    # Add fruits to the map, place them in difficult locations
    fruits = [
    Fruit(300, HEIGHT - block_size * 2 - 90, 70),  # Hard-to-reach location
    Fruit(1000, HEIGHT - block_size * 3 - 90, 70),  # Higher location
    Fruit(1500, HEIGHT - block_size * 5 - 90, 70),  # Even higher near fire
    Fruit(1800, HEIGHT - block_size * 6 - 90, 70),  # Very high and near fire
    Fruit(2100, HEIGHT - block_size * 4 - 90, 70),  # Harder to reach location
    Fruit(2400, HEIGHT - block_size * 5 - 90, 70),  # Add more fruits in tricky positions
    Fruit(2700, HEIGHT - block_size * 6 - 90, 70),  # Near fire and higher elevation
]

    score = 0  # Initialize score to 0
    offset_x = 0  # Horizontal offset for scrolling
    scroll_area_width = 300  # Define a smaller scroll area to limit movement
    # Start the timer
    start_ticks = pygame.time.get_ticks()  # Get the number of ticks since pygame started
    run = True  # Variable to keep the game loop running
    while run:
        clock.tick(FPS)  # Limit the frame rate

        for event in pygame.event.get():  # Process all events
            if event.type == pygame.QUIT:  # Exit the game if the close button is pressed
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:  # Allow jumping when space is pressed
                    player.jump()

        player.loop(FPS)  # Update the player object

        for fire in fires:
            fire.loop()  # Update each fire trap

        handle_move(player, objects)  # Handle player movement and collision

        # Handle fruit collection and update the score
        collected_fruits = handle_fruit_collection(player, fruits)
        score += collected_fruits  # Increase the score by the number of collected fruits

        # Check if player health is 0 and display the end screen
        if player.health <= 0:
            draw_end_screen(window, font)
            main(window)  # Restart the game after the end screen

        draw(window, background, bg_image, player, objects, offset_x)  # Draw the frame

        # Draw fruits (apples)
        for fruit in fruits:
            fruit.draw(window, offset_x)  # Draw the fruit

        # Draw the score
        draw_score(window, font, score)  # Display the score on the screen

        # Draw the health bar
        draw_health_bar(window, font, player.health)  # Display the health on the screen
# Draw the timer and check if time runs out
        time_left = draw_timer(window, font, start_ticks)
        if time_left < 11:
            timer_sound.play()
        if time_left == 0:  # If time runs out, the game ends
            draw_end_screen(window, font)
            main(window)  # Restart the game after time runs out

        # Handle screen scrolling
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel  # Adjust the horizontal offset

        pygame.display.update()  # Update the display

    pygame.quit()  # Quit pygame
    quit()  # Exit the program

# Run the game
if __name__ == "__main__":
    main(window) 
