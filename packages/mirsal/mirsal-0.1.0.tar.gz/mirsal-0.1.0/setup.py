from setuptools import setup, find_packages

setup(
    name="mirsal",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "pyngrok",
    ],
    entry_points={
        'console_scripts': [
            'mirsal=mirsal.cli:main',
        ],
    },
    author="Bashar Talafha",
    description="📄 Live log file viewer with ngrok + Flask",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

