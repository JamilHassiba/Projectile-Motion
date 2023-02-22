import pygame
import pymunk
# import pymunk.pygame_util
from time import time
import math, random

# Initialize pygame
pygame.init()

vector = pygame.math.Vector2

# 1 meter = 44 pixels
METER = 44

# Set window width and height
WINDOW_WIDTH = 43 * METER
WINDOW_HEIGHT = 23 * METER

# Create the display surface and give it a caption
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Physics Simulation")

# Create the space and give it a gravity
space = pymunk.Space()
space.gravity = (0, 9.81 * METER)

# draw_options = pymunk.pygame_util.DrawOptions(display_surface)

# Set the FPS and clock
FPS = 60
clock = pygame.time.Clock()

# Set the time step
dt = 1 / FPS


class Simulation():
    '''A class that manages the simulation'''
    
    def update(self):
        '''A function that keeps updating the simulation continuously'''
        
        self.remove_first_ball()
        self.remove_out()
    
    def remove_out(self):
        '''A function that removes any ball that leaves the right and left sides of the screen'''
        
        for ball in cannon.cannon_balls:
            
            if ball.rect.left > WINDOW_WIDTH or ball.rect.right < 0:
                
                ball.destroy()
                cannon.cannon_balls.remove(ball)
    
    def remove_first_ball(self):
        '''A function that removes the first ball if there are more than 4 balls on the screen to prevent lagging'''
        
        if len(cannon.cannon_balls) > 5:
            
            cannon.cannon_balls[0].destroy()
            cannon.cannon_balls.pop(0)
    
    def remove_balls(self):
        '''A function that destroys all balls'''
        
        for ball in cannon.cannon_balls:
            ball.destroy()
        
        cannon.cannon_balls = []


class Ground():
    '''A class that manages the ground'''
    
    def __init__(self):
        
        self.width, self.height = WINDOW_WIDTH, METER * 4
        self.position = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - self.height // 2)
        
        # Create a static body and position it
        body = pymunk.Body(body_type = pymunk.Body.STATIC)
        body.position = self.position
        
        # Give the body the shape of a rectangle and give it a collision ID
        shape = pymunk.Poly.create_box(body, (self.width, self.height))
        shape.collision_type = 0
        space.add(body, shape)
    
    def draw(self):
        '''A function that draws the ground'''
        
        # Attach a grass image on the rectangle and blit it on the display_surface
        image = pygame.transform.scale(pygame.image.load("earth.png").convert_alpha(), (self.width, self.height))
        rect = image.get_rect(center = self.position)
        display_surface.blit(image, rect)


class CannonBall():
    '''A class that creates and manages a cannon ball'''
    
    def __init__(self, radius, mass, id):
        
        self.radius = radius
        self.diameter = radius * 2
        self.mass = mass
        self.id = id
        
        self.particles = []
        self.particle_size = 3
        self.particle_color = 'blue'#random.sample(('blue', 'purple', 'orange', 'dark green', 'red', 'yellow'), 1).pop()
        
        self.max_height = 0
        self.range = 0
        self.time = 0
        
        self.in_air = False
        self.show_vectors = False
        
        # Create a dynamic body, position it, and calculate its moment of inertia
        self.moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, self.moment, pymunk.Body.DYNAMIC)
        self.body.position = (cannon.center.x, cannon.center.y)
        
        # Give the body the shape of a circle and a collision ID
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.collision_type = self.id
        
        # Give the ball a filter of 1 so that any created ball would have the same number and therefore they won't be able to collide with each other
        self.shape.filter = pymunk.ShapeFilter(1)
        space.add(self.body, self.shape)
    
    def update(self):
        '''A function that updates the ball's position'''
        
        if self.in_air:
            calc_max_height(self)
            calc_range(cannon, self)
            calc_time(self)
    
    def draw(self):
        '''A function that draws the ball and its trail'''
        
        self.draw_ball()
        self.draw_trail()
    
    def draw_ball(self):
        '''A function that draws the ball'''
        
        # Attach a cannon ball image on top of the circle and make it move with it
        self.image = pygame.transform.scale(pygame.image.load("clown.png").convert_alpha(), (self.diameter, self.diameter))
        self.rect = self.image.get_rect(center = (self.body.position.x, self.body.position.y))
        display_surface.blit(self.image, self.rect)
    
    def draw_trail(self):
        '''A function that creates the trail and draws it'''
        
        # Create the trail's particles and add them to the particles' list if the ball is in the air
        if self.in_air:
            self.particles.append(pygame.Rect(self.rect.centerx - self.particle_size / 2, self.rect.centery - self.particle_size / 2, self.particle_size, self.particle_size))
        
        # Draw the particles in the particles' list
        for particle in self.particles:
            pygame.draw.rect(display_surface, pygame.Color(self.particle_color), particle)
    
    def launch(self, velocity, angle):
        '''A function that launches the ball'''
        
        # Calculate the x and y velocity components
        velocity_x = velocity * math.cos(math.radians(angle)) * METER
        velocity_y = velocity * math.sin(math.radians(angle)) * METER
        
        # Launch the ball and start the timer
        self.body.velocity = (velocity_x, -velocity_y)
        self.start = time()
        
        self.in_air = True
    
    def ground_collision(self, arbiter, space, data):
        '''A function that manages the ball when it collides with the ground'''
        
        # Make the ball's velocity zero
        self.body.velocity = (0, 0)
        self.in_air = False
        
        print(self.max_height/METER, self.range/METER, self.time)
        
        # Return True so that the ball wouldn't go through the ground
        return True
    
    def destroy(self):
        '''A function that destroys the ball'''
        
        # Delete the particles
        self.particles = []
        
        # Delete the ball
        space.remove(self.shape, self.body)
        self.shape = None
        self = None


class Cannon():
    '''A class that manages the cannon and its movement'''
    
    def __init__(self):
        
        self.angle = 0
        self.cannon_balls = []
        self.ball_id = 1
        self.center = vector(200, WINDOW_HEIGHT - 5 * METER)
        self.offset = vector(80, 0)
        
        # Create a cannon image and position it
        self.image = pygame.transform.flip(pygame.transform.scale(pygame.image.load("Cannon Ball\PNG\cannon.png").convert_alpha(), (200, 89)), False, True)
        self.rect = self.image.get_rect(center = self.center + self.offset)
        
        # Create a copy of the cannon as a reference image when rotating
        self.ref_image = self.image.copy()
        self.ref_rect = self.ref_image.get_rect(center = self.center)
    
    def update(self):
        '''A function that updates the cannon's position'''
        
        # Rotate the cannon
        self.rotate_check()
        self.rotate()
    
    def draw(self):
        '''A function that draws the cannon'''
        
        display_surface.blit(self.image, self.rect)
        pygame.draw.circle(display_surface, (30, 250, 70), self.center, 3)
    
    def rotate_check(self):
        
        # Get the coordinates of the mouse position
        self.mouse = vector(pygame.mouse.get_pos())
        
        # If the mouse is not clicked set can_rotate to False to prevent the cannon from rotating
        if not pygame.mouse.get_pressed()[0]:
            self.can_rotate = False
        
        # Else if the mouse was colliding with the cannon and was not colliding with the tape rotate the cannon 
        elif self.rect.collidepoint(self.mouse) and not tape.can_move_tape and not tape.can_move_end:
            self.can_rotate = True
    
    def rotate(self):
        '''A function that rotates the cannon if it can rotate'''
        
        if self.can_rotate:
            
            # Calculate the distance from the mouse to the cannon
            distance_x = self.mouse.x - self.center.x
            distance_y = self.mouse.y - self.center.y
            
            # Calculate the angle
            self.angle = math.degrees(math.atan2(-distance_y, distance_x))
            
            # Rotate the offset (-angle because it's a vector)
            rotated_offset = self.offset.rotate(-self.angle)
            
            # Rotate the image according to the reference image (image copy) move it by the offset
            self.image = pygame.transform.rotozoom(self.ref_image, self.angle, 1)
            self.rect = self.image.get_rect(center = self.ref_rect.center + rotated_offset)
    
    def shoot(self):
        '''A function that shoots cannon balls from the cannon'''
        
        # Create a ball with a unique ID and add it to the cannon balls' array
        ball = CannonBall(METER / 2, 10, self.ball_id)
        self.cannon_balls.append(ball)
        
        # Launch the ball
        ball.launch(16, self.angle)
        
        # Keep calling the ball's ground_collision function
        handler = space.add_collision_handler(0, self.ball_id)
        handler.begin = ball.ground_collision
        
        # Change the ball ID
        self.ball_id += 1


class Tape():
    '''A class that manages the measuring tape'''
    
    def __init__(self):
        
        self.start_pos = vector(500, 500)
        self.end_pos = vector(self.start_pos.x + METER, self.start_pos.y)
        
        self.length = self.start_pos.distance_to(self.end_pos)
        self.angle = math.degrees(math.atan2(-(self.end_pos.y - self.start_pos.y), (self.end_pos.x - self.start_pos.x)))
        
        self.start_image = pygame.transform.scale(pygame.image.load('plus.png').convert_alpha(), (45, 45))
        self.start_rect = self.start_image.get_rect(center = self.start_pos)
        
        self.ref_start = self.start_image.copy()
        self.ref_start_rect = self.start_image.get_rect(center = self.start_pos)
        
        self.end_image = self.start_image.copy()
        self.end_rect = self.end_image.get_rect(center = self.end_pos)
        
        self.ref_end = self.end_image.copy()
        self.ref_end_rect = self.end_image.get_rect(center = self.end_pos)
        
        self.offset = vector(-26, -26)
        
        self.tape_image = pygame.transform.scale(pygame.image.load("tape.png"), (104, 120))
        self.tape_rect = self.tape_image.get_rect(center = self.start_rect.center)
        
        self.tape_ref = self.tape_image.copy()
        self.tape_ref_rect = self.tape_image.get_rect(center = self.start_rect.center)
    
    def update(self):
        '''A function that keeps updating the tape's shape and position continuously'''
        
        self.move_check()
        self.move_tape()
        self.move_end()
    
    def draw(self):
        '''A function that draws the tape, the start plus, the end plus, and the line between them'''
        
        pygame.draw.line(display_surface, pygame.Color("grey43"), self.start_pos, self.end_pos, 3)
        display_surface.blit(self.tape_image, self.tape_rect)
        display_surface.blit(self.start_image, self.start_rect)
        display_surface.blit(self.end_image, self.end_rect)
    
    def move_check(self):
        '''A function to check if the tape can be moved'''
        
        # Get the coordinates of the mouse position
        self.mouse = vector(pygame.mouse.get_pos())
        
        # If the mouse is not clicked set can_move_tape and can_move_end to False to prevent the tape from moving
        if not pygame.mouse.get_pressed()[0]:
            
            self.can_move_tape = False
            self.can_move_end = False
        
        # Else if the mouse was colliding with the end of the tape and was not colliding with the tape nor the cannon move the end of the tape 
        elif self.end_rect.collidepoint(self.mouse) and not self.can_move_tape and not cannon.can_rotate:
            self.can_move_end = True
        
        # If the mouse was clicked and it collided with the end of the tape and it wasn't colliding with the tape, can_move_end will be set to True 
        # thus the end of the tape can be moved. However, if the mouse was still clicked but it wasn't colliding anymore with the end of the tape or 
        # the mouse was still clicked but it also collided with the tape, can_move_end will still be True because it will only be False if the mouse was released.
        # This will alow the end of the tape to keep moving as long as the mouse clicked it even if the mouse wasn't colliding with it anymore due to its fast motion
        # and even if it also collided with the tape because this will cause the tape to also move with te mouse. (Same logic for the tape)
        
        # Note: the collision between the end of the tape and the mouse is checked before the collision between the tape and the mouse is because the end of the tape
        # will be on top of the tape if they overlapped so the end collision is checked is checked first so that only the end of the tape will be moved when the mouse 
        # is clicked
        
        # Else if the mouse was colliding with the tape and was not colliding with the end of the tape nor the cannon move the tape 
        elif  self.start_rect.collidepoint(self.mouse) and not self.can_move_end and not cannon.can_rotate:
            self.can_move_tape = True
    
    def move_tape(self):
        '''A function that moves the tape if it can be moved'''
        
        if  self.can_move_tape:
            
            # Make the start position equal to the mouse position and update the start plus, the tape, and the reference tape rects
            self.start_pos = self.mouse
            self.start_rect.center = self.start_pos
            self.tape_rect.center = self.start_rect.center
            
            # Calculate the the end x and y positions using trigonometry (the minus in end_y is because the position is inverted in pygame)
            self.end_pos.x = self.start_pos.x + math.cos(math.radians(self.angle)) * self.length
            self.end_pos.y = self.start_pos.y - math.sin(math.radians(self.angle)) * self.length
            
            # Update the end plus rect
            self.end_rect.center = self.end_pos
    
    def move_end(self):
        '''A function that moves the end position of the tape if it can be moved'''
        
        if self.can_move_end:
            
            # Make the end position equal to the mouse position and update the end plus rect
            self.end_pos = self.mouse
            self.end_rect.center = self.end_pos
            
            # Calculate the length and angle of the line
            self.length = self.start_pos.distance_to(self.end_pos)
            self.angle = math.degrees(math.atan2(-(self.end_pos.y - self.start_pos.y), (self.end_pos.x - self.start_pos.x)))
            
            self.start_image = pygame.transform.rotozoom(self.ref_start, self.angle, 1)
            self.start_rect = self.start_image.get_rect(center = self.start_rect.center)
            
            self.end_image = pygame.transform.rotozoom(self.ref_end, self.angle, 1)
            self.end_rect = self.end_image.get_rect(center = self.end_rect.center)
            
            # Rotate the offset (-angle because it's a vector)
            self.offset.rotate(-self.angle)
            
            # # Rotate the tape
            self.tape_image = pygame.transform.rotozoom(self.tape_ref, self.angle, 1)
            self.tape_rect = self.tape_image.get_rect(center = self.start_rect.center)


def calc_max_height(ball):
        
        # Calculate the maximum height
        current_height = (WINDOW_HEIGHT - 2 * METER) - ball.rect.centery
        
        if current_height > ball.max_height:
            ball.max_height = current_height

def calc_range(cannon, ball):
    
    current_range = ball.rect.centerx - cannon.rect.centery
    
    if current_range > ball.range:
        ball.range = current_range

def calc_time(ball):
    
    stop = time()
    ball.time = stop - ball.start


# Create the sprites and a simulation object (order matters)
simulation = Simulation()
grass = Ground()
tape = Tape()
cannon = Cannon()


running = True
while running:
    
    # Get the game events
    for event in pygame.event.get():
        
        # break the loop if the player quits
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        
        # Launch the ball if the player presses the space button
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            cannon.shoot()
        
        # Remove all balls if the player presses the 'C' button
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            simulation.remove_balls()
    
    # change the color of the screen
    display_surface.fill(pygame.Color("cadetblue2"))
    
    # Draw and update the sprites and the simulation (order matters)
    
    if cannon.cannon_balls:
        for ball in cannon.cannon_balls:
            ball.draw()
            ball.update()
    
    grass.draw()
    cannon.draw()
    tape.draw()
    
    simulation.update()
    tape.update()
    cannon.update()
    
    # Update the space once every second
    space.step(dt)
    # space.debug_draw(draw_options)
    
    # Update the display and tick the clock 
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()