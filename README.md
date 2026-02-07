# Cave Explorer (Pygame)

A robust procedural dungeon crawler built with Python and Pygame. Explore infinite caves, fight goblins, and see how deep you can go!

## Features

*   **Procedural Generation**: Uses Cellular Automata to generate unique, organic cave layouts every time.
*   **Fog of War**: Explore the unknown. Areas you haven't seen are hidden, and areas you've visited are remembered.
*   **Combat System**: Turn-based combat mechanics inspired by D&D 5e (AC, Attack Rolls, HP).
*   **Dungeon Progression**: Find the yellow stairs to descend deeper. The deeper you go, the stronger the enemies become.
    *   **Persistent Levels**: You can climb back up to previous floors, and they remain exactly as you left them.
*   **UI System**: 
    *   **Minimap**: A toggleable radar to see the full cave layout.
    *   **Message Log**: Scrolling combat log to track battle events.
    *   **Health & Status**: Visual health bar and level tracking.

## Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/mbolding/cave_gen.git
    cd cave_gen
    ```

2.  **Install Dependencies**:
    This project requires `pygame` and `numpy`.
    ```bash
    pip install -r requirements.txt
    # OR
    uv sync
    ```

3.  **Run the Game**:
    ```bash
    python main.py
    # OR
    uv run main.py
    ```

## Controls

| Key | Action |
| :--- | :--- |
| **Arrow Keys** | Move / Attack (bump into enemies) |
| **M** | Toggle Minimap |
| **H** | Toggle Help / Controls Popup |
| **Space** | Start Game / Restart (on Game Over) |

## Development Roadmap

See [ROADMAP.md](./ROADMAP.md) for the current development status and future plans.

## License

MIT
