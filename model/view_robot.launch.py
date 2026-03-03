import os
from launch import LaunchDescription
from launch_ros.actions import Node

URDF_PATH = os.path.join(os.path.dirname(__file__), 'kurokun.urdf')

def generate_launch_description():
    with open(URDF_PATH, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.join(os.path.dirname(__file__), 'kurokun.rviz')]
                if os.path.exists(os.path.join(os.path.dirname(__file__), 'kurokun.rviz'))
                else [],
        ),
    ])
