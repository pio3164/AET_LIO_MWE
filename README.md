# AET_LIO_MWE

A minimal working example for running AET-LIO with ROS Noetic.

This repository provides the configuration, sample data path convention, trajectory saving script, and evaluation tools for testing the LIO pipeline.

---

## Environment

The project was tested with the following environment:

| Dependency | Version |
| --- | --- |
| ROS | Noetic |
| Ceres Solver | 1.14.0 |
| PCL | 1.10.0 |
| GTSAM | 4.1.1 |
| Python | 3.8.10 |

Additional dependencies:

- [Livox-SDK](https://github.com/Livox-SDK/Livox-SDK)
- [livox_ros_driver](https://github.com/Livox-SDK/livox_ros_driver)

---

## Configuration and Data Paths

- Parameter configuration file:

```text
AET_LIO_MWE/src/AET-LIO/config/lslidar.yaml
```

- RTK ground-truth trajectory file:

```text
AET_LIO_MWE/rtk/rtk_data.csv
```

- Recommended rosbag directory:

```text
AET_LIO_MWE/data/
```

- Workspace Directory Structure

```text
AET_LIO_MWE/
├── src/
│   └── AET-LIO/             # This repository (core package)
│       ├── config/          # Parameter configurations (lslidar.yaml)
│       ├── include/         # (Please create this folder)
│       └── ...
├── data/                    # (Please create this folder to store the downloaded rosbag)
│   └── sample.bag
└── rtk/
    ├── rtk_data.csv         # Reference RTK trajectory
    ├── save_path.py         # Script to record LIO trajectory
    └── compare_gps_lio.py   # Script to evaluate and plot results
```

---

## Installation and Running

### 1. Build the Workspace

Clone or download this repository, then create the required directories:

```bash
cd AET_LIO_MWE
mkdir -p src/AET-LIO/include
mkdir -p data
```

Add the livox_ros_driver environment:

```bash
source ws_livox/devel/setup.bash
```

Build the ROS workspace:

```bash
catkin_make
source devel/setup.bash
```

---

### 2. Download the Sample Dataset

Download the sample rosbag from:

[Google Drive Sample Bag](https://drive.google.com/file/d/1_JyrWb9awo0ONVJPZBl7bzVyxb0ugbp9/view?usp=sharing)

Place the downloaded rosbag in:

```text
AET_LIO_MWE/data/
```

For example, the final file path should be:

```text
AET_LIO_MWE/data/sample.bag
```

If the downloaded file has a different name, either rename it to `sample.bag` or modify the `rosbag play` command accordingly.

---

### 3. Launch the LIO Node

Open a terminal and run:

```bash
cd AET_LIO_MWE
source devel/setup.bash
roslaunch aet_lio mapping_lslidar.launch
```

---

### 4. Save the LIO Trajectory

Open a new terminal and run:

```bash
cd AET_LIO_MWE/rtk
python3 save_path.py
```

This script saves the LIO trajectory as:

```text
AET_LIO_MWE/rtk/odometry_trajectory.txt
```

---

### 5. Play the Rosbag

Open another terminal and run:

```bash
cd AET_LIO_MWE/data
rosbag play sample.bag
```

Wait until the rosbag playback finishes.

---

### 6. Evaluate the Trajectory

After the rosbag finishes playing, run:

```bash
cd AET_LIO_MWE/rtk
python3 compare_gps_lio.py
```

This script calculates error metrics and generates the trajectory comparison plot between the RTK ground truth and the LIO result.

---

## Notes

- Make sure `rtk_data.csv` exists before running the evaluation script.
- Make sure `save_path.py` is running while the rosbag is being played.
- If you open a new terminal for ROS-related commands, remember to source the workspace:

```bash
source AET_LIO_MWE/devel/setup.bash
```
