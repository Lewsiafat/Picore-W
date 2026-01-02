# Product Guide - Picore-W

## Initial Concept
Overview: This project is a foundational infrastructure repository for the Raspberry Pi Pico 2 W (RP2350) using MicroPython. Its primary goal is to provide a robust, reusable base layer for future IoT applications, specifically focusing on network reliability.

Core Objective: To implement a resilient WiFi State Machine that manages the network connection lifecycle. It must handle connection, disconnection, re-connection attempts, and error states automatically, ensuring that the main application always has a clear understanding of the network status.

## Target Audience
- Developers building IoT applications on Raspberry Pi Pico 2 W.
- Systems requiring high network availability and automated recovery.

## Core Features
- **Resilient WiFi State Machine**: Manages the full lifecycle of WiFi connections.
- **Automated Reconnection**: Handles network drops and attempts recovery without blocking the main application.
- **Status Reporting**: Provides granular feedback on connection states (Connecting, Connected, Auth Failed, No AP found, etc.).
- **Smart Provisioning**: Automatically enters Access Point (AP) mode with a web interface for credential input when no valid configuration is found.

## Design Philosophy
- **Purity & Minimalism**: Avoid unnecessary abstractions; focus on the core networking problem.
- **Extensibility**: Designed as a base layer that can be easily integrated into larger applications.
- **Robustness**: Prioritize error handling and state consistency.
