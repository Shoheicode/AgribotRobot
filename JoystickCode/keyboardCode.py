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

speed_value = 30
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
