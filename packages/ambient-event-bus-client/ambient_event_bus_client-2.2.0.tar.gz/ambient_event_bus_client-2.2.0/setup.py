from setuptools import setup, find_packages

NAME = "ambient_event_bus_client"
VERSION = "2.2.0"

setup(
    name=NAME,
    version=VERSION,
    description="A library to interact with the Ambient Labs Event Bus.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Jose Catarino",
    author_email="jose@ambientlabscomputing.com",
    url="https://github.com/ambientlabscomputing/ambient-event-bus-client",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
