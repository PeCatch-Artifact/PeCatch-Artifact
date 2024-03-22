from setuptools import setup, find_packages

setup(
    name="madmax-plugins",
    description="This is an example of detectors and printers to Slither.",
    url="https://github.com/trailofbits/slither-plugins",
    author="Trail of Bits",
    version="0.1",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["slither-analyzer==0.9.1"],
    entry_points={
        "slither_analyzer.plugin": "slither my-plugin=plugin:make_plugin",
    },
)