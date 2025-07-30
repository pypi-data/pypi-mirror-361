# Duck Quest - Board Game

![Logo](./duckquest/assets/images/logo.png)

[![Version](https://img.shields.io/github/v/release/LeoLeman555/Board_Game_DuckQuest)](https://github.com/LeoLeman555/Board_Game_DuckQuest/releases)
[![License](https://img.shields.io/github/license/LeoLeman555/Board_Game_DuckQuest)](LICENSE)
[![Status](https://img.shields.io/badge/status-prototype--stable-brightgreen)]()
![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)
[![CI Tests](https://github.com/LeoLeman555/Board_Game_DuckQuest/actions/workflows/tests.yml/badge.svg)](https://github.com/LeoLeman555/Board_Game_DuckQuest/actions/workflows/tests.yml)

DuckQuest is an educational game created within a school project. It is aimed at young children and allows them to learn to think like an algorithm in order to understand how these work. We achieve this by asking them to find the shortest route through a graph, just as a Dijkstra algorithm would.

## Table of Contents

- [Overview](#overview)
- [Dependencies](#dependencies)
- [Hardware Requirements](#hardware-requirements)
- [Execution Modes](#execution-modes)
- [Installation](#installation)
- [Run](#run)
- [Project Structure](#project-structure)
- [Logging](#logging)
- [Tests](#tests)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

### Game Concept
In DuckQuest, the graph is represented as a network of routes around a pond. Children guide a duck along the shortest path using physical buttons for graph nodes and LED strips for graph edges. A Raspberry Pi powers and controls the setup. 

### Example Visualization
The following graph represents the playground used in DuckQuest.

Each node is a possible location for the duck, and each edge represents a path with a specific weight, visualized by its color.

The goal is to help the duck travel from A1 (start) to Q2 (goal) by choosing the shortest path — just like Dijkstra's algorithm would do.

![Sample graph](./duckquest/assets/images/sample_graph.png)

Edge color legend:
| Weight |    Color   | Meaning                    |
|--------|------------|----------------------------|
|    1   |    Green   | Fastest, most optimal path |
|    2   | Bright-Green | Still efficient            |
|    3   |   Yellow   |	Moderate path              |
|    4   |   Orange   |	Slower                     |
|    5   |     Red    |	Longest, to be avoided     |

## Dependencies

The project uses the following main libraries:

- `matplotlib` – for visualizing the graph
- `networkx` – for graph logic and shortest path calculations
- `pygame` – for background music
- `RPi.GPIO` – for button input (Raspberry Pi only)
- `rpi_ws281x` – for controlling addressable LEDs (Raspberry Pi only)
- `tkinter` – for GUI (included with Python)

## Hardware Requirements
To build the DuckQuest board game, you need the following components:

- Complete Raspberry Pi kit
- Push buttons for nodes
- Addressable RGB strips for edges (like WS2812)
- 5V Power Supply for powering the LED strip
- Jumper wires

## Execution Modes

DuckQuest can run in two modes:

- **Hardware mode (Raspberry Pi)**  
  Real GPIO pins control the LED strips and buttons.

- **Mock mode (Windows/macOS/Linux)**  
  The hardware is replaced with mock interfaces and visual output.

The system auto-detects the environment at runtime.

## Installation

### Prerequisites

If you run in Hardware Mode ensure you have the following software installed on your raspberry:

- [Python 3.11+](https://www.python.org/)
- [Git](https://git-scm.com/)
- An active graphical interface (like X11) – **required for running the game UI**

### Steps for Installation

1. Clone the repository on your Raspberry Pi:
   ```bash
   git clone https://github.com/LeoLeman555/Board_Game_DuckQuest.git
   ```

2. Navigate to the project directory:
   ```bash
   cd ./Board_Game_DuckQuest/
   ```

3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   - **Linux**:
   ```bash
   source venv/bin/activate
   ```
   - **Windows**:
   ```powershell
   venv\Scripts\activate
   ```

5. Installing dependencies with a Python script:
   ```bash
   python install.py
   ```

> **Why use `install.py` instead of `requirements.txt`?**  
> The `RPi.GPIO` module is specifically designed for Raspberry Pi and does not work on Windows or non-Raspberry Pi Linux systems.  
> If included directly in `requirements.txt`, installation would fail on unsupported platforms. 
> Additionally, the `rpi_ws281x` module, which is used to control the WS281x LED strips, is also Raspberry Pi-specific. Just like `RPi.GPIO`, it doesn't function on other platforms.
>  
> The `install.py` script ensures that both `RPi.GPIO` and `rpi_ws281x` are installed only if the script detects a Raspberry Pi. This makes the installation process more flexible and prevents errors on unsupported platforms.

## Run
To launch the game, use the following command:
```bash
sudo -E $(which python) -m duckquest.main
```

> `sudo` is required to access GPIO and PWM devices on Raspberry Pi.


## Project Structure

```plaintext
duckquest/
├── graph/         # Graph logic, UI components, and Matplotlib rendering
├── hardware/      # GPIO control for buttons and LED strips (with mocks)
├── audio/         # Background music and sound effects manager
├── utils/         # Helper functions and centralized logging system
├── main.py        # Main entry point to launch the game

docs/              # Technical documentation
logs/              # Generated logs (console + file logging system)
scripts/           # Manual testing tools for hardware (GPIO, LEDs)
tests/             # Unit and manual tests using Pytest
```

## Logging

All modules use structured logging, with outputs going to the console and into a file. See [`docs/logging.md`](./docs/logging.md) for details.

## Tests

All test instructions (unit, UI, and hardware) are documented in [`docs/tests.md`](./docs/tests.md).

## Contributing

Want to help improve DuckQuest? Contributions are welcome!

- Fork the repository
- Create a feature branch (`feat/your-feature`)
- Make sure tests pass (`pytest`)
- Open a Pull Request

If you like the project, consider giving it a ⭐️ on GitHub — it really helps!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or feedback, feel free to contact me:

- GitHub: [LeoLeman555](https://github.com/LeoLeman555)
- Email: leo.leman555@gmail.com
