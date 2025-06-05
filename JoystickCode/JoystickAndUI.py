import pygame
import serial
import time
import sys
import math

# Setup serial to ESP32
try:
    ser = serial.Serial("COM3", 115200)  # Adjust COM port
    time.sleep(2)
    connection_status = True
except:
    ser = None
    connection_status = False

pygame.init()
pygame.joystick.init()

# Initialize the first connected joystick
if pygame.joystick.get_count() == 0:
    print("No joystick detected.")
    joystick = None
else:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick connected: {joystick.get_name()}")

# Display settings
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle Control Interface")

# Colors
DARK_BG = (20, 20, 30)
PANEL_BG = (40, 45, 60)
ACCENT_COLOR = (0, 180, 255)
SUCCESS_COLOR = (0, 255, 150)
WARNING_COLOR = (255, 180, 0)
DANGER_COLOR = (255, 80, 80)
TEXT_COLOR = (220, 220, 230)
SECONDARY_TEXT = (150, 160, 170)

# Fonts
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 24)
font_tiny = pygame.font.Font(None, 18)

print("Use left stick to control. ESC to quit.")

last_sent = ""
clock = pygame.time.Clock()

# Maximum motor power
MAX_POWER = 32

# Control stick settings
stick_center_x_left = WIDTH // 4
stick_center_x_right = 3 * WIDTH // 4
stick_center_y = HEIGHT // 2
stick_outer_radius = 80
stick_inner_radius = 15

# Mock data (replace with real data from robot)
robot_voltage = 0
enc1 = 0
enc2 = 0
speedL = 0
speedR = 0


def draw_rounded_rect(surface, color, rect, corner_radius):
    """Draw a rounded rectangle"""
    x, y, width, height = rect

    # Draw the main rectangle
    pygame.draw.rect(
        surface, color, (x + corner_radius, y, width - 2 * corner_radius, height)
    )
    pygame.draw.rect(
        surface, color, (x, y + corner_radius, width, height - 2 * corner_radius)
    )

    # Draw the corners
    pygame.draw.circle(
        surface, color, (x + corner_radius, y + corner_radius), corner_radius
    )
    pygame.draw.circle(
        surface, color, (x + width - corner_radius, y + corner_radius), corner_radius
    )
    pygame.draw.circle(
        surface, color, (x + corner_radius, y + height - corner_radius), corner_radius
    )
    pygame.draw.circle(
        surface,
        color,
        (x + width - corner_radius, y + height - corner_radius),
        corner_radius,
    )


def draw_status_panel():
    """Draw the top status panel"""
    panel_rect = (20, 20, WIDTH - 40, 80)
    draw_rounded_rect(screen, PANEL_BG, panel_rect, 10)

    # Connection status
    status_color = SUCCESS_COLOR if connection_status else DANGER_COLOR
    status_text = "CONNECTED" if connection_status else "DISCONNECTED"

    # Connection indicator circle
    pygame.draw.circle(screen, status_color, (60, 60), 12)

    # Status text
    status_surface = font_medium.render(status_text, True, status_color)
    screen.blit(status_surface, (85, 45))

    # Voltage display
    voltage_color = (
        SUCCESS_COLOR
        if robot_voltage > 11.0
        else WARNING_COLOR if robot_voltage > 10.0 else DANGER_COLOR
    )
    voltage_text = f"VOLTAGE: {robot_voltage:.1f}V"
    voltage_surface = font_medium.render(voltage_text, True, voltage_color)
    screen.blit(voltage_surface, (300, 45))

    # Voltage bar
    bar_width = 200
    bar_height = 20
    bar_x = 300
    bar_y = 70

    # Background bar
    pygame.draw.rect(
        screen, (60, 60, 70), (bar_x, bar_y, bar_width, bar_height), border_radius=10
    )

    # Voltage level (assuming 9V-13V range)
    voltage_percentage = max(0, min(1, (robot_voltage - 9) / 4))
    fill_width = int(bar_width * voltage_percentage)
    if fill_width > 0:
        pygame.draw.rect(
            screen,
            voltage_color,
            (bar_x, bar_y, fill_width, bar_height),
            border_radius=10,
        )

    # Title
    title_surface = font_large.render("VEHICLE CONTROL INTERFACE", True, TEXT_COLOR)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, 35))
    screen.blit(title_surface, title_rect)


def draw_control_stick(center_x, center_y, stick_y_offset, power_value, label, color):
    """Draw a control stick with power indication"""
    # Outer circle (track)
    pygame.draw.circle(
        screen, SECONDARY_TEXT, (center_x, center_y), stick_outer_radius, 3
    )

    # Power level arc
    if abs(power_value) > 0:
        arc_color = color
        arc_thickness = 8
        power_ratio = abs(power_value) / MAX_POWER
        arc_angle = power_ratio * math.pi

        # Draw power arc
        start_angle = -math.pi / 2 - arc_angle / 2
        end_angle = -math.pi / 2 + arc_angle / 2

        # Create points for the arc
        points = []
        for i in range(int(arc_angle * 20) + 1):
            angle = start_angle + (end_angle - start_angle) * i / (arc_angle * 20)
            x = center_x + (stick_outer_radius - 5) * math.cos(angle)
            y = center_y + (stick_outer_radius - 5) * math.sin(angle)
            points.append((x, y))

        if len(points) > 1:
            pygame.draw.lines(screen, arc_color, False, points, arc_thickness)

    # Inner stick position
    stick_y = center_y + stick_y_offset * (stick_outer_radius - stick_inner_radius - 5)
    pygame.draw.circle(screen, color, (center_x, int(stick_y)), stick_inner_radius)
    pygame.draw.circle(
        screen, TEXT_COLOR, (center_x, int(stick_y)), stick_inner_radius, 2
    )

    # Label and power value
    label_surface = font_medium.render(label, True, TEXT_COLOR)
    label_rect = label_surface.get_rect(
        center=(center_x, center_y + stick_outer_radius + 30)
    )
    screen.blit(label_surface, label_rect)

    power_text = f"{power_value:+.0f}"
    power_surface = font_small.render(power_text, True, color)
    power_rect = power_surface.get_rect(
        center=(center_x, center_y + stick_outer_radius + 55)
    )
    screen.blit(power_surface, power_rect)


def draw_encoder_display():
    """Draw encoder readings"""
    panel_rect = (20, HEIGHT - 120, WIDTH - 40, 80)
    draw_rounded_rect(screen, PANEL_BG, panel_rect, 10)

    # Encoder labels
    enc_title = font_medium.render("ENCODER READINGS", True, TEXT_COLOR)
    screen.blit(enc_title, (40, HEIGHT - 110))

    # Left encoder
    left_enc_text = f"LEFT: {enc1}"
    left_enc_surface = font_small.render(left_enc_text, True, ACCENT_COLOR)
    screen.blit(left_enc_surface, (40, HEIGHT - 80))

    # Right encoder
    right_enc_text = f"RIGHT: {enc2}"
    right_enc_surface = font_small.render(right_enc_text, True, ACCENT_COLOR)
    screen.blit(right_enc_surface, (200, HEIGHT - 80))

    # Speed indicators (mock calculation based on encoder changes)
    speed_left = abs(enc1 % 100) / 10  # Mock speed calculation
    speed_right = abs(enc2 % 100) / 10

    speed_left_text = f"SPEED: {speedL:.1f}"
    speed_right_text = f"SPEED: {speedR:.1f}"

    speed_left_surface = font_tiny.render(speed_left_text, True, SECONDARY_TEXT)
    speed_right_surface = font_tiny.render(speed_right_text, True, SECONDARY_TEXT)

    screen.blit(speed_left_surface, (40, HEIGHT - 60))
    screen.blit(speed_right_surface, (200, HEIGHT - 60))


def send_command(speed1, speed2):
    global last_sent
    if not ser:
        return

    s1 = int(speed1)
    s2 = int(speed2)
    command = f"{s1},{s2}\n"
    if command != last_sent:
        try:
            ser.write(command.encode())
            print(f"Sent: {command.strip()}")
            last_sent = command
        except:
            print("Failed to send command")


def draw_instructions():
    """Draw control instructions"""
    instructions = [
        "LEFT STICK: Left Motor Control",
        "RIGHT STICK: Right Motor Control",
        "ESC: Exit Application",
    ]

    y_start = HEIGHT - 250
    for i, instruction in enumerate(instructions):
        text_surface = font_tiny.render(instruction, True, SECONDARY_TEXT)
        screen.blit(text_surface, (WIDTH - 250, y_start + i * 20))


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    # Get joystick input
    axis_y = 0
    axis_y2 = 0

    if joystick:
        pygame.event.pump()
        axis_y = joystick.get_axis(1)  # Left stick Y
        axis_y2 = joystick.get_axis(3)  # Right stick Y
        # for i in range(joystick.get_numbuttons()):
        #     if joystick.get_button(i):
        #         print(f"Button {i} is pressed")
        if ser and joystick.get_button(9):
            print("Resetting robot...")
            # Toggle RTS and DTR to reset
            ser.dtr = False
            ser.rts = True
            time.sleep(0.1)
            ser.dtr = True
            ser.rts = False
            time.sleep(0.1)
            try:
                ser = serial.Serial("COM3", 115200)  # Adjust COM port
                time.sleep(2)
                connection_status = True
            except:
                ser = None
                connection_status = False

    # Calculate motor powers
    left_power = axis_y * MAX_POWER
    right_power = axis_y2 * MAX_POWER

    # Apply deadzone
    if abs(left_power) < 2:
        left_power = 0
    if abs(right_power) < 2:
        right_power = 0

    # Clamp values
    left_power = max(-MAX_POWER, min(MAX_POWER, left_power))
    right_power = max(-MAX_POWER, min(MAX_POWER, right_power))

    send_command(left_power, right_power)

    # Read serial data
    if ser and ser.in_waiting:
        try:
            line = ser.readline().decode().strip()
            if line.startswith("ENCODER"):
                _, enc1a, enc2a = line.split(",")
                enc1 = int(enc1a)
                enc2 = int(enc2a)
            if line.startswith("VOLTAGE"):
                # Assuming voltage data format: "VOLTAGE,12.4"
                _, voltage_str = line.split(",")
                robot_voltage = float(voltage_str)
            if line.startswith("SPEED"):
                _, enc1a, enc2a = line.split(",")
                enc1 = int(enc1a)
                enc2 = int(enc2a)
            print(f"Received: {line}")
        except Exception as e:
            print(f"Failed to read: {e}")

    # Draw everything
    screen.fill(DARK_BG)

    # Draw UI components
    draw_status_panel()
    draw_control_stick(
        stick_center_x_left,
        stick_center_y,
        axis_y,
        left_power,
        "LEFT MOTOR",
        SUCCESS_COLOR,
    )
    draw_control_stick(
        stick_center_x_right,
        stick_center_y,
        axis_y2,
        right_power,
        "RIGHT MOTOR",
        ACCENT_COLOR,
    )
    draw_encoder_display()
    draw_instructions()

    # Connection warning
    if not connection_status:
        warning_text = "ROBOT NOT CONNECTED - CHECK CONNECTION"
        warning_surface = font_medium.render(warning_text, True, DANGER_COLOR)
        warning_rect = warning_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

        # Warning background
        warning_bg_rect = (
            warning_rect.x - 20,
            warning_rect.y - 10,
            warning_rect.width + 40,
            warning_rect.height + 20,
        )
        draw_rounded_rect(screen, (80, 20, 20), warning_bg_rect, 5)

        screen.blit(warning_surface, warning_rect)

        try:
            ser = serial.Serial("COM3", 115200)  # Adjust COM port
            time.sleep(2)
            connection_status = True
        except:
            ser = None
            connection_status = False

    pygame.display.flip()
    clock.tick(60)  # Increased to 60 FPS for smoother animation

# Cleanup
if ser:
    ser.close()
pygame.quit()
sys.exit()
