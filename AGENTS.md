# Bridge Game Project

## Project Goal

This project is a four-player bridge-inspired card game written primarily in Python.

The game will eventually support:

- Four players
- Four rounds
- Special ability cards
- Round results affecting ability-card distribution
- Multiplayer networking
- Room codes
- Browser-based gameplay

## Architecture Principle

Keep game logic independent from UI and networking.

Core game logic must not depend on:

- Pygame
- FastAPI
- WebSocket
- Browser code

## Planned Development Order

1. Card
2. Deck
3. Hand
4. Player
5. Team
6. Trick
7. Rules
8. Round
9. Ability cards
10. Game state
11. UI
12. Networking
13. Web version

Do not implement later phases prematurely.

## OOP and Software Design

This project should be designed primarily using object-oriented programming.

Prefer appropriate use of:

- Encapsulation
- Abstraction
- Inheritance when there is a genuine "is-a" relationship
- Polymorphism
- Composition
- Abstract Base Classes (ABC)
- Properties when appropriate
- Enums for fixed domain concepts
- Type hints
- Dataclasses when they improve clarity
- Dependency injection when useful
- SOLID principles where appropriate
- Design patterns when they solve a real architectural problem

Important principles:

- Prefer composition over unnecessary inheritance.
- Do not introduce inheritance only to demonstrate OOP.
- Avoid overly complex abstractions.
- Each class should have a clear responsibility.
- Keep coupling between modules low.
- Keep game logic independent from UI and networking.
- Prefer interfaces/abstractions at boundaries where future implementations may change.

When implementing a feature, consider whether an OOP or advanced OOP technique would improve the design.

If introducing an advanced OOP technique or design pattern, briefly explain:
1. What technique is being used.
2. Why it is appropriate here.
3. What problem it solves.

## Development Workflow

For each feature:

1. Inspect the existing repository.
2. Implement only the requested feature.
3. Add or update tests.
4. Run pytest.
5. Avoid modifying unrelated files.
6. Explain major architectural changes before making them.

## Git

Keep changes small and focused.

Do not commit generated files, virtual environments, secrets, or cache files.