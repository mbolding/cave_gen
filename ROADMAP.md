# Roguelike Dungeon Explorer Roadmap

## 1. Core Movement & Entities 
- [ ] **Player Entity**: Create a generic `Entity` class and a `Player` subclass.
- [x] **Movement Logic**: Allow the player to move with arrow keys/WASD, colliding with walls (checking the `grid`).
- [x] **Camera/Scrolling**: If the map is larger than the screen (it is), implemented a camera system to follow the player.

## 2. Exploration Mechanics
- [x] **Field of View (FOV)**: Implement "Fog of War". The player should only see tiles within a certain radius and line-of-sight. Unseen areas should be shrouded.
- [x] **Explored Memory**: Remember visited areas (drawn in grey) vs currently visible areas (drawn in full color).

## 3. Turn-Based System & NPCs
- [ ] **NPC/Enemy Entities**: Spawn basic enemies (e.g., Goblins) in random open floor spots.
- [ ] **Turn-Based Loop**: Game waits for player input. Player Move -> Enemies Move.
- [ ] **Basic Enemy AI**: Enemies move randomly or towards the player if visible.

## 4. Combat System (D&D Inspired)
- [ ] **Stats**: Add HP, Armor Class (AC), Strength to entities.
- [ ] **Melee Attacks**: Bumping into an enemy triggers an attack instead of movement.
- [ ] **Combat Resolution**: Roll dice (d20) vs AC to hit, roll damage.
- [ ] **Death**: Enemies vanish when HP <= 0. Game Over screen if Player dies.

## 5. User Interface (UI)
- [ ] **Message Log**: A scrolling text box at the bottom showing combat info ("You hit the Goblin for 4 damage!").
- [ ] **Status Bar**: Health bar, current level, stats display.

## 6. Progression
- [ ] **Stairs & Depth**: Add a staircase tile. Moving to it generates a new cave map (Deeper Level).
- [ ] **XP & Leveling**: Killing enemies gives XP. Level up increases stats.

## 7. Items & Inventory
- [ ] **Items**: Potions (Heal), Scrolls.
- [ ] **Inventory System**: UI to list carried items and Use/Drop them.
- [ ] **Equipment**: Weapons and Armor that modify stats.

## 8. Magic & Advanced Features
- [ ] **Spells**: Fireball, Magic Missile (using the A* targeting potentially).
- [ ] **Save/Load System**: Persistence using JSON or Pickle.
