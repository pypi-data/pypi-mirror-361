from setuptools import setup, find_packages

setup(
    name="vasbotlauncher",
    version="0.1.0",
    description="A Discord bot launcher written in Python.",
    long_description="A launcher that dynamically pulls and runs the latest Discord bot release.",
    long_description_content_type="text/plain",
    author="DEAMJAVA",
    author_email="deamminecraft3@gmail.com",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires="==3.12.*",
    entry_points={
        "console_scripts": [
            "vasbot=vasbotlauncher:launch",
        ],
    },
)
