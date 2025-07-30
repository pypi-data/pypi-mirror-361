from setuptools import setup, find_packages

setup(
    name='pyops-cli',
    version='1.0.0',
    description='PyOps CLI Toolkit: System Monitoring, Git Automation, Linux Commands, API Tools',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Rohan Jadhav',
    author_email='youremail@example.com',
    url='https://github.com/yourusername/pyops-cli',  # Replace this!
    packages=find_packages(),
    install_requires=[
        'psutil',
        'gitpython',
        'requests',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'pyops=pyops.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)