# Project Guidelines

## Code Style
- Use uv for all dependency and execution tasks.
- Keep source code identifiers in English.
- Use type hints on function and method signatures.
- Follow ruff and mypy feedback before finalizing edits.
- Use module-level logger initialization with logging.getLogger(__name__).

## Architecture
- Treat src/core/state.py AppState as the single state hub.
- Keep module boundaries clear:
  - src/core: shared state, config, hotkeys, websocket transport.
  - src/services: player control logic only.
  - src/ui: HUD, settings window, and system tray behavior.
- Do not couple service logic directly to UI widgets. Services should trigger state notifications and let UI observers react.
- Keep thread/async boundaries safe:
  - Hotkey and tray callbacks are synchronous.
  - Interact with asyncio state through loop.call_soon_threadsafe(...).

## Build and Test
- Setup environment: uv sync
- Run app: uv run main.py
- Open settings UI only: uv run -m src.ui.settings
- Lint: uv run ruff check src/ main.py
- Lint with fixes: uv run ruff check --fix src/ main.py
- Type check: uv run mypy src/ main.py
- Refresh lockfile after dependency/structure updates: uv lock

## Conventions
- WebSocket protocol is text-based and expects KEY:VALUE messages.
- Default local WebSocket endpoint is ws://127.0.0.1:8975.
- Volume mute behavior separates mute state from explicit volume=0 state.
- Config is reloaded from settings.json at runtime in volume-related flows.

## Platform and Pitfalls
- This project is Windows-first due to keyboard hooks, pystray, and Win32 HUD behavior.
- Keep tray startup on a daemon thread; pystray.Icon.run() is blocking.
- Be careful with HUD Win32 calls and DPI behavior when changing UI/window logic.

## References
- See README.md for quick project overview and setup.
- See .cursorrules for additional workspace collaboration preferences.
