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

screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Joystick Motor Control")

print("Use left stick to control. ESC to quit.")

last_sent = ""
clock = pygame.time.Clock()

# Maximum motor power (scale to 0–100)
MAX_POWER = 32


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
                _, enc1, enc2 = line.split(",")
                print(f"Encoder M1: {enc1}, M2: {enc2}")
            # Create a text surface (text, antialias, color)
            text_leftE = font.render(
                "Left Encoder:" + str(enc1),
                True,
                (255, 255, 255),
            )  # White text
            text_rightE = font.render(
                "Right Encoder:" + str(enc1),
                True,
                (255, 255, 255),
            )  # White text
            # Get the rectangle of the text surface and center it
            text_LE = text_leftE.get_rect(center=(150, 100))
            text_RE = text_rightE.get_rect(center=(350, 100))
            screen.blit(text_leftE, text_LE)  # Draw text
            screen.blit(text_rightE, text_RE)  # Draw text
        except Exception as e:
            print(f"Failed to read: {e}")

    # print(f"Left: {left_power}, Right: {right_power}")
    screen.blit(text_left, text_L)  # Draw text
    screen.blit(text_right, text_R)  # Draw text

    pygame.display.flip()  # Update display
    clock.tick(30)

ser.close()
pygame.quit()
sys.exit()
