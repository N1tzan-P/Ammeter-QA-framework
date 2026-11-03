# Design Decisions & Architecture

This document outlines the architectural choices and bug fixes applied to build the Quality Assurance framework for the ammeter emulator assignment.

## 1. Unified Measurement API & Orchestration
* **Unified Testing Interface:** Created a single testing framework to handle all three devices. Instead of writing separate, hardcoded test functions for the Greenlee, ENTES, and CIRCUTOR emulators, the testing script loops through the devices and pulls their specific ports and commands directly from the YAML configuration file.

## 2. Configuration-Driven Architecture
* **Defensive YAML Parsing:** The framework is dynamically controlled via `config.yaml`. To ensure safe execution, the backend utilizes safe dictionary `.get()` chaining and `NULL` value fallbacks. If configuration values are left empty or commented out, the system automatically falls back to safe runtime defaults (e.g., enforcing a `5.0` second socket timeout) rather than crashing.

## 3. Result Analysis & Object-Oriented Design
* **Stateless Processing:** Statistical calculation logic (mean, median, standard deviation) is encapsulated as a stateless static method.
* **Data Visualization:** Integrated `matplotlib` to automatically generate `measurement_comparison.png`, visualizing the mathematical variance between the different hardware emulation implementations (Ohm's Law vs. Hall Effect vs. Rogowski Coil).

## 4. Legacy Code Removal
* **Legacy Code Removal:** The provided `examples/run_tests.py` script was explicitly marked as a "lazy example" not intended for use. To ensure a clean repository, this was removed, leaving `src/run_qa.py` as the clear execution entry point.

## 5. Original Template Bug Fixes
During development, three critical bugs within the provided template codebase were fixed to ensure functional execution:
* **Fixed Execution Block (`main.py`)**: The provided template had the `request_current_from_ammeter` execution calls commented out because the hardcoded byte commands were incomplete and would have been rejected by the servers. To make `main.py` work and successfully return data, I uncommented this block and corrected the byte strings by appending the required command flags (e.g., changing `b'MEASURE_GREENLEE'` to `b'MEASURE_GREENLEE -get_measurement'`).
* **Fixed wrong port numbers and missing flag**: the original `README.md` and `config.yaml` listed ports `5000–5002` instead of `5001–5003` and omitted the `-current` flag from the CIRCUTOR command. I uncommented the calls in `main.py` and updated the commands and ports across all files to match the emulator implementations (`GreenleeAmmeter`, `EntesAmmeter`, and `CircutorAmmeter`).
* **Daemon Thread Termination (`main.py`)**: The provided `main.py` template ended with a `pass` statement. This caused the main thread to exit instantly, abruptly killing the `daemon=True` emulator threads before the QA suite could connect. I replaced this with an infinite `while True` loop to keep the local sockets listening and allow graceful shutdowns via `Ctrl+C`.
* **Missing Logger Handler (`src/utils/logger.py`)**: The original `TestLogger` class defined a log file path but never attached a `logging.FileHandler`. I updated `_setup_logger` to properly bind the handler and set a `DEBUG` level, ensuring the statistical test results successfully write to the `results/logs/` directory.