import setuptools

setuptools.setup(
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": ["statistically = statistically.statistically:main"]
    },
    setup_requires=["twine"],
)
