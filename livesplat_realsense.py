"""
After installing LiveSplat, connect your Realsense devices and run this
script to launch the application. 

Important: This script requires pyrealsense2. The Python 3.12+ version
is currently published under the name "pyrealsense2-beta". Get it by 
running `pip install pyrealsense2-beta`.
"""

import numpy as np
import livesplat
import pyrealsense2 as rs # pip install pyrealsense2-beta

def get_device_metadata(desired_width, desired_height, desired_fps):
    """This uses pyrealsense2 to query the connected RealSense
    devices.  For each device, it pulls out the serial number, color
    and depth sensor objects, and color and depth stream profile
    objects matching the desired width, height, and fps. These are
    returned in a list of dict with keys serial_number, color_sensor,
    color_profile, depth_sensor, depth_profile.
    """
    metadata = []

    # Create context and get devices
    context = rs.context()
    devices = context.query_devices()
    for i, dev in enumerate(devices):
        color_profile = None
        depth_profile = None
        color_sensor = None
        depth_sensor = None
        
        serial = dev.get_info(rs.camera_info.serial_number)
        print(f"\nDevice {i}: Serial {serial}")

        for sensor in dev.query_sensors():
            sensor_name = sensor.get_info(rs.camera_info.name)
            for profile in sensor.get_stream_profiles():
                video_profile = profile.as_video_stream_profile()
                stream_type = video_profile.stream_type()

                if (video_profile.width() == desired_width and
                    video_profile.height() == desired_height and
                    video_profile.fps() == desired_fps):

                    if stream_type == rs.stream.color and color_profile is None:
                        color_profile = video_profile
                        color_sensor = sensor
                        print(f"  Found color profile on sensor '{sensor_name}'")

                    elif stream_type == rs.stream.depth and depth_profile is None:
                        depth_profile = video_profile
                        depth_sensor = sensor
                        print(f"  Found depth profile on sensor '{sensor_name}'")

            # Stop early if both profiles found
            if color_profile and depth_profile:
                break

        if color_profile and depth_profile:
            metadata.append({
                "serial_number": serial,
                "color_sensor": color_sensor,
                "color_profile": color_profile,
                "depth_sensor": depth_sensor,
                "depth_profile": depth_profile,
            })
        else:
            print("  Warning: Device is missing color or depth sensor")
            continue
    return metadata

def intrinsics_to_mat3x3(fx, fy, ppx, ppy):
    """Converts from focal params and pixel offset to 3x3 camera matrix"""
    result = np.eye(3)
    result[0,0] = fx
    result[1,1] = fy
    result[0,2] = ppx
    result[1,2] = ppy
    return result
    

def main():
    metadata = get_device_metadata(desired_width=640, desired_height=480, desired_fps=30)

    # create a mapping from profile uid to serial numbers this is used
    # when receiving frames from the frame queue to back out which
    # device the frame is coming from
    profile_uid_to_serial_number = {}
    for datum in metadata:
        serial_number = datum["serial_number"]
        color_profile = datum["color_profile"].as_video_stream_profile()
        depth_profile = datum["depth_profile"].as_video_stream_profile()
        profile_uid_to_serial_number[color_profile.unique_id()] = serial_number
        profile_uid_to_serial_number[depth_profile.unique_id()] = serial_number

    # register all cameras
    for i, datum in enumerate(metadata):
        color_profile = datum["color_profile"].as_video_stream_profile()
        color_intrinsics = color_profile.get_intrinsics()
        depth_profile = datum["depth_profile"].as_video_stream_profile()
        depth_intrinsics = depth_profile.get_intrinsics()
        depth_scale = datum["depth_sensor"].get_option(rs.option.depth_units)
        serial_number = datum["serial_number"]

        pose_rgb_depth = depth_profile.get_extrinsics_to(color_profile)
        tx_rgb_depth = np.eye(4)
        tx_rgb_depth[:3, :3] = np.reshape(pose_rgb_depth.rotation, (3, 3))
        tx_rgb_depth[:3, -1] = pose_rgb_depth.translation

        depth_width = depth_intrinsics.width
        depth_height = depth_intrinsics.height
        rgb_width = color_intrinsics.width
        rgb_height = color_intrinsics.height
        
        hm_depthimage_depth = intrinsics_to_mat3x3(
            depth_intrinsics.fx,
            depth_intrinsics.fy,
            depth_intrinsics.ppx,
            depth_intrinsics.ppy)

        hm_rgbimage_rgb = intrinsics_to_mat3x3(
            color_intrinsics.fx,
            color_intrinsics.fy,
            color_intrinsics.ppx,
            color_intrinsics.ppy)

        livesplat.register_camera_params(
            device_id = serial_number,
            rgb_width = rgb_width,
            rgb_height = rgb_height,
            depth_width = depth_width,
            depth_height = depth_height,
            hm_rgbimage_rgb = hm_rgbimage_rgb,
            hm_depthimage_depth = hm_depthimage_depth,
            tx_rgb_depth = tx_rgb_depth,
            depth_scale = depth_scale,
        )

    # start all cameras
    frame_queue = rs.frame_queue(10)
    for i, datum in enumerate(metadata):
        color_profile = datum["color_profile"].as_video_stream_profile()
        depth_profile = datum["depth_profile"].as_video_stream_profile()
        color_sensor = datum["color_sensor"]
        depth_sensor = datum["depth_sensor"]
        color_sensor.open(color_profile)
        color_sensor.start(frame_queue)
        depth_sensor.open(depth_profile)
        depth_sensor.start(frame_queue)

    livesplat.start_viewer()
    while not livesplat.should_stop_all():
        frame = frame_queue.poll_for_frame()
        if frame:
            profile = frame.get_profile()
            profile_uid = profile.unique_id()
            serial_number = profile_uid_to_serial_number[profile_uid]
            stream_type = profile.stream_type()
            if stream_type == rs.stream.color:
                data = frame.get_data()            
                livesplat.ingest_rgb(
                    serial_number,
                    data)
            if stream_type == rs.stream.depth:
                data = frame.get_data()
                livesplat.ingest_depth(
                    serial_number,
                    data)

    for datum in metadata:
        color_sensor = datum["color_sensor"]
        depth_sensor = datum["depth_sensor"]
        color_sensor.stop()
        color_sensor.close()
        depth_sensor.stop()
        depth_sensor.close()

if __name__ == '__main__':
    main()
