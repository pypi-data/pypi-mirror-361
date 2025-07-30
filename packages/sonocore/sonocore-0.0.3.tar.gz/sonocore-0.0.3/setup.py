from setuptools import setup, find_packages

setup(
    name="sonocore",
    version="0.0.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "aiohttp>=3.8.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful and advanced Lavalink client for Python with Lavasrc support.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/your_username/sonocore",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    python_requires='>=3.8',
)
