from setuptools import find_packages, setup

setup(
    name="measureit2",
    packages= find_packages(include=["measureit2"]), 
    version="0.1.0",
    description="4 Naive native python ways to compute dot product are currently supported. Benchmarking TBA soon.",
    author="Dhananjayan Sudhakar",
    author_email="vvandhiyadhevan@gmail.com",
    install_requires= [],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)