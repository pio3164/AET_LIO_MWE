# AET_LIO_MWE
DEMO
# Environment
* **ROS**: Noetic
* **Ceres Solver**: 1.14.0
* **PCL (Point Cloud Library)**: 1.10.0
* **GTSAM**: 4.1.1
* **Livox ROS Driver & SDK**:
  * [Livox-SDK](https://github.com/Livox-SDK/Livox-SDK)
  * [livox_ros_driver](https://github.com/Livox-SDK/livox_ros_driver)

---

# Configuration & Data Paths
* **Parameter Configuration**: The configuration file `lslidar.yaml` is located at:
  `AET_LIO_MWE/src/AET-LIO/config/`
* **RTK Ground Truth**: The RTK trajectory data `rtk_data.csv` is located at:
  `AET_LIO_MWE/rtk/`

---

# Installation and Running

### 1. Build and Launch the LIO Node
Open a terminal and run:
```bash
cd AET_LIO_MWE
catkin_make
source devel/setup.bash
roslaunch aet_lio mapping_lslidar.launch

### 2. Download Sample Dataset
Please download the sample rosbag from [https://drive.google.com/file/d/1_JyrWb9awo0ONVJPZBl7bzVyxb0ugbp9/view?usp=sharing] and place it in the `AET_LIO_MWE/sample_bag` directory.

### 3. Save the LIO Trajectory
Open a new terminal to record the trajectory:
cd AET_LIO_MWE/rtk
# Saves the LIO trajectory as 'odometry_trajectory.txt' in the current directory
python3 save_path.py

### 4. Play the Rosbag
Open another terminal to play the sample bag:
cd AET_LIO_MWE/sample_bag
rosbag play sample.bag

### 5. Evaluation (After the bag finishes)
Once the bag playback is complete, open a new terminal to calculate errors and plot the trajectory:
cd AET_LIO_MWE/rtk
# Calculates error metrics and generates the trajectory comparison plot
python3 compare_gps_lio.py

