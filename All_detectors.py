import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# -------------------------------------------------
# Sources
# -------------------------------------------------
sources = {
    "Isotope A": [511, 909],       # Zr-89
    "Isotope B": [662],            # Cs-137
    "Isotope C": [1173, 1332]      # Co-60
}

target_activity = {
    "Isotope A": 500e3,
    "Isotope B": 200e3,
    "Isotope C": 200e3
}

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
# Streamlit UI
# -------------------------------------------------
st.title("Radiation Detector Simulator")

col1, col2 = st.columns(2)

with col1:
    voltage = st.slider("Voltage (V)", 0, 1500, 400)
    n_events = st.slider("Number of Events", 10, 500, 100)

with col2:
    mode = st.radio("Detector Mode", ["Ionisation", "Proportional", "GM"])
    source = st.radio("Source", list(sources.keys()))

# -------------------------------------------------
# Plot
# -------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

signals, energies = simulate(voltage, source, n_events, mode)

# ---------------- Ionisation ----------------
if mode == "Ionisation":
    time = np.linspace(0, 1, len(signals))
    current = signals / max(signals) * 1e-12 if max(signals) > 0 else signals

    ax1.plot(time, current)
    ax1.set_title("Ionisation Chamber Output")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Current (A)")

    if voltage < 100:
        activity_display = target_activity[source] * np.random.uniform(0.1, 0.6)
    elif 100 <= voltage <= 200:
        activity_display = target_activity[source] * np.random.uniform(0.95, 1.05)
    else:
        activity_display = target_activity[source] * np.random.uniform(0.7, 1.3)

    ax1.text(0.05, 0.85,
             f"Estimated Activity: {activity_display/1e3:.1f} kBq",
             transform=ax1.transAxes)

# ---------------- Proportional ----------------
elif mode == "Proportional":
    spectrum = []

    n_sim = n_events * 150  # balanced performance vs quality

    for _ in range(n_sim):

        if source == "Isotope B":  # Cs-137
            if np.random.rand() < 0.6:
                spectrum.append(np.random.normal(662, 10))
            if np.random.rand() < 0.4:
                spectrum.append(np.random.uniform(0, 480))
            if np.random.rand() < 0.15:
                spectrum.append(np.random.normal(180, 15))

        elif source == "Isotope C":  # Co-60
            if np.random.rand() < 0.35:
                spectrum.append(np.random.normal(1173, 10))
            if np.random.rand() < 0.35:
                spectrum.append(np.random.normal(1332, 10))
            if np.random.rand() < 0.5:
                spectrum.append(np.random.uniform(0, 1200))
            if np.random.rand() < 0.05:
                spectrum.append(2505)  # sum peak

        elif source == "Isotope A":  # Zr-89
            if np.random.rand() < 0.4:
                spectrum.append(np.random.uniform(50, 450))
            if np.random.rand() < 0.3:
                spectrum.append(np.random.normal(511, 30))
            if np.random.rand() < 0.3:
                spectrum.append(np.random.normal(909, 30))

    spectrum = np.array(spectrum)
    spectrum = spectrum[spectrum > 0]

    ax1.hist(spectrum, bins=300, range=(0, 2500))
    ax1.set_xlim(0, 2500)
    ax1.set_title("Energy Spectrum")
    ax1.set_xlabel("Energy (keV)")
    ax1.set_ylabel("Counts")
    ax1.grid(alpha=0.3)

# ---------------- GM ----------------
elif mode == "GM":
    counts = np.sum(signals)

    ax1.bar(["Counts"], [counts])
    ax1.set_title("GM Counter Output")

    true_cps = target_activity[source] * gm_efficiency[source]

    if voltage < 800:
        cps_display = true_cps * np.random.uniform(0.05, 0.3)
    elif 800 <= voltage <= 1200:
        cps_display = true_cps * np.random.uniform(0.9, 1.1)
    else:
        cps_display = true_cps * np.random.uniform(0.5, 1.5)

    ax1.text(0.05, 0.85,
             f"Count rate ≈ {cps_display:.0f} cps",
             transform=ax1.transAxes)

# ---------------- Voltage curve ----------------
V = np.linspace(0, 1500, 300)
response = [voltage_response(v, mode) for v in V]

ax2.plot(V, response)
ax2.axvline(voltage, linestyle='--')
ax2.set_title("Detector Response vs Voltage")
ax2.set_xlabel("Voltage (V)")
ax2.set_ylabel("Signal")
ax2.grid(alpha=0.3)

# -------------------------------------------------
# Show in Streamlit
# -------------------------------------------------
st.pyplot(fig)
