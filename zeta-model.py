import numpy as np
from mpmath import zeta, mp
import matplotlib.pyplot as plt

# Set precision for mpmath
mp.dps = 15

def load_known_zeros(file_path, max_zeros=100000):
    """Load known zeta zeros from a file."""
    try:
        with open(file_path, 'r') as f:
            zeros = []
            for _ in range(max_zeros):
                line = f.readline()
                if not line:
                    break
                zero = float(line.strip())
                zeros.append(zero)
        known_zeros = np.array(zeros)
        known_zeros.sort()
        return known_zeros
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except ValueError as e:
        print(f"Error: Invalid data format in '{file_path}'. {e}")
        return None

def zeta_magnitude(t):
    """Compute the magnitude of the Riemann zeta function at s = 0.5 + it."""
    s = mp.mpc(0.5, t)
    return float(abs(zeta(s)))

def find_closest_zero(predicted_t, known_zeros):
    """Find the closest known zero to the predicted zero."""
    idx = np.searchsorted(known_zeros, predicted_t)
    if idx == 0:
        return known_zeros[0]
    elif idx == len(known_zeros):
        return known_zeros[-1]
    else:
        before = known_zeros[idx - 1]
        after = known_zeros[idx]
        return before if abs(predicted_t - before) <= abs(predicted_t - after) else after

def predict_refined_zeros(training_zeros, num_predictions, phase_shift=0.1, oscillation_amplitude=0.2):
    """
    Predict additional zeros using a refined oscillatory model.
    """
    spacings = np.diff(training_zeros)
    average_spacing = np.mean(spacings)
    predicted_zeros = []
    last_zero = training_zeros[-1]

    for i in range(num_predictions):
        # Introduce refined oscillation
        oscillation = oscillation_amplitude * np.sin(i * phase_shift)
        new_zero = last_zero + average_spacing + oscillation
        predicted_zeros.append(new_zero)
        last_zero = new_zero

    return np.array(predicted_zeros)

def refine_predictions(predicted_zeros, known_zeros):
    """
    Apply residual correction for oscillatory patterns in predictions.
    """
    residuals = [predicted_t - find_closest_zero(predicted_t, known_zeros) for predicted_t in predicted_zeros]
    indices = np.arange(len(residuals))

    # Fit a linear trend to the residuals and remove it
    trend = np.polyfit(indices, residuals, 4)
    residual_correction = residuals - (trend[0] * indices + trend[1])
    corrected_zeros = predicted_zeros - residual_correction

    return corrected_zeros

def validate_predictions(predicted_zeros, known_zeros):
    """
    Validate predicted zeros against known zeros.
    """
    validated = []
    invalid = []
    for t_pred in predicted_zeros:
        closest_t = find_closest_zero(t_pred, known_zeros)
        int_pred = int(np.floor(t_pred))
        int_closest = int(np.floor(closest_t))
        if int_pred == int_closest:
            validated.append((t_pred, closest_t))
        else:
            invalid.append((t_pred, closest_t))
    return validated, invalid

# Enhanced Main Script
if __name__ == "__main__":
    # Load known zeros
    file_path = 'zeta.txt'  # Update this path to the actual file location
    known_zeros = load_known_zeros(file_path, max_zeros=100000)

    if known_zeros is not None:
        # Split into training and validation sets
        training_set = known_zeros[:100]
        validation_set = known_zeros[100:]

        # Predict zeros
        predicted_zeros = predict_refined_zeros(training_set, num_predictions=100000)

        # Refine predictions with residual corrections
        refined_zeros = refine_predictions(predicted_zeros, validation_set)

        # Validate refined predictions
        validated, invalid = validate_predictions(refined_zeros, validation_set)

        # Output Results
        print(f"Total Predicted Zeros: {len(refined_zeros)}")
        print(f"Validated Zeros: {len(validated)}")
        print(f"Invalid Zeros: {len(invalid)}")
        val = []
        if validated:
            print("\nValidated Zeros:")
            for t_pred, t_closest in validated:
                if t_pred in val:
                   break
                if t_pred not in val:
                   print(f"Predicted t = {t_pred:.6f}, Closest Zero t = {t_closest:.6f}")
                   val.append(t_pred)
                   
        if invalid:
            print("\nInvalid Zeros:")
            for t_pred, t_closest in invalid:
                print(f"Predicted t = {t_pred:.6f}, Closest Zero t = {t_closest:.6f}")

        # Visualization
        validated_t = [t[0] for t in validated]
        invalid_t = [t[0] for t in invalid]
        plt.scatter(validated_t, [0] * len(validated_t), color='blue', label='Validated', marker='o')
        plt.scatter(invalid_t, [0] * len(invalid_t), color='red', label='Invalid', marker='x')
        plt.xlabel('t')
        plt.title('Validation Results')
        plt.legend()
        plt.show()
