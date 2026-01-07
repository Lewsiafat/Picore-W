# Plan: WiFiManager Decoupling & Memory Optimization

## Phase 1: Preparation & Constants [checkpoint: 9d89bf5]
- [x] Task: Create feature branch `refactor/wifi-manager-decoupling` (Branch Created)
- [x] Task: Create `src/constants.py` and move WiFi state machine constants (0dadcc5)
- [x] Task: Create `src/config.py` and move default WiFi configuration constants (3e6546a)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Constants' (Protocol in workflow.md)

## Phase 2: Template Decoupling [checkpoint: 6258338]
- [x] Task: Create `src/templates/` directory and migrate HTML to `.html` files (12803ed)
- [x] Task: Implement file-based template reading logic in `WiFiManager` (bd7b7e5)
- [x] Task: Conductor - User Manual Verification 'Phase 2: Templates' (Protocol in workflow.md)

## Phase 3: Integration & Cleanup [checkpoint: da06757]
- [x] Task: Update `wifi_manager.py` and other modules to import from new constants/config (58e38c6)
- [x] Task: Final cleanup of redundant strings and comments in `wifi_manager.py` (d742619)
- [x] Task: Conductor - User Manual Verification 'Phase 3: Integration' (Protocol in workflow.md)
