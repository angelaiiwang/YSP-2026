"""
FSL Auto-Tune Simulator
========================
Simulates a bank of Frequency Selective Limiter (FSL) response curves,
one per tuning "code" (e.g. a DAC/varactor step, ~10-20 discrete
settings), since real hardware data isn't available yet. Each code
shifts the limiter's notch/minimum to a different center frequency.

Auto-tuning searches the synthesized code bank and selects the code
whose minimum lands closest to a fixed target frequency (a "set value"
for now, no live tracking), then plots before vs after.

Requirements: numpy, pandas, matplotlib
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['font.family'] = 'serif'

class FSLSimulator:
    def __init__(self, n_codes=16, freq_min=80.0, freq_max=120.0,
                 q_nominal=25.0, depth_nominal_dB=25.0,
                 n_points=400, seed=42):
        self.n_codes = n_codes
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.q_nominal = q_nominal
        self.depth_nominal_dB = depth_nominal_dB
        self.freq_axis = np.linspace(freq_min, freq_max, n_points)
        self.rng = np.random.default_rng(seed)

        self.codes = np.arange(1, n_codes + 1)
        self.tables = {}          # code -> DataFrame(frequency_MHz, response_dB)
        self.lookup_table = None  # code -> measured_min_freq_MHz, measured_min_dB

        self._synthesize_bank()

    # ------------------------------------------------------------------
    # Synthesis
    # ------------------------------------------------------------------
    @staticmethod
    def _lorentzian(freq, f_center, Q, depth_dB):
        detuning = (freq - f_center) / (f_center / Q)
        return -depth_dB / (1 + detuning ** 2)

    def _synthesize_bank(self):
        """Build one synthetic response table per code, with a
        code -> center-frequency mapping that is mostly linear plus a
        little bow and jitter, to mimic real hardware nonidealities."""
        span = self.freq_max - self.freq_min
        ideal_centers = np.linspace(self.freq_min + 0.15 * span,
                                     self.freq_max - 0.15 * span,
                                     self.n_codes)
        bow = 0.4 * np.sin(np.linspace(0, np.pi, self.n_codes))
        jitter = self.rng.normal(0, 0.15, self.n_codes)
        center_freqs = ideal_centers + bow + jitter

        records = []
        for code, f_c in zip(self.codes, center_freqs):
            Q_c = max(5.0, self.q_nominal + self.rng.normal(0, 1.0))
            depth_c = max(3.0, self.depth_nominal_dB + self.rng.normal(0, 0.8))
            resp = self._lorentzian(self.freq_axis, f_c, Q_c, depth_c)
            resp = resp + self.rng.normal(0, 0.05, resp.shape)  # measurement noise

            self.tables[code] = pd.DataFrame({
                "frequency_MHz": self.freq_axis,
                "response_dB": resp,
            })

            idx_min = int(np.argmin(resp))
            records.append({
                "code": code,
                "measured_min_freq_MHz": self.freq_axis[idx_min],
                "measured_min_dB": resp[idx_min],
            })

        self.lookup_table = pd.DataFrame(records)

    # ------------------------------------------------------------------
    # Auto-tuning
    # ------------------------------------------------------------------
    def find_best_code(self, target_freq_MHz):
        """Nearest-neighbor search: pick the code whose calibrated
        minimum sits closest to the fixed target frequency."""
        diffs = (self.lookup_table["measured_min_freq_MHz"] - target_freq_MHz).abs()
        best_row = self.lookup_table.loc[diffs.idxmin()]
        return int(best_row["code"])

    def get_curve(self, code):
        return self.tables[code]

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    def plot_before_after(self, target_freq_MHz, initial_code=None,
                           show_all_codes=True, save_path=None):
        if initial_code is None:
            initial_code = int(self.codes[0])

        best_code = self.find_best_code(target_freq_MHz)

        df_before = self.tables[initial_code]
        df_after = self.tables[best_code]

        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot all synthesized codes in the background
        if show_all_codes:
            for code, df in self.tables.items():
                ax.plot(df.frequency_MHz, df.response_dB,
                        color="dimgray", lw=1, alpha=0.6, zorder=1)
            ax.plot([], [], color="dimgray", lw=1,
                    label=f"All {self.n_codes} synthesized codes")

        ax.plot(df_before.frequency_MHz, df_before.response_dB,
                color="tab:red", lw=2, linestyle="--", zorder=2,
                label=f"Before tuning (code {initial_code})")
        ax.plot(df_after.frequency_MHz, df_after.response_dB,
                color="tab:green", lw=2.5, zorder=3,
                label=f"After tuning (code {best_code})")
        
        #Target line annotation
        ax.axvline(target_freq_MHz, color="blue", lw=1.2, linestyle=":",
                   label=f"Target = {target_freq_MHz:.2f} MHz")

        after_min_freq = self.lookup_table.loc[
            self.lookup_table["code"] == best_code, "measured_min_freq_MHz"].iloc[0]
        after_min_dB = self.lookup_table.loc[
            self.lookup_table["code"] == best_code, "measured_min_dB"].iloc[0]
        ax.plot(after_min_freq, after_min_dB, "o", color="tab:green", ms=8, zorder=4)

        #Green arrow annotation for the minimum point after tuning
        ax.annotate(f"min @ {after_min_freq:.2f} MHz\n({after_min_dB:.1f} dB)",
                    xy=(after_min_freq, after_min_dB),
                    xytext=(after_min_freq-7, after_min_dB - 5),
                    fontsize=9, color="tab:green",
                    arrowprops=dict(arrowstyle="->", color="tab:green"))

        ax.set_title("FSL Auto-Tuning (Synthesized Codes): Before vs After")
        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("Response (dB)")
        ax.set_ylim(-self.depth_nominal_dB - 8, 5)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower right", fontsize=9)
        fig.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=200)

        return fig, ax, best_code


# ---------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------
if __name__ == "__main__":
    sim = FSLSimulator(n_codes=16, freq_min=80.0, freq_max=120.0, seed=7)

    print("Synthesized code -> minimum frequency lookup table:")
    print(sim.lookup_table.to_string(index=False))

    TARGET_FREQ = 103.5  # <-- the fixed "set value" target for now

    best_code = sim.find_best_code(TARGET_FREQ)
    print(f"\nTarget frequency: {TARGET_FREQ} MHz")
    print(f"Selected code: {best_code}")

    fig, ax, best_code = sim.plot_before_after(
        target_freq_MHz=TARGET_FREQ,
        initial_code=1,
        save_path=".\\FSL_Autotune\\fsl_autotune_synthesized.png",
    )
    plt.show()

    sim.lookup_table.to_csv(".\\FSL_Autotune\\fsl_lookup_table.csv", index=False)