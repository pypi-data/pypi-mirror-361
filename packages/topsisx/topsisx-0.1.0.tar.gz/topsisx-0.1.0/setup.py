from setuptools import setup, find_packages

setup(
    name="topsisx",  # Your package name
    version="0.1.0",
    author="Suvit Kumar",
    author_email="suvitkumar03@gmail.com",
    description="An advanced multi-criteria decision-making library (TOPSIS, AHP, etc.) with visualizations and API support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/suvitkumar03/topsisx",  # Replace with your GitHub repo URL
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "plotly",
        "fpdf",
        "fastapi",
        "uvicorn",
        "python-multipart"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "topsisx=topsisx.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
