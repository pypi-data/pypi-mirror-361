from setuptools import setup, find_packages

setup(
    name="vasbotlauncher",
    version="0.2.0",
    description="Launcher A Discord bot written in Python.",
    long_description="A Discord bot launcher written in Python.",
    long_description_content_type="text/plain",
    author="DEAMJAVA",
    author_email="deamminecraft3@gmail.com",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "vasbot=vasbotlauncher:launch",
        ],
    },
)
