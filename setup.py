from setuptools import setup, find_packages

setup(
    name='image-viewer',
    version='0.1.0',
    description='A web application to display images from a specified directory while maintaining the directory structure.',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-RESTful',
        'Pillow',
    ],
    entry_points={
        'console_scripts': [
            'image-viewer=image_viewer.cli:main',
        ],
    },
)