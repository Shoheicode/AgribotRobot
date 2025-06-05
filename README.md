# 🚜 AgriCruiser Robot

**AgriCruiser** is a custom-built ground robot designed for precision agriculture tasks. It is controlled via joystick input through a real-time UI on a PC and communicates wirelessly with onboard ESP32 microcontrollers that manage dual-motor movement, sensor feedback, and voltage monitoring.

## 📁 Project Structure

```
AgriCruiser/
├── Esp32Code/
│   ├── Reciever.ino         # Runs on ESP32-B (motor + telemetry node)
│   └── Sender.ino           # Runs on ESP32-A (receives PC input, sends to ESP32-B)
├── JoystickCode/
│   ├── JoystickAndUI.py     # Main PC GUI and joystick controller interface
│   ├── joystickCode.py      # (Legacy / auxiliary) direct joystick test script
│   └── keyboardCode.py      # (Optional) keyboard-based motor control
├── requirements.txt         # Python dependencies
├── setup_env.bat            # Windows environment setup
├── setup_env.sh             # Unix/Linux environment setup
├── README.md                # You are here
└── .gitignore               # Git ignored files
```

## 🧠 System Overview

### 🖥 PC Controller
- **Language:** Python + Pygame
- **Script:** `JoystickAndUI.py`
- **Purpose:** Reads joystick input, displays robot UI (connection, voltage, encoder), and sends motor commands to ESP32-A via serial.

### 📡 ESP32-A: Sender Node
- **Script:** `Sender.ino`
- **Role:** Reads motor speeds from PC serial input and transmits them via ESP-NOW to ESP32-B.
- **Features:**
  - Retry loop for ESP-NOW peer connection
  - Receives encoder and voltage telemetry and relays back to PC

### 🤖 ESP32-B: Receiver Node
- **Script:** `Reciever.ino`
- **Role:** Receives commands from ESP32-A, controls RoboClaw motors, and sends encoder + battery voltage telemetry back.
- **Hardware:** 
  - RoboClaw motor controller
  - Two motors with encoders
  - Battery voltage monitoring

## 🎮 Controls & UI

- **Left Stick (Y-axis):** Left motor speed
- **Right Stick (Y-axis):** Right motor speed
- **Button 9 (e.g., Logitech 'Start'):** Attempt ESP32 hardware reset
- **ESC key or window close:** Exit application

UI displays:
- Connection status
- Battery voltage (with colored indicator bar)
- Motor power levels
- Encoder values and mock speed estimates

## 🚀 Getting Started

### Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```

### Run PC Controller

```bash
cd JoystickCode
python JoystickAndUI.py
```

Ensure the joystick is connected before launch.

### Upload ESP32 Code

1. Use Arduino IDE or PlatformIO.
2. Upload `Sender.ino` to ESP32-A (connected to PC).
3. Upload `Reciever.ino` to ESP32-B (connected to RoboClaw + motors).
4. Adjust MAC addresses if necessary (see `receiverAddress` in both `.ino` files).

## 🔧 Troubleshooting

- **Joystick not detected?** Ensure it's plugged in before running the Python script.
- **ESP32 not connecting?** Double-check MAC address matching and power cycle both boards.
- **No motor movement?** Check RoboClaw wiring, address (`0x80`), and power supply.
- **Serial error in Python?** Update COM port in `JoystickAndUI.py`.

## 📋 Notes

- ESP-NOW uses 2.4GHz Wi-Fi and may be affected by interference.
- The RoboClaw must be powered appropriately (e.g., 12–24V) and grounded with ESP32.

## 📸 Screenshot

![UI Screenshot](./65f0651d-97ed-44e9-ae15-806545b75128.png)

## 📜 License

MIT License — Feel free to use and adapt.

---

## 🎮 Joystick-Controlled Motor Interface with ESP32

This project uses a USB joystick to control two motors via an ESP32 board over serial communication. It also reads and displays encoder data received from the ESP32.

### 📦 Requirements

- Python 3.8 or higher
- A connected ESP32 board on a serial port (e.g., COM3)
- A compatible joystick (Xbox, PS4, Logitech, etc.)

### 🔧 Setup Instructions

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/esp32-joystick-control.git
cd esp32-joystick-control
```

#### 2. Create and Activate a Virtual Environment

On Linux/macOS:
```bash
bash setup_env.sh
source venv/bin/activate
```

On Windows:
```bash
.\setup_env.bat
venv\Scripts\activate
```

#### 3. Run the Script

Make sure your ESP32 is connected and configured to listen on the correct COM port.

```bash
python JoystickCode\joystickCode.py
```

#### 🧼 Cleanup

To deactivate the virtual environment when you're done:

```bash
deactivate
```

#### 📝 Notes

- If no joystick is detected, the program will exit automatically.
- Adjust the COM port in the Python script (`serial.Serial("COM3", 115200)`) as needed for your system.
- Encoder data should be sent from the ESP32 in the format:

```
ENCODER,<value1>,<value2>
```
## Version:
Update Roboclaw with version BasicmicroMotionStudio_1.0.0.75

Update ESP 32 with version 2.0.9

## Circuit Diagram for AgriCrusier:
![image](https://github.com/user-attachments/assets/66a488dc-2805-404c-b62c-07e03828eeb1)
