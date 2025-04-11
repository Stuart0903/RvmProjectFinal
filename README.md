# 🤖 RVM Project - Reverse Vending Machine System

## 📋 Overview
The RVM (Reverse Vending Machine) Project is an advanced Python-based application that interfaces with Arduino hardware and camera systems to create an automated recycling solution. This system uses computer vision and embedded systems to identify, sort, and process recyclable items.

---

## ⚙️ Installation and Setup

### Prerequisites
- ✅ VS Code IDE
- ✅ Python 3.8 or higher
- ✅ Git
- ✅ Arduino board
- ✅ External USB camera (or integrated camera)
- ✅ Serial USB cable

### Step-by-Step Installation

#### 1️⃣ Install PlatformIO Extension in VS Code
- Open VS Code
- Go to Extensions marketplace (or press `Ctrl+Shift+X`)
- Search for "PlatformIO"
- Click Install

#### 2️⃣ Clone the Repository
```bash
git clone https://github.com/Stuart0903/RvmProjectFinal.git
```
> 💡 Keep the cloned repository in a dedicated folder

#### 3️⃣ Open the Project with PlatformIO
- In VS Code, click on the PlatformIO icon in the sidebar
- Select "Open Project"
- Navigate to and select the cloned folder "RvmProjectFinal"

#### 4️⃣ Install Python Dependencies
```bash
cd RvmProjectFinal
pip install -r requirements.txt
```

#### 5️⃣ Upload Arduino Code
- Connect your Arduino board to your computer
- From your project directory, locate the `main.cpp` file
- Try uploading through PlatformIO:
  - Click on the PlatformIO icon
  - Select "Upload" under Project Tasks

**If upload fails:**
- Install Arduino IDE from [arduino.cc](https://www.arduino.cc/en/software)
- Open Arduino IDE
- Create a new sketch
- Copy all code from `main.cpp`
- Paste into the Arduino IDE sketch
- Select your board type and port from Tools menu
- Click "Upload" button
- Once uploaded successfully, return to the RVM project

#### 6️⃣ Run the Application
```bash
cd src
python main.py
```

---

## 🔌 Hardware Setup

### Arduino Connection
- Connect your Arduino board to your computer using a USB serial cable
- The system will automatically detect available serial ports

### Camera Setup
- Connect an external USB camera to your computer
- If using an external camera, ensure it's properly connected before starting the application
- If no external camera is detected or you wish to use an integrated camera, modify the camera index in `settings.py`:
  ```python
  # Change camera_index from 0 to 1 for integrated camera
  camera_index = 1
  ```

### Circuit Diagram
Below is the circuit diagram for connecting components to your Arduino:
![image](https://github.com/user-attachments/assets/313247a3-821e-4e4d-a2de-9fc3c352cbca)








**Key components in the circuit:**
- Arduino board (e.g., Arduino Uno or Mega)
- Sensors for detecting items
- Actuators for sorting mechanisms
- Power supply connections
- USB connection to computer

> ⚠️ Please refer to the diagram above for proper wiring and connections.

---

## ⚙️ Configuration
Additional configuration options can be found in `config/settings.py`. You may need to adjust these settings based on your specific hardware setup.

---

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Arduino Not Detected** | Ensure the Arduino is properly connected and that you have the correct drivers installed. Check the COM port in Device Manager. |
| **Camera Not Working** | Verify the camera is connected and try changing the camera index in settings.py. Test the camera with another application. |
| **Serial Communication Errors** | Check that the correct COM port is being used and that no other applications are using the serial port. |
| **Upload Failures** | Make sure you have the correct board selected in Arduino IDE or PlatformIO. Check USB connection. |

### Logs
The application generates logs in the `logs` directory which can be useful for debugging issues.

---

## 📊 Project Structure

```
RvmProjectFinal/
├── src/                   # Source code
│   ├── main.py            # Main application entry point
│   ├── config/            # Configuration files
│   │   └── settings.py    # Settings and parameters              # Arduino code
│   └── main.cpp           # Main Arduino code
├── requirements.txt    
├──lib   # Python dependencies
    └── README.md              # This file
```


## 📞 Contact
gmail: stharpan.officical777@gmail.com

