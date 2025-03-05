from setuptools import find_packages, setup
import os, glob

package_name = 'pinky_emotion'

data_files = [
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    ('share/' + package_name + '/emotion', glob.glob(os.path.join('emotion', '*.gif'))),
]

emotion_dir = 'emotion'
for root, dirs, files in os.walk(emotion_dir):
    if files:
        rel_dir = os.path.relpath(root, emotion_dir)
        install_dir = os.path.join('share', package_name, emotion_dir)
        if rel_dir != '.':
            install_dir = os.path.join(install_dir, rel_dir)
        file_paths = [os.path.join(root, f) for f in files]
        data_files.append((install_dir, file_paths))


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pinklab',
    maintainer_email='kyung133851@pinklab.art',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "pinky_emotion=pinky_emotion.pinky_emotion:main",
            "pinky_emotion_topic=pinky_emotion.pinky_emotion_topic:main",
        ],
    },
)