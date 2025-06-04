# 🎮 Joystick-Controlled Motor Interface with ESP32

This project uses a USB joystick to control two motors via an ESP32 board over serial communication. It also reads and displays encoder data received from the ESP32.

## 📦 Requirements

- Python 3.8 or higher
- A connected ESP32 board on a serial port (e.g., COM3)
- A compatible joystick (Xbox, PS4, Logitech, etc.)

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/esp32-joystick-control.git
cd esp32-joystick-control
```

### 2. Create and Activate a Virtual Environment
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

### 3. Run the Script
Make sure your ESP32 is connected and configured to listen on the correct COM port.
```bash
python JoystickCode\joystickCode.py
```

### 🧼 Cleanup
To deactivate the virtual environment when you're done:
```bash
deactivate
```
### 📝 Notes

- If no joystick is detected, the program will exit automatically.
- Adjust the COM port in the Python script (serial.Serial("COM3", 115200)) as needed for your system.
- Encoder data should be sent from the ESP32 in the format:

        ENCODER,<value1>,<value2>
