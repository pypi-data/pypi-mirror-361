import pygame
from math import cos, sin, radians
from sys import platform, exit
from enum import Enum
from functools import partial

CLOCK_TICK = 30

# Utility to get a list of possible fonts that can be used
def print_drawly_fonts():
    print("Fonts Available to Use in Your Program")
    print("Note: This lists fonts on the system, which may not be available on all systems")
    print(pygame.font.get_fonts())

# Create a global object for the file to hold all state data
class Data:
    def __init__(self):
        self.ms = 1000
        self.color = "black"
        self.text_color = "black"
        self.screen = None
        self.background = "white"
        self.poly_width = 0
        self.poly_points = []
        self.draw_list = []
        self.background_list = []
        self.draw_background = False
        self.dimensions = None
        self.terminal = None
        self.terminal_lines = None
        self.terminal_line_height = None
        self.terminal_msg = []
        self.clock = pygame.time.Clock()
        self.first_draw = True # don't delay on first time drawing


# Global object to store state
data = Data()


# Enum for rotating rectangles to identify the rotation point
class RotationPoint(Enum):
    '''
        Rotation points specifies the point about which an object will be rotated

        Attributes:
            BOTTOM_LEFT
            BOTTOM_RIGHT
            TOP_LEFT
            TOP_RIGHT
            CENTER
    '''
    BOTTOM_LEFT = 0
    '''Rotate about the bottom left corner'''
    BOTTOM_RIGHT = 1
    '''Rotate about the bottom right corner'''
    TOP_RIGHT = 2
    '''Rotate about the top right corner'''
    TOP_LEFT = 3
    '''Rotate about the top left corner'''
    CENTER = 4
    '''Rotate about the center'''


# First call always made
def start(title="Welcome to Drawly", dimensions=(1280, 720), background="white", terminal=False, terminal_lines=8, terminal_line_height=25):
    """
        Must be called before any other Drawly functions in order to create the window.

        Args:
            title (str): (Optional) Title of the Drawly window
            dimensions ((int, int)): (Optional) Tuple of the dimensions of the window. 1280x720 default
            background (str): (Optional) Background color of the window. White by default
            terminal (bool): (Optional) Determins if the terminal window should be shown or not. False by default
            terminal_lines (int): (Optional) Number of lines for the terminal for input and output at the bottom of the window. 8 by default
            terminal_line_height (int): (Optional) Height of a single line in the terminal. 25 by default
    """
    data.terminal = terminal
    if not terminal:
        data.terminal_lines = 0
    else:
        data.terminal_lines = terminal_lines
    data.terminal_line_height = terminal_line_height
    data.dimensions = (dimensions[0], dimensions[1] + data.terminal_lines * data.terminal_line_height)
    data.background = background
    pygame.init()
    data.screen = pygame.display.set_mode(data.dimensions)
    data.screen.fill(background)
    pygame.display.set_caption(title)
    draw_terminal()

# Change the speed at which paint draws. Sets the approximate frame rate. The draw() functions will not
# draw faster than the frame rate
def set_speed(speed):
    """
        Set the speed for drawing. Each time draw() or redraw() is called there will be a delay based on
            the speed value. 1 is slow, approximately 1 frame every 2 seconds. 10 is approximately 30 frames per second
        Args:
            speed (int): Rate at which drawings are rendered on the screen
    """
    if speed < 1:
        speed = 1
    elif speed > 10:
        speed = 10
    data.ms = 33 + 197 * (10 - speed)


# Change the color that will be used
def set_color(new_color):
    """
        Change the color for future drawings.

        Args:
            new_color (str): Color to use
    """
    data.color = new_color


# Draw all items that have been created since the last call to paint()
def draw():
    """
        Draws all items created since the last call of draw()
    """
    do_draw(False)


# Erase all items then draw new items that have been created since the last call to draw()
def redraw():
    """
        Draws all items created since the last call of draw()
    """
    do_draw(True)


def do_draw(refresh):
    # See if the user closed the window
    for event in pygame.event.get():
        check_exit_event(event)

    if not data.first_draw: # Don't pause on first draw
        pygame.time.wait(data.ms)
    else:
        data.first_draw = False

    # Clear the screen and draw the background on a redraw
    if refresh:
        data.screen.fill(data.background)
        for i in data.background_list:
            i()

    # Draw the current list of items since last draw
    for i in data.draw_list:
        i()
    data.draw_list.clear()

    # Draw the terminal on top of the rest of the screen
    draw_terminal()

def draw_terminal():
    # Draw the terminal area of the window
    if data.terminal:
        pygame.draw.rect(data.screen, "black",
                         pygame.Rect(0, data.dimensions[1] - data.terminal_lines * data.terminal_line_height,
                                     data.dimensions[0], data.terminal_lines * data.terminal_line_height))

        for i in range(data.terminal_lines):
            if i < len(data.terminal_msg):
                text_font = pygame.font.SysFont("courier", data.terminal_line_height - 4).render(data.terminal_msg[i],
                                                                                                 True, "white")
                data.screen.blit(text_font, (10, data.dimensions[1] - (1 + i) * data.terminal_line_height))

    # Call this here because draw_terminal() is always called last
    pygame.display.flip()

# draw a circle with a center at x_pos, y_pos
def circle(x_pos, y_pos, radius, stroke=0):
    """
        Creates a circle to be drawn on the screen. The circle will be drawn the next time draw() is called.


        Args:
            x_pos (int): X-coordinate of the center of the circle
            y_pos (int): Y-coordinate of the center of the circle
            radius (int): Radius of the circle
            stroke (int): (Optional) Default is 0, which is a filled circle. Otherwise is the size of outline stroke
    """
    add_draw_item(partial(pygame.draw.circle, data.screen, data.color, [x_pos, y_pos], radius, width=stroke))


# Draw a rectangle with an optional rotation and rotation point
"""
    Borrowed some of this code from online and will credit if I ever find the place again. :)
    - rotation_angle: in degree
    - rotation_offset_center: moving the center of the rotation: (-100,0) will turn the rectangle around a point 100 above center of the rectangle,
                                         if (0,0) the rotation is at the center of the rectangle
    - nAntialiasingRatio: set 1 for no antialising, 2/4/8 for better aliasing
"""


def rectangle(x_pos, y_pos, width, height, stroke=0, rotation_angle=0, rotation_point=RotationPoint.CENTER):
    """
        Creates a rectangle to be drawn on the screen.

        Args:
            x_pos (int): X-coordinate of the top left of the unrotated rectangle
            y_pos (int): Y-coordinate of the top left of the unrotated rectangle
            width (int): Width of the unrotated rectangle (x-direction)
            height (int): Height of the unrotated rectangle (y-direction)
            stroke (int): 0 for a filled rectangle. > 0 is  the width of the line drawn. Default is 0.
            rotation_angle (int): Degrees to rotate the rectangle. Default is 0
            rotation_point: (RotationPoint): Point to rotate the rectangle about
    """
    nRenderRatio = 8

    # the rotation point is relative to the center of the rectangle
    if rotation_point == RotationPoint.CENTER:
        rotation_offset_center = (0, 0)
    elif rotation_point == RotationPoint.BOTTOM_LEFT:
        rotation_offset_center = (-width // 2, height // 2)
    elif rotation_point == RotationPoint.BOTTOM_RIGHT:
        rotation_offset_center = (width // 2, height // 2)
    elif rotation_point == RotationPoint.TOP_RIGHT:
        rotation_offset_center = (width // 2, -height // 2)
    elif rotation_point == RotationPoint.TOP_LEFT:
        rotation_offset_center = (-width // 2, -height // 2)
    else:  # manually enter a point as a tuple
        x_pt, y_pt = rotation_point
        rotation_offset_center = (x_pt - x_pos - width // 2, y_pt - y_pos - height // 2)

    sw = width + abs(rotation_offset_center[0]) * 2
    sh = height + abs(rotation_offset_center[1]) * 2

    surfcenterx = sw // 2
    surfcentery = sh // 2
    s = pygame.Surface((sw * nRenderRatio, sh * nRenderRatio))
    s = s.convert_alpha()
    s.fill((0, 0, 0, 0))

    rw2 = width // 2  # halfwidth of rectangle
    rh2 = height // 2

    pygame.draw.rect(s, data.color, ((surfcenterx - rw2 - rotation_offset_center[0]) * nRenderRatio,
                                     (surfcentery - rh2 - rotation_offset_center[1]) * nRenderRatio,
                                     width * nRenderRatio,
                                     height * nRenderRatio), stroke * nRenderRatio)
    s = pygame.transform.rotate(s, rotation_angle)
    if nRenderRatio != 1: s = pygame.transform.smoothscale(s, (
        s.get_width() // nRenderRatio, s.get_height() // nRenderRatio))
    incfromrotw = (s.get_width() - sw) // 2
    incfromroth = (s.get_height() - sh) // 2
    add_draw_item(partial(data.screen.blit, s, (x_pos - surfcenterx + rotation_offset_center[0] + rw2 - incfromrotw,
                                                y_pos - surfcentery + rotation_offset_center[1] + rh2 - incfromroth)))


# Draw a line with a starting point, length, and angle. The angle is the heading given in degrees based on the unit circle
def vector(x_pos, y_pos, length, angle=0, stroke=1):
    """
        Draws a line based on a starting point, length, angle, and stroke size (width of line)

        Args:
            x_pos (int): X-coordinate of the start of the line
            y_pos (int): Y-coordinate of the start of the line
            length (int): Length of the line to draw
            angle (int): (Optional) Direction of line in degrees. 0 degrees is horizontal to the right. Default is 0
            stroke (int): (Optional) Width of the line drawn. Default is 1
    """
    end_x = x_pos + length * cos(radians(-angle))  # use negative to match with unit circle
    end_y = y_pos + length * sin(radians(-angle))
    add_draw_item(partial(pygame.draw.line, data.screen, data.color, (x_pos, y_pos), (end_x, end_y), stroke))


# Draw a line with a starting point and end point
def line(x_pos1, y_pos1, x_pos2, y_pos2, stroke=1):
    """
       Draws a line based on a starting point, end point, and stroke size (width of line)

       Args:
           x_pos1 (int): X-coordinate of the start of the line
           y_pos1 (int): Y-coordinate of the start of the line
           x_pos2(int): X-coordinate of the end of the line
           y_pos2 (int): Y-coordinate of the end of the line
           stroke (int): (Optional) Width of the line drawn. Default is 1
   """
    add_draw_item(partial(pygame.draw.line, data.screen, data.color, (x_pos1, y_pos1), (x_pos2, y_pos2), stroke))


# Call when starting to define a polygon. Width=0 is filled. Otherwise is a stroke size
def polygon_begin(stroke=0):
    """
       Call to begin creating a polygon. Call add_poly_points to create the polygon

       Args:
           stroke (int): 0 for a filled rectangle. > 0 is  the width of the line drawn. Default is 0.
   """
    data.poly_width = stroke
    data.poly_points.clear()


# Add points for the polygon. Must be called after begin and before end
def add_poly_point(x_pos, y_pos):
    """
       Add a point to the polygon to be drawn.

       Args:
           x_pos (int): X-position of the point to add
           y_pos (int): Y-position of the point to add
   """
    data.poly_points.append([x_pos, y_pos])


# Call after adding points to the polygon to draw it
def polygon_end():
    """
        Call to end the creation of the polygon.
    """
    add_draw_item(partial(pygame.draw.polygon, data.screen, data.color, data.poly_points.copy(), data.poly_width))


# Define a rectangle that an ellipse will fit in.
def ellipse(x_pos, y_pos, width, height, stroke=0):
    """
       Draws an ellipse inside of the defined rectangle

       Args:
            x_pos (int): X-coordinate of the top left
            y_pos (int): Y-coordinate of the top left
            width (int): Width of the rectangle (x-direction)
            height (int): Height of the rectangle (y-direction)
            stroke (int): 0 for a filled rectangle. > 0 is  the width of the line drawn. Default is 0.
    """
    add_draw_item(partial(pygame.draw.ellipse, data.screen, data.color, (x_pos, y_pos, width, height), stroke))


# Define a rectangle that an ellipse will fit in. Start and end are the degree points where the line will be drawn
def arc(x_pos, y_pos, width, height, start, end, stroke=1):
    """
       Draws an ellipse arc inside of the defined rectangle

       Args:
            x_pos (int): X-coordinate of the top left
            y_pos (int): Y-coordinate of the top left
            width (int): Width of the rectangle (x-direction)
            height (int): Height of the rectangle (y-direction)
            start (int): Degree point on arc to begin drawing
            end (int): Degree point on arc to end drawing
            stroke (int): 0 for a filled rectangle. > 0 is  the width of the line drawn. Default is 0.
    """
    add_draw_item(
        partial(pygame.draw.arc, data.screen, data.color, (x_pos, y_pos, width, height), radians(start), radians(end),
    stroke))


# Write some text.
def text(x_pos, y_pos, text, size=20, font="courier"):
    """
       Draws text on the screen.

       Args:
            x_pos (int): X-coordinate of the top left of the text
            y_pos (int): Y-coordinate of the top left of the text
            text (str): Text to write
            size (int): (Optional) Font size. Default is 20
    """
    text_font = pygame.font.SysFont(font, size).render(text, True, data.color)
    add_draw_item(partial(data.screen.blit, text_font, (x_pos, y_pos)))

# Call when adding items to the background image
def background_begin():
    data.draw_background = True


# Call when done adding items to the background image
def background_end():
    data.draw_background = False


# Add a drawing function to the appropriate list
def add_draw_item(draw_function):
    if data.draw_background:
        data.background_list.append(draw_function)
    data.draw_list.append(draw_function)

# Display a message and continue on with the program. Message stays until this or terminal_input is called again
# Terminal variable in Data object must be true for this to work
def terminal_output(*msg):
    """
       Prints a single line of output on the terminal. Terminal variable must be > 0 when calling start().

       Args:
            msg (string): (Optional) String to print. No parameter prints a blank line. Can be comma separated strings
    """
    if not data.terminal:
        print("Terminal Error: Terminal is not enabled")
        return

    tmp_msg = ""
    for i in msg:
        if tmp_msg != "":
            tmp_msg += " "
        tmp_msg += i.replace("\t", "    ")
    data.terminal_msg.insert(0, tmp_msg)

    draw_terminal()

# Display the prompt and wait for the user to enter a string and hit return
# Terminal variable in Data object must be true for this to work
def terminal_input(*prompt):
    """
       Prompts user for input in the terminal section. Terminal variable must be > 0 when calling start().

       Args:
            prompt (string): String to print before prompting for user input
    """
    if not data.terminal:
        print("Terminal Error: Terminal is not enabled")
        return "-1"

    data.terminal_msg.insert(0, "")
    draw()
    tmp_prompt = ""
    for i in prompt:
        if tmp_prompt != "":
            tmp_prompt += " "
        tmp_prompt += i.replace("\t", "    ")

    msg = ""
    cursor_cnt = 0
    cursor = "|"
    active = True
    while active:
        cursor_cnt += 1
        for event in pygame.event.get():
            check_exit_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    ### Do Stuff to Reset Game ###
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    if len(msg) > 0:
                        msg = msg[:-1]
                else:
                    msg += event.unicode

        if cursor_cnt // 10 % 2 == 0:
            cursor = ""
        else:
            cursor = "|"

        # Just drawing the line that accepts input
        pygame.draw.rect(data.screen, "black", pygame.Rect(0, data.dimensions[1] - data.terminal_line_height, data.dimensions[0], data.terminal_line_height))
        text_font = pygame.font.SysFont("courier", data.terminal_line_height - 4).render(tmp_prompt + msg + cursor, True, "white")
        data.screen.blit(text_font, (10, data.dimensions[1] - data.terminal_line_height))
        pygame.display.flip()
        data.clock.tick(CLOCK_TICK)

    data.terminal_msg[0] = tmp_prompt + msg
    data.first_draw = True # Remove delay on next draw after input
    return msg

# Display a message and continue on with the program. Message stays until this or terminal_input is called again
# Terminal variable in Data object must be true for this to work
def terminal_clear():
    """
       Clears the terminal window
    """
    if not data.terminal:
        print("Terminal Error: Terminal is not enabled")
        return

    data.terminal_msg = []
    draw_terminal()

# Call when done so window doesn't close. Click on X to close
def done():
    """
       Call at the end of the program so the window stays until it is closed by the user
    """
    while True:
        # Keep polling until an exit event happens
        event = pygame.event.wait()  # Non-busy wait
        check_exit_event(event)


# Close window on appropriate event
def check_exit_event(event):
    close = False
    if event.type == pygame.QUIT:
        # User clicks window close button
        close = True
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            # User clicks escape key
            close = True
        if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # User hits Ctrl+C
            close = True

    if close:
        pygame.quit()
        exit()