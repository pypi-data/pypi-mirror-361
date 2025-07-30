from setuptools import setup, find_packages

setup(
    name="Web_Vulnscanner",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
      "playwright>=1.42.0",
      "httpx>=0.27.0",
      "requests>=2.31.0",
      "h2>=4.1.0",
      "rich>=13.0.0",
    ],
    author="Randomguy",
    author_email="gawzenneth@gmail.com",
    description="A Simple CLI python tool to scan a website for various common vulnerabilities.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/randomguy6407/Vulnscanner",
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'web_vulnscanner=vulnscanner.main:main',  # if you want a CLI command
        ],
    },
)
