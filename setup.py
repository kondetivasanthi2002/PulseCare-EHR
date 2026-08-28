from setuptools import setup, find_packages

setup(
    name="pulsecare-ehr",
    version="2.4.0",
    description="Enterprise Healthcare Management System",
    author="PulseCare Team",
    license="Proprietary",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Medical Science Apps"
    ],
    packages=find_packages(),
    py_modules=["main", "run", "server", "manage"],
    entry_points={
        "console_scripts": [
            "pulsecare=manage:main",
            "pulsecare-server=main:main"
        ],
    },
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.23"
    ]
)
