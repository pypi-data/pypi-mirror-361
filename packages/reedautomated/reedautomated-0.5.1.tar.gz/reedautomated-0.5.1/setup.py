from setuptools import setup, find_packages

setup(
    name="reedautomated",
    version="0.5.1",  
     packages=find_packages(include=['reedautomated', 'reedautomated.*']),
     install_requires=[
        "selenium",
        "schedule",
        "chromedriver"
    ],
)
