# Ammeter Emulators & QA Framework

This project provides emulators for different types of ammeters (Greenlee, ENTES, and CIRCUTOR) alongside a Quality Assurance testing framework to validate them. Each ammeter emulator runs on a separate thread and responds to current measurement requests via TCP socket communication.

## Project Structure

- `Ammeters/`
  - `base_ammeter.py`: Abstract base class for all ammeter emulators.
  - `Circutor_Ammeter.py`: Emulator for the CIRCUTOR ammeter.
  - `Entes_Ammeter.py`: Emulator for the ENTES ammeter.
  - `Greenlee_Ammeter.py`: Emulator for the Greenlee ammeter.
  - `client.py`: Base client to request current measurements.
- `config/`
  - `config.yaml`: Configuration file for ammeter parameters and test suite tuning.
- `src/`
  - `run_qa.py`: Main Quality Assurance orchestrator script.
  - `testing/`
    - `test_framework.py`: Unified API framework for socket management and statistical analysis.
  - `utils/`
    - `config.py`, `logger.py`, `Utils.py`: Helper modules for configuration loading, logging, and data generation.
- `main.py`: Main script to initialize and start the ammeter emulator servers.
- `requirements.txt`: Python package dependencies.
- `results/`: Generated post-execution. Included in the GitHub repo per request to include Sample test results.
  - `logs/`: Execution archives containing historical test data and statistical aggregations.
  - `measurement_comparison.png`: Generated visualization plots.
  - `main_execution_sample.txt`: Sample main execution output as requested.
- `design_decisions.md`: A document that details sode design decisions as requested.
- `README.md`: The file you are currently reading.

## Installation & Requirements
Ensure you are running **Python 3.9+**. Install the required dependencies (matplotlib, pyyaml) using pip:
```sh
pip install -r requirements.txt
```

## Usage

### 1. Start the Ammeter Emulators
To initialize the hardware emulators and open the local TCP sockets, run the `main.py` script:
```sh
python main.py
```
*(Keep this terminal window running to host the local sockets. Press `Ctrl+C` to gracefully shut down the servers when testing is complete).*

### 2. Execute the QA Suite
Open a second terminal window in the project root and trigger the testing framework:
```sh
python src/run_qa.py
```

## Ammeter Specifications

### Greenlee Ammeter
- **Port**: 5001
- **Command**: `MEASURE_GREENLEE -get_measurement`
- **Measurement Logic**: Calculates current using voltage (1V - 10V) and (0.1Ω - 100Ω).
- **Measurement method**: Ohm's Law: I = V / R

### ENTES Ammeter
- **Port**: 5002
- **Command**: `MEASURE_ENTES -get_data`
- **Measurement Logic**: Calculates current using magnetic field strength (0.01T - 0.1T) and calibration factor (500 - 2000).
- **Measurement method**: Hall Effect: I = B * K

### CIRCUTOR Ammeter
- **Port**: 5003
- **Command**: `MEASURE_CIRCUTOR -get_measurement -current`
- **Measurement Logic**: Calculates current using voltage values (0.1V - 1.0V) over a number of samples and a random time step (0.001s - 0.01s).
- **Measurement method**: Rogowski Coil Integration: I = ∫V dt