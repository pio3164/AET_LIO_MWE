#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


GPS_CSV = "rtk_data.csv"
AET_TXT = "odometry_trajectory.txt"

OUTPUT_METRICS_CSV = "aet_2d_metrics.csv"
OUTPUT_FIG = "gps_aet_2d_trajectory.png"

DO_RIGID_ALIGN_2D = True
FORCE_START_ALIGN = False
SHOW_FIGURE = True


def gps_lonlat_to_local_xy(lon, lat):
    """
     Convert latitude and longitude to local plane coordinates, unit in meters.
     Use WGS84 radius approximation
    """
    lon = np.asarray(lon, dtype=float)
    lat = np.asarray(lat, dtype=float)

    lon0 = lon[0]
    lat0 = lat[0]

    earth_radius = 6378137.0
    deg2rad = np.pi / 180.0

    x = (lon - lon0) * deg2rad * earth_radius * np.cos(lat0 * deg2rad)
    y = (lat - lat0) * deg2rad * earth_radius

    return x, y


def read_gps_pose_csv(gps_csv):
    if not os.path.isfile(gps_csv):
        raise FileNotFoundError(f"GPS file not found")

    df = pd.read_csv(gps_csv)

    required_cols = ["time_sec", "time_nsec", "lon", "lat"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"gps_pose.csv Missing column: {col}")

    t = df["time_sec"].to_numpy(dtype=float) + df["time_nsec"].to_numpy(dtype=float) * 1e-9

    lon = df["lon"].to_numpy(dtype=float)
    lat = df["lat"].to_numpy(dtype=float)

    x, y = gps_lonlat_to_local_xy(lon, lat)
    gps_xy = np.column_stack((x, y))

    valid = np.isfinite(t) & np.isfinite(gps_xy[:, 0]) & np.isfinite(gps_xy[:, 1])
    t = t[valid]
    gps_xy = gps_xy[valid]

    order = np.argsort(t)
    t = t[order]
    gps_xy = gps_xy[order]

    return t, gps_xy


def read_aet_txt(aet_txt):
    if not os.path.isfile(aet_txt):
        raise FileNotFoundError(f"Unable to find LIO file")

    data = np.loadtxt(aet_txt)

    if data.ndim == 1:
        data = data.reshape(1, -1)

    if data.shape[1] < 4:
        raise ValueError("At least 4 columns are required: t p.x p.y p.z")

    t = data[:, 0].astype(float)
    x = data[:, 1].astype(float)
    y = data[:, 2].astype(float)

    aet_xy = np.column_stack((x, y))

    valid = np.isfinite(t) & np.isfinite(aet_xy[:, 0]) & np.isfinite(aet_xy[:, 1])
    t = t[valid]
    aet_xy = aet_xy[valid]

    order = np.argsort(t)
    t = t[order]
    aet_xy = aet_xy[order]

    return t, aet_xy


def interpolate_xy(t_src, xy_src, t_query):
    xq = np.interp(t_query, t_src, xy_src[:, 0])
    yq = np.interp(t_query, t_src, xy_src[:, 1])
    return np.column_stack((xq, yq))


def estimate_rigid_2d(src, dst):
    """
    rigid body transformation：
        dst ≈ src @ R.T + t
    """
    src = np.asarray(src, dtype=float)
    dst = np.asarray(dst, dtype=float)

    src_mean = np.mean(src, axis=0)
    dst_mean = np.mean(dst, axis=0)

    src_centered = src - src_mean
    dst_centered = dst - dst_mean

    H = src_centered.T @ dst_centered
    U, _, Vt = np.linalg.svd(H)

    R = Vt.T @ U.T

    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T

    t = dst_mean - src_mean @ R.T

    return R, t


def apply_rigid_2d(src, R, t):
    return src @ R.T + t


def compute_metrics_2d(est_xy, ref_xy):
    err = np.linalg.norm(est_xy - ref_xy, axis=1)

    rmse = np.sqrt(np.mean(err ** 2))
    mean = np.mean(err)
    max_err = np.max(err)
    min_err = np.min(err)
    epe = np.linalg.norm(est_xy[-1] - ref_xy[-1])

    return {
        "RMSE": rmse,
        "Mean": mean,
        "Max": max_err,
        "Min": min_err,
        "EPE": epe,
        "Errors": err
    }


def main():
    print("========== Read data ==========")

    gps_t, gps_xy = read_gps_pose_csv(GPS_CSV)
    aet_t, aet_xy = read_aet_txt(AET_TXT)

    print(f"GPS points number: {len(gps_t)}")
    print(f"LIO points number: {len(aet_t)}")

    print(f"GPS time range: {gps_t[0]:.9f} to {gps_t[-1]:.9f}")
    print(f"LIO time range: {aet_t[0]:.9f} to {aet_t[-1]:.9f}")

    t_start = max(gps_t[0], aet_t[0])
    t_end = min(gps_t[-1], aet_t[-1])

    if t_end <= t_start:
        raise RuntimeError(
            "GPS and LIO do not have overlapping time periods, please check if the timestamps are consistent. \n"
            f"GPS: {gps_t[0]:.9f} to {gps_t[-1]:.9f}\n"
            f"AET: {aet_t[0]:.9f} to {aet_t[-1]:.9f}"
        )

    mask_gps = (gps_t >= t_start) & (gps_t <= t_end)
    t_common = gps_t[mask_gps]
    gps_xy_common = gps_xy[mask_gps]

    aet_xy_interp = interpolate_xy(aet_t, aet_xy, t_common)

    print(f"Common time period: {t_start:.9f} to {t_end:.9f}")
    print(f"Points used for evaluation: {len(t_common)}")

    if DO_RIGID_ALIGN_2D:
        R, trans = estimate_rigid_2d(aet_xy_interp, gps_xy_common)
        aet_xy_aligned = apply_rigid_2d(aet_xy_interp, R, trans)
        print("rigid body global alignment has been performed.")
    else:
        aet_xy_aligned = aet_xy_interp.copy()
        print("rigid body global alignment has not been performed yet.")

    if FORCE_START_ALIGN:
        delta = gps_xy_common[0] - aet_xy_aligned[0]
        aet_xy_aligned = aet_xy_aligned + delta
        

    metrics = compute_metrics_2d(aet_xy_aligned, gps_xy_common)

    print("\n========== error metric ==========")
    print(f"RMSE : {metrics['RMSE']:.6f} m")
    print(f"Mean : {metrics['Mean']:.6f} m")
    print(f"Max  : {metrics['Max']:.6f} m")
    print(f"Min  : {metrics['Min']:.6f} m")
    print(f"EPE  : {metrics['EPE']:.6f} m")

    result_df = pd.DataFrame([{
        "Method": "LIO",
        "RMSE_m": metrics["RMSE"],
        "Mean_m": metrics["Mean"],
        "Max_m": metrics["Max"],
        "Min_m": metrics["Min"],
        "EPE_m": metrics["EPE"],
        "Num_Points": len(t_common),
        "Time_Start": t_start,
        "Time_End": t_end
    }])

    result_df.to_csv(OUTPUT_METRICS_CSV, index=False)
    print(f"\n The error indicator has been saved to: {OUTPUT_METRICS_CSV}")

    plt.figure(figsize=(9, 7))

    plt.plot(
        gps_xy_common[:, 0],
        gps_xy_common[:, 1],
        "k-",
        linewidth=2.0,
        label="GPS"
    )

    plt.plot(
        aet_xy_aligned[:, 0],
        aet_xy_aligned[:, 1],
        "r-",
        linewidth=1.8,
        label="LIO aligned"
    )

    plt.scatter(
        gps_xy_common[0, 0],
        gps_xy_common[0, 1],
        c="green",
        s=80,
        marker="o",
        label="Start"
    )

    plt.scatter(
        gps_xy_common[-1, 0],
        gps_xy_common[-1, 1],
        c="blue",
        s=80,
        marker="x",
        label="GPS End"
    )

    plt.scatter(
        aet_xy_aligned[-1, 0],
        aet_xy_aligned[-1, 1],
        c="red",
        s=80,
        marker="x",
        label="LIO End"
    )

    plt.axis("equal")
    plt.grid(True)
    plt.xlabel("X / m")
    plt.ylabel("Y / m")
    plt.title("2D Trajectory Comparison: GPS vs LIO")
    plt.legend()
    plt.tight_layout()

    plt.savefig(OUTPUT_FIG, dpi=300)
    print(f"The trajectory map has been saved to: {OUTPUT_FIG}")

    if SHOW_FIGURE:
        plt.show()


if __name__ == "__main__":
    main()
