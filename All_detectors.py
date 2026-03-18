import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, Button

# -------------------------------------------------
# Sources (hidden identities for assignment)
# -------------------------------------------------
sources = {
    "Isotope A": [511, 909],       # Zr-89
    "Isotope B": [662],            # Cs-137
    "Isotope C": [1173, 1332]      # Co-60
}

# Plateau activities
target_activity = {
    "Isotope A": 500e3,
    "Isotope B": 200e3,
    "Isotope C": 200e3
}

# GM efficiencies (tuned for realistic CPS)
gm_efficiency = {
    "Isotope A": 0.015,
    "Isotope B": 0.05,
    "Isotope C": 0.03
}

W = 30  # eV per ion pair

# -------------------------------------------------
# Physics
# -------------------------------------------------
def primary_ionisation(E_keV):
    return (E_keV * 1000) / W

def voltage_response(voltage, mode):
    if voltage < 100:
        return 0.01 + 0.99 * (voltage / 100)
    elif voltage < 200:
        return 1.0
    elif voltage < 800:
        return 1.0 + 4 * (voltage - 200) / 600
    elif voltage < 1200:
        return 5.0
    else:
        return 5.0

# -------------------------------------------------
# Simulation
# -------------------------------------------------
def simulate(voltage, source, n_events, mode):
    energies = np.random.choice(sources[source], size=n_events)
    pairs = primary_ionisation(energies)
    gain = voltage_response(voltage, mode)
    signals = []

    valid_ranges = {
        "Ionisation": (100, 200),
        "Proportional": (200, 800),
        "GM": (800, 1200)
    }

    vmin, vmax = valid_ranges[mode]

    for p in pairs:
        fluct = np.random.normal(1, 0.05)
        if voltage < vmin or voltage > vmax:
            if mode == "Ionisation":
                signal = np.random.normal(0.05, 0.02) * p
            elif mode == "Proportional":
                signal = np.random.normal(0.5, 0.2)
            elif mode == "GM":
                signal = np.random.choice([0, 1], p=[0.9, 0.1])
        else:
            if mode == "GM":
                signal = 1
            else:
                signal = p * gain * fluct
        signals.append(signal)

    return np.array(signals), energies

# -------------------------------------------------
# Plot setup
# -------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9))
plt.subplots_adjust(left=0.28, bottom=0.3, hspace=0.45)

voltage0 = 400
n_events0 = 100
mode0 = "Ionisation"
source0 = "Isotope A"

# -------------------------------------------------
# Redraw
# -------------------------------------------------
def redraw(voltage, source, n_events, mode):
    ax1.clear()
    ax2.clear()

    signals, energies = simulate(voltage, source, n_events, mode)

    # ---------------- Ionisation ----------------
    if mode == "Ionisation":
        time = np.linspace(0, 1, len(signals))
        current = signals / max(signals) * 1e-12 if max(signals) > 0 else signals

        ax1.plot(time, current)
        ax1.set_title("Ionisation Chamber Output", pad=15)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Current (A)")

        if voltage < 100:
            activity_display = target_activity[source] * np.random.uniform(0.1, 0.6)
        elif 100 <= voltage <= 200:
            activity_display = target_activity[source] * np.random.uniform(0.95, 1.05)
        else:
            activity_display = target_activity[source] * np.random.uniform(0.7, 1.3)

        ax1.text(0.02, 0.85,
                 f"Estimated Activity: {activity_display/1e3:.1f} kBq",
                 transform=ax1.transAxes,
                 bbox=dict(facecolor='white', alpha=0.7))

    # ---------------- Proportional ----------------
    elif mode == "Proportional":
        n_sim = n_events * 200  # increase counts for smooth spectra
        spectrum = []

        for E in np.random.choice(energies, size=n_sim):

            if source == "Isotope B":  # Cs-137
                # Photopeak
                if np.random.rand() < 0.6:
                    spectrum.append(np.random.normal(662, 10))
                # Compton continuum
                if np.random.rand() < 0.4:
                    spectrum.append(np.random.uniform(0, 480))
                # Backscatter
                if np.random.rand() < 0.15:
                    spectrum.append(np.random.normal(180, 15))
                # Background
                if np.random.rand() < 0.25:
                    spectrum.append(np.random.uniform(0, 150))

            elif source == "Isotope C":  # Co-60
                # Photopeaks
                if np.random.rand() < 0.35:
                    spectrum.append(np.random.normal(1173, 10))
                if np.random.rand() < 0.35:
                    spectrum.append(np.random.normal(1332, 10))
                # Compton continuum
                if np.random.rand() < 0.6:
                    spectrum.append(np.random.uniform(0, 1170))
                if np.random.rand() < 0.6:
                    spectrum.append(np.random.uniform(0, 1325))
                # Backscatter
                if np.random.rand() < 0.2:
                    spectrum.append(np.random.normal(200, 40))
                # Sum peak
                if np.random.rand() < 0.08:
                    spectrum.append(1173+1332)
                # Background
                if np.random.rand() < 0.2:
                    spectrum.append(np.random.uniform(0, 200))

            elif source == "Isotope A":  # Zr-89
                # Low-energy broad structure
                if np.random.rand() < 0.5:
                    spectrum.append(np.random.uniform(50, 450))
                # Peaks at 511 and 909
                if np.random.rand() < 0.3:
                    spectrum.append(np.random.normal(511, 30))
                if np.random.rand() < 0.3:
                    spectrum.append(np.random.normal(909, 30))
                # Background
                if np.random.rand() < 0.25:
                    spectrum.append(np.random.uniform(0, 400))

        spectrum = np.array(spectrum)
        spectrum = spectrum[spectrum > 0]

        ax1.hist(spectrum, bins=400, histtype='step', linewidth=1.5)
        ax1.set_title("Energy Spectrum", pad=15)
        ax1.set_xlabel("Energy (keV)")
        ax1.set_ylabel("Counts")

    # ---------------- GM ----------------
    elif mode == "GM":
        time_bins = np.linspace(0, 1, 20)
        counts, _ = np.histogram(np.random.uniform(0, 1, len(signals)), bins=time_bins)

        ax1.step(time_bins[:-1], counts, where='post')
        ax1.set_title("GM Counter Output", pad=15)
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Counts")

        true_cps = target_activity[source] * gm_efficiency[source]

        if voltage < 800:
            cps_display = true_cps * np.random.uniform(0.05, 0.3)
        elif 800 <= voltage <= 1200:
            cps_display = true_cps * np.random.uniform(0.9, 1.1)
        else:
            cps_display = true_cps * np.random.uniform(0.5, 1.5)

        ax1.text(0.02, 0.85,
                 f"Count rate ≈ {cps_display:.0f} cps",
                 transform=ax1.transAxes,
                 bbox=dict(facecolor='white', alpha=0.7))

    # ---------------- Voltage curve ----------------
    V = np.linspace(0, 1500, 300)
    response = [voltage_response(v, mode) for v in V]

    ax2.plot(V, response)
    ax2.axvline(voltage, linestyle='--')
    ax2.set_title("Detector Response vs Voltage", pad=15)
    ax2.set_xlabel("Voltage (V)")
    ax2.set_ylabel("Signal")
    ax2.grid(alpha=0.3)

# Initial draw
redraw(voltage0, source0, n_events0, mode0)

# -------------------------------------------------
# Widgets
# -------------------------------------------------
ax_voltage = plt.axes([0.28, 0.2, 0.6, 0.03])
ax_events  = plt.axes([0.28, 0.15, 0.6, 0.03])

s_voltage = Slider(ax_voltage, "Voltage (V)", 0, 1500, valinit=voltage0)
s_events  = Slider(ax_events, "Events", 10, 500, valinit=n_events0, valstep=10)

ax_radio_mode = plt.axes([0.02, 0.6, 0.2, 0.2])
radio_mode = RadioButtons(ax_radio_mode, ("Ionisation", "Proportional", "GM"))

ax_radio_source = plt.axes([0.02, 0.35, 0.2, 0.2])
radio_source = RadioButtons(ax_radio_source, tuple(sources.keys()))

ax_button = plt.axes([0.02, 0.2, 0.15, 0.08])
btn = Button(ax_button, "New Data")

def update(val):
    redraw(s_voltage.val, radio_source.value_selected, int(s_events.val), radio_mode.value_selected)

s_voltage.on_changed(update)
s_events.on_changed(update)

radio_mode.on_clicked(lambda label: redraw(s_voltage.val, radio_source.value_selected, int(s_events.val), label))
radio_source.on_clicked(lambda label: redraw(s_voltage.val, label, int(s_events.val), radio_mode.value_selected))
btn.on_clicked(lambda event: redraw(s_voltage.val, radio_source.value_selected, int(s_events.val), radio_mode.value_selected))

plt.show()