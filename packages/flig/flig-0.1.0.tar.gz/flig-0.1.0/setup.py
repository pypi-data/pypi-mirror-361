from setuptools import setup, find_packages

setup(
    name="flig",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'torch>=2.0.0',
        'numpy>=1.21.0',
        'captum>=0.6.0'
    ],
    author="Paul Gräve",
    description="Frequency-domain model analysis package",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://gitlab.com/paulabraham.graeve/flex",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",
    license_files=["LICENSE", "CITATION.cff"],
    extras_require={
        'academic': ['howfairis>=0.20.0']
    }
)