import socket
import time
import statistics
from typing import Dict, List
from utils.config import load_config
from utils.logger import TestLogger


class AmmeterTestFramework:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.logger = TestLogger("ammeter_qa_framework")
        self.logger.info("Test framework initialized.")

        self.default_commands = {
            "Greenlee": {"port": 5001, "command": b'MEASURE_GREENLEE -get_measurement'},
            "Entes": {"port": 5002, "command": b'MEASURE_ENTES -get_data'},
            "Circutor": {"port": 5003, "command": b'MEASURE_CIRCUTOR -get_measurement -current'}
        }

    def _measure_once(self, port: int, command: bytes, timeout: float = 5.0) -> float:
        """Executes a single measurement via TCP socket with a configurable timeout."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect(('localhost', port))
                s.sendall(command)
                data = s.recv(1024)
                if data:
                    return float(data.decode('utf-8'))
                raise ValueError("No data received from emulator.")
        except Exception as e:
            self.logger.error(f"Measurement failed on port {port}: {str(e)}")
            raise

    @staticmethod
    def _calculate_statistics(measurements: List[float]) -> Dict[str, float]:
        """Computes mean, median, std_dev, min, and max for a list of measurements."""
        if not measurements:
            return {}
        return {
            "mean": statistics.mean(measurements),
            "median": statistics.median(measurements),
            "std_dev": statistics.stdev(measurements) if len(measurements) > 1 else 0.0,
            "min": min(measurements),
            "max": max(measurements),
            "sample_count": len(measurements)
        }

    def run_test(self, ammeter_type: str) -> Dict:
        """Executes the sampling loop for a specified ammeter based on configuration parameters."""
        self.logger.info(f"Starting QA test for: {ammeter_type}")

        ammeters_section = self.config.get("ammeters") or {}
        ammeter_cfg = (
                ammeters_section.get(ammeter_type)
                or ammeters_section.get(ammeter_type.lower())
                or {}
        )
        default_cfg = self.default_commands.get(ammeter_type, {})

        port = ammeter_cfg.get("port") or default_cfg.get("port")
        cmd_raw = ammeter_cfg.get("command")
        command = cmd_raw.encode("utf-8") if isinstance(cmd_raw, str) else default_cfg.get("command")

        testing_cfg = self.config.get("testing") or {}
        sampling_cfg = testing_cfg.get("sampling") or {}

        raw_samples = sampling_cfg.get("measurements_count")
        raw_duration = sampling_cfg.get("total_duration_seconds")
        raw_freq = sampling_cfg.get("sampling_frequency_hz")
        raw_timeout = testing_cfg.get("timeout_seconds")

        freq_hz = float(raw_freq) if isinstance(raw_freq, (int, float, str)) else 5.0
        timeout_sec = float(raw_timeout) if isinstance(raw_timeout, (int, float, str)) else 5.0

        if isinstance(raw_samples, (int, float, str)):
            num_samples = int(raw_samples)
        elif isinstance(raw_duration, (int, float, str)):
            num_samples = max(1, int(float(raw_duration) * freq_hz))
        else:
            num_samples = 10

        if raw_duration is not None and raw_freq is None and num_samples > 0:
            delay = float(raw_duration) / num_samples
        else:
            delay = 1.0 / freq_hz

        if not port or not isinstance(command, bytes):
            self.logger.error(f"Invalid configuration for {ammeter_type}")
            return {"error": "Invalid ammeter configuration"}

        measurements = []
        start_time = time.time()

        for i in range(num_samples):
            try:
                val = self._measure_once(int(port), command, timeout=timeout_sec)
                measurements.append(val)
                self.logger.debug(f"[{ammeter_type}] Sample {i + 1}/{num_samples}: {val}A")
            except Exception as e:
                self.logger.warning(f"[{ammeter_type}] Sample {i + 1} failed: {e}")
            time.sleep(delay)

        actual_duration = time.time() - start_time
        stats = self._calculate_statistics(measurements)

        test_results = {
            "ammeter_type": ammeter_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "requested_samples": num_samples,
            "successful_samples": len(measurements),
            "actual_duration_seconds": round(actual_duration, 4),
            "statistics": stats,
            "raw_measurements": measurements
        }

        self.logger.info(f"Test completed for {ammeter_type}. Stats: {stats}")
        return test_results