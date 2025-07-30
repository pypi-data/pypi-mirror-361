import sys
import subprocess


def is_raspberry_pi():
    """Check if the system is a Raspberry Pi."""
    try:
        with open("/proc/cpuinfo", "r") as f:
            return "Raspberry Pi" in f.read()
    except FileNotFoundError:
        return False


# Upgrade pip first
subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)

# List of dependencies
common_requirements = [
    "black==23.10.1",
    "matplotlib~=3.10",
    "networkx~=3.4",
    "pygame~=2.6",
    "pytest~=8.0",
]

# Add Raspberry Pi-specific dependencies if necessary
if is_raspberry_pi():
    common_requirements.extend(
        [
            "RPi.GPIO==0.7.1",  # Managing the Raspberry Pi's GPIOs
            "rpi_ws281x==5.0.0",  # WS281x LED strip control
        ]
    )

# Install dependencies
try:
    subprocess.run(
        [sys.executable, "-m", "pip", "install"] + common_requirements, check=True
    )
    print("✅ Installation completed successfully!")
except subprocess.CalledProcessError:
    print("❌ Installation failed. Check the error messages above.")
    sys.exit(1)
