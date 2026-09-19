"""
Turn a PhysioNet/CinC Challenge 2015 record into a text `state` block for Jev.

Not copied from NeillWhite/icu-false-alarm-reduction (that repo carries no
license) -- independently written against the same open dataset, using only
MIT-licensed wfdb/neurokit2. Deliberately smaller than that repo's Model 2:
no signal-quality-index gating via neurokit2's expensive quality functions,
no cross-channel peak matching -- just heart-rate-by-window plus a cheap
flatline/clipping heuristic, closer in scope to their "Model 1 naive" baseline.
"""
import json
import sys
from pathlib import Path

import neurokit2 as nk
import numpy as np
import pandas as pd
import wfdb

RAW_DIR = Path("data/raw/training")
SAMPLE_CSV = Path("data/raw/sample.csv")
OUT_JSON = Path("data/cases.json")

ALARM_TYPE_LABELS = {
    "Asystole": "Asystole (ASY) -- no discernible heartbeat for >=4s",
    "Bradycardia": "Extreme Bradycardia (EBR) -- heart rate <=40bpm sustained for >=5 beats",
    "Tachycardia": "Extreme Tachycardia (ETC) -- heart rate >=140bpm sustained for >=17 beats",
    "Ventricular_Tachycardia": "Ventricular Tachycardia (VTA) -- >=5 beats of ventricular tachycardia",
    "Ventricular_Flutter_Fib": "Ventricular Flutter/Fibrillation (VFB) -- fibrillatory ECG for >=4s",
}

ECG_LIKE = {"I", "II", "III", "AVR", "AVL", "AVF", "MCL", "MCL1", "V"}


def signal_quality_flag(sig: np.ndarray) -> str:
    if len(sig) == 0:
        return "no signal"
    diffs = np.abs(np.diff(sig))
    flat_frac = float(np.mean(diffs < 1e-6))
    lo, hi = np.min(sig), np.max(sig)
    clip_frac = float(np.mean(np.isclose(sig, hi) | np.isclose(sig, lo)))
    if flat_frac > 0.3:
        return f"flatline suspected ({flat_frac:.0%} near-zero deltas)"
    if clip_frac > 0.05:
        return f"clipping suspected ({clip_frac:.0%} at signal extremes)"
    return "no obvious artifact"


def ecg_hr_trend(sig: np.ndarray, fs: float, alarm_time_s: float, window_s: int = 10):
    """Returns (full_trend, near_alarm_summary, error). `alarm_time_s` anchors
    the "near alarm" window to the actual alarm trigger point, not just the
    end of the file -- 'l' records carry a 30s retrospective tail *after* the
    alarm, so "last N seconds of the recording" would look past the event."""
    try:
        cleaned = nk.ecg_clean(sig, sampling_rate=fs)
        _, info = nk.ecg_peaks(cleaned, sampling_rate=fs)
        rpeaks = np.asarray(info["ECG_R_Peaks"])
        if len(rpeaks) < 3:
            return None, None, f"too few R-peaks detected ({len(rpeaks)})"
        rr = np.diff(rpeaks) / fs
        hr = 60.0 / rr
        times = rpeaks[1:] / fs
        n_windows = max(1, int(len(sig) / fs // window_s))
        trend = []
        for w in range(n_windows):
            mask = (times >= w * window_s) & (times < (w + 1) * window_s)
            if mask.sum() > 0:
                trend.append(round(float(hr[mask].mean()), 1))
        if not trend:
            return None, None, "no windows with detected beats"

        near_mask = (times >= alarm_time_s - 30) & (times <= alarm_time_s)
        if near_mask.sum() > 0:
            # Instantaneous beat-to-beat HR is fragile: one misdetected/extra
            # peak produces an outlier RR interval and a wild instantaneous
            # rate. Median + IQR is far more robust to that than min/max.
            near_hr = hr[near_mask]
            near_summary = {
                "window": "last 30s before the alarm trigger",
                "median_bpm": round(float(np.median(near_hr)), 1),
                "iqr_bpm": [round(float(np.percentile(near_hr, 25)), 1), round(float(np.percentile(near_hr, 75)), 1)],
                "n_beats": int(near_mask.sum()),
            }
        else:
            near_summary = None
        return trend, near_summary, None
    except Exception as exc:  # noqa: BLE001 -- record this as a feature-extraction failure, not a crash
        return None, None, f"peak detection failed: {exc}"


def build_state(rec_name: str, alarm_type: str) -> tuple[str, dict]:
    rec = wfdb.rdrecord(str(RAW_DIR / rec_name))
    fs = float(rec.fs)
    sig_names = rec.sig_name
    duration_s = rec.sig_len / fs
    # 'l' records carry a 30s retrospective tail recorded *after* the alarm;
    # 's' records stop recording at the alarm itself.
    alarm_time_s = duration_s - 30.0 if rec_name.endswith("l") else duration_s
    lines = [
        f"Bedside monitor alarm triggered: {ALARM_TYPE_LABELS[alarm_type]}",
        f"Channels recorded: {', '.join(sig_names)} (sampling rate {fs:.0f} Hz)",
        f"Recording covers {duration_s:.0f}s of monitor data; the alarm fired at "
        f"the {alarm_time_s:.0f}s mark of this recording.",
        "",
    ]
    debug = {"channels": {}, "alarm_time_s": alarm_time_s, "duration_s": duration_s}
    for i, name in enumerate(sig_names):
        sig = rec.p_signal[:, i]
        sig = sig[~np.isnan(sig)]
        chan_debug = {"n_samples": int(len(sig))}
        if len(sig) == 0:
            lines.append(f"- {name}: no signal recorded")
            debug["channels"][name] = chan_debug
            continue
        qflag = signal_quality_flag(sig)
        chan_debug["quality"] = qflag
        if name in ECG_LIKE:
            trend, near_summary, err = ecg_hr_trend(sig, fs, alarm_time_s)
            chan_debug["hr_trend"] = trend
            chan_debug["hr_near_alarm"] = near_summary
            chan_debug["hr_error"] = err
            if trend:
                near_txt = (
                    f"in the {near_summary['window']}: {near_summary['n_beats']} beats detected, "
                    f"median {near_summary['median_bpm']} bpm (IQR {near_summary['iqr_bpm'][0]}-{near_summary['iqr_bpm'][1]})"
                    if near_summary
                    else "no beats detected in the 30s before the alarm"
                )
                lines.append(
                    f"- {name} (ECG lead): signal quality = {qflag}. "
                    f"Heart rate {near_txt}. "
                    f"Full-recording heart rate by 10s window (bpm, earliest to latest) = {trend}"
                )
            else:
                lines.append(f"- {name} (ECG lead): signal quality = {qflag}; heart rate not computable ({err})")
        elif name == "PLETH":
            lines.append(f"- {name} (plethysmograph, an independent pulsatile channel): signal quality = {qflag}")
        elif name == "ABP":
            lines.append(f"- {name} (arterial blood pressure waveform, an independent pulsatile channel): signal quality = {qflag}")
        elif name == "RESP":
            lines.append(f"- {name} (respiration waveform): signal quality = {qflag}")
        else:
            lines.append(f"- {name}: signal quality = {qflag}")
        debug["channels"][name] = chan_debug
    return "\n".join(lines), debug


def main():
    sample = pd.read_csv(SAMPLE_CSV)
    cases = []
    for _, row in sample.iterrows():
        rec_name, alarm_type, true_alarm = row["record"], row["type"], int(row["true_alarm"])
        try:
            state, debug = build_state(rec_name, alarm_type)
        except Exception as exc:  # noqa: BLE001
            print(f"!! {rec_name}: FAILED to build state: {exc}", file=sys.stderr)
            continue
        cases.append(
            {
                "id": rec_name,
                "alarm_type": alarm_type,
                "true_alarm": true_alarm,
                "state": state,
                "_debug": debug,
            }
        )
        print(f"-- {rec_name} ({alarm_type}, true_alarm={true_alarm}) --")
        print(state)
        print()

    OUT_JSON.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    print(f"Wrote {len(cases)}/{len(sample)} cases to {OUT_JSON}")


if __name__ == "__main__":
    main()
