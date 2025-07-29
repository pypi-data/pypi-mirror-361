from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name='console-animation',
    version='0.1.3',
    description='An easy to use decorator to show a console spinner during function execution.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Koushik',
    author_email='koushikla115@gmail.com',
    url='https://github.com/KoushikEng/console-animation',
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
