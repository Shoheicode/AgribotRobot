import pygame
import serial
import time
import sys

# Setup serial to ESP32
ser = serial.Serial("COM3", 115200)  # Adjust COM port
time.sleep(2)

pygame.init()
pygame.joystick.init()

# Initialize the first connected joystick
if pygame.joystick.get_count() == 0:
    print("No joystick detected.")
    sys.exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick connected: {joystick.get_name()}")

WIDTH, HEIGHT = 600, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Joystick Motor Control")

print("Use left stick to control. ESC to quit.")

last_sent = ""
clock = pygame.time.Clock()

# Maximum motor power (scale to 0–127)
MAX_POWER = 32

# Circle settings
circle_radius = 20
outer_radius = 30
center_x, center_y = WIDTH // 2, HEIGHT // 2


def send_command(speed1, speed2):
    global last_sent
    # Round and format speeds
    s1 = int(speed1)
    s2 = int(speed2)
    command = f"{s1},{s2}\n"
    if command != last_sent:
        ser.write(command.encode())
        print(f"Sent: {command.strip()}")
        last_sent = command


# Set up font (name, size)
font = pygame.font.SysFont(None, 24)  # None uses default font

# Create a text surface (text, antialias, color)
text_surface = font.render("Hello, Pygame!", True, (255, 255, 255))  # White text

# Get the rectangle of the text surface and center it
text_rect = text_surface.get_rect(center=(250, 150))

enc1 = 0
enc2 = 0


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        running = False

    # Read joystick axes
    pygame.event.pump()
    axis_y = joystick.get_axis(1)  # Forward/backward (invert so up = +)
    axis_y2 = joystick.get_axis(3)  # Right stick Y (optional, for additional control)
    # axis_x = joystick.get_axis(0)  # Left/right

    # Tank drive mixing
    left_power = (axis_y) * MAX_POWER
    right_power = (axis_y2) * MAX_POWER

    if abs(left_power) < 2:
        left_power = 0
    if abs(right_power) < 2:
        right_power = 0

    # Clamp values to range [-100, 100]
    left_power = max(-MAX_POWER, min(MAX_POWER, left_power))
    right_power = max(-MAX_POWER, min(MAX_POWER, right_power))

    send_command(left_power, right_power)

    screen.fill((0, 0, 0))  # 🔄 Clear previous frame

    # Create a text surface (text, antialias, color)
    text_left = font.render(
        "Left Power:" + "{:.2f}".format(left_power / 127), True, (255, 255, 255)
    )  # White text
    text_right = font.render(
        "Right Power:" + "{:.2f}".format(right_power / 127), True, (255, 255, 255)
    )  # White text

    # Get the rectangle of the text surface and center it
    text_L = text_left.get_rect(center=(150, 100))
    text_R = text_right.get_rect(center=(350, 100))

    if ser.in_waiting:
        try:
            line = ser.readline().decode().strip()
            if line.startswith("ENCODER"):
                _, enc1a, enc2a = line.split(",")
                print(f"Encoder M1: {enc1a}, M2: {enc2a}")
                enc1 = int(enc1a)
                enc2 = int(enc2a)
            print(f"Received: {line}")
        except Exception as e:
            print(f"Failed to read: {e}")

    # Create a text surface (text, antialias, color)
    text_leftE = font.render(
        "Left Encoder:" + str(enc1),
        True,
        (255, 255, 255),
    )  # White text
    text_rightE = font.render(
        "Right Encoder:" + str(enc2),
        True,
        (255, 255, 255),
    )  # White text
    # Get the rectangle of the text surface and center it
    text_LE = text_leftE.get_rect(center=(150, 300))
    text_RE = text_rightE.get_rect(center=(350, 300))
    screen.blit(text_leftE, text_LE)  # Draw text
    screen.blit(text_rightE, text_RE)  # Draw text

    # print(f"Left: {left_power}, Right: {right_power}")
    screen.blit(text_left, text_L)  # Draw text
    screen.blit(text_right, text_R)  # Draw text

    # Map from [-1, 1] to vertical position on screen
    pos_y_left = int(center_y + axis_y * (circle_radius))
    pos_y_right = int(center_y + axis_y2 * (circle_radius))

    # X positions for left and right sticks
    pos_x_left = WIDTH // 4
    pos_x_right = 3 * WIDTH // 4

    pygame.draw.circle(
        screen, (255, 0, 0), (pos_x_left, center_y), outer_radius, 1
    )  # Draw left outer circle
    pygame.draw.circle(
        screen, (255, 0, 0), (pos_x_right, center_y), outer_radius, 1
    )  # Draw right outer circle

    # Draw the circles
    pygame.draw.circle(screen, (0, 255, 0), (pos_x_left, pos_y_left), circle_radius)
    pygame.draw.circle(screen, (0, 0, 255), (pos_x_right, pos_y_right), circle_radius)

    pygame.display.flip()  # Update display
    clock.tick(30)

ser.close()
pygame.quit()
sys.exit()
