import time
import os
import matplotlib.pyplot as plt
from testing.test_framework import AmmeterTestFramework


def plot_results(all_results: dict):
    """Generates a comparative visual report for the sampled ammeter measurements."""
    os.makedirs("results", exist_ok=True)
    plt.figure(figsize=(10, 6))

    for device, data in all_results.items():
        if "error" in data or not data.get("raw_measurements"):
            continue

        measurements = data["raw_measurements"]
        mean_val = data['statistics']['mean']
        plt.plot(measurements, marker='o', label=f"{device} (Mean: {mean_val:.2f}A)")

    plt.title("Ammeter Measurement Consistency Comparison")
    plt.xlabel("Sample Number")
    plt.ylabel("Current (Amperes)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    output_path = "results/measurement_comparison.png"
    plt.savefig(output_path)
    print(f"\nVisualization saved to {output_path}")


def main():
    print("Initializing QA Test Framework...")
    framework = AmmeterTestFramework()

    target_devices = ["Greenlee", "Entes", "Circutor"]
    all_results = {}

    for device in target_devices:
        print(f"\n--- Testing {device} Ammeter ---")
        results = framework.run_test(device)
        all_results[device] = results

        if "error" not in results:
            stats = results.get("statistics", {})
            print(f"Samples collected: {results.get('successful_samples')}/{results.get('requested_samples')}")
            print(f"Mean: {stats.get('mean', 0):.4f} A | Std Dev: {stats.get('std_dev', 0):.4f} A")
        else:
            print(f"Test failed: {results['error']}")

        # Brief pause to ensure socket teardown between connections
        time.sleep(1)

    # Generate the visual report
    plot_results(all_results)
    print("Check results/logs/ for detailed execution logs.")


if __name__ == "__main__":
    main()