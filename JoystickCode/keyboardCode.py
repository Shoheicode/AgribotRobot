# import pygame
# import serial
# import time
# import sys

# # Configure serial port
# ser = serial.Serial("COM3", 115200)  # Replace COM4 with your ESP32 port
# time.sleep(2)

# # Pygame setup
# pygame.init()
# screen = pygame.display.set_mode((300, 100))
# pygame.display.set_caption("ESP32 Motor Control")

# print("Keyboard control ready. Use W/S/X to send commands.")

# # Motor control state
# speed_value = 0
# current_direction = 0


# def send_command(speed, direction):
#     command = f"{speed},{direction}\n"
#     ser.write(command.encode())
#     print(f"Sent: {command.strip()}")


# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#         elif event.type == pygame.KEYDOWN:
#             print(f"Key pressed: {event.key}")
#             key = event.key

#             if key == pygame.K_w:
#                 current_direction = 1
#                 speed_value += 1
#                 if speed_value > 127:
#                     speed_value = 127
#                 send_command(speed_value, current_direction)

#             elif key == pygame.K_s:
#                 current_direction = -1
#                 speed_value -= 1
#                 if speed_value < 0:
#                     speed_value = 0
#                 send_command(speed_value, current_direction)

#             elif key == pygame.K_x:
#                 current_direction = 0
#                 send_command(0, current_direction)

#             elif key == pygame.K_ESCAPE:
#                 running = False

# # Clean up
# ser.close()
# pygame.quit()
# sys.exit()

import pygame
import serial
import time
import sys

# Setup serial to ESP32
ser = serial.Serial("COM3", 115200)  # Adjust COM port
time.sleep(2)

pygame.init()
screen = pygame.display.set_mode((300, 100))
pygame.display.set_caption("Dual Motor Control")

print("Hold W/S to move both. A/D for turns. X to stop. ESC to quit.")

speed_value = 5000
last_sent = ""

clock = pygame.time.Clock()


def send_command(speed1, speed2):
    global last_sent
    command = f"{speed1},{speed2}\n"
    if command != last_sent:
        ser.write(command.encode())
        print(f"Sent: {command.strip()}")
        last_sent = command


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    spd1, spd2 = 0, 0

    if keys[pygame.K_w]:
        spd1 = spd2 = speed_value
    elif keys[pygame.K_s]:
        spd1 = spd2 = -speed_value
    elif keys[pygame.K_a]:
        spd1 = -speed_value
        spd2 = speed_value
    elif keys[pygame.K_d]:
        spd1 = speed_value
        spd2 = -speed_value
    elif keys[pygame.K_x]:
        spd1 = spd2 = 0

    send_command(spd1, spd2)

    if keys[pygame.K_ESCAPE]:
        running = False

    clock.tick(20)

ser.close()
pygame.quit()
sys.exit()
