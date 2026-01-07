# Plan: WiFiManager Decoupling & Memory Optimization

## Phase 1: Preparation & Constants
- [x] Task: Create feature branch `refactor/wifi-manager-decoupling` (Branch Created)
- [x] Task: Create `src/constants.py` and move WiFi state machine constants (0dadcc5)
- [x] Task: Create `src/config.py` and move default WiFi configuration constants (3e6546a)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Constants' (Protocol in workflow.md)

## Phase 2: Template Decoupling
- [ ] Task: Create `src/templates/` directory and migrate HTML to `.html` files
- [ ] Task: Implement file-based template reading logic in `WiFiManager`
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Templates' (Protocol in workflow.md)

## Phase 3: Integration & Cleanup
- [ ] Task: Update `wifi_manager.py` and other modules to import from new constants/config
- [ ] Task: Final cleanup of redundant strings and comments in `wifi_manager.py`
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration' (Protocol in workflow.md)
