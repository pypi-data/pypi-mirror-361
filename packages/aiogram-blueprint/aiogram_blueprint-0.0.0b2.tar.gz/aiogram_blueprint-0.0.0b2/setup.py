from setuptools import setup, find_packages

setup(
    name="aiogram-blueprint",
    version="0.0.0b2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "Jinja2",
        "InquirerPy",
    ],
    entry_points={
        "console_scripts": [
            "aiogram-blueprint=aiogram_blueprint.cli:cli",
        ],
    },
    package_data={
        "aiogram_blueprint": ["template/**/*"],
    },
)
