# Gamepad Vibration

A small application for controlling a gamepad's vibration motors.

## Run

On Windows, run:

```bat
run.bat
```

On Linux or macOS, run:

```bash
./run.sh
```

On the first run, the script creates a local `.venv` virtual environment and installs pygame in it. Python 3 and internet access are required to install the dependency the first time. Alternatively, you can install pygame manually in a virtual environment and run `gamepad_vibration.py` with that environment's Python interpreter.

Connect a gamepad before starting the application or while it is running. The application uses SDL's standard controller layout: **X** toggles vibration, the left stick controls the left (low-frequency) motor, and the right stick controls the right (high-frequency) motor. A motor turns off when its corresponding stick is released.

Controller support and vibration feedback (rumble) must be available in SDL and the operating system. On Linux, the user may also need permission to access the input device.
