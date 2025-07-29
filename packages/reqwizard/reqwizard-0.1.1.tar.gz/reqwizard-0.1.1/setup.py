from setuptools import setup, find_packages

def load_config(filename):
    config = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                config[key.strip()] = value.strip()
    return config

config = load_config("config.pri")

setup(
    name=config["name"],
    version=config["version"],
    author=config["author"],
    author_email=config["email"],
    description=config["description"],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url=config["git"],
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "packaging"
    ],
    entry_points={
        'console_scripts': [
            'reqwizard = reqwizard.cli:cli',
        ],
    },
    include_package_data=True,
    python_requires=">=3.10",
)
