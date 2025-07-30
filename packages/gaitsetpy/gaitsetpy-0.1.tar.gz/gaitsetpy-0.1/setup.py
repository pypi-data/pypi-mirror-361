from setuptools import setup, find_packages

setup(
    name='gaitsetpy',
    version='0.1',
    packages=find_packages(include=["gaitsetpy", "gaitsetpy.*"]),
    description="A Python package for gait analysis using sensor data.",
    author="Alohomora Labs",
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'requests',
        'statsmodels',
        'matplotlib',
        'scikit-learn',
        'joblib',
    ],

)