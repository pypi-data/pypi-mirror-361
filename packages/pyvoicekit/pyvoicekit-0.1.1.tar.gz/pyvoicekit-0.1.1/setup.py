from setuptools import setup, find_packages

setup(
    name="pyvoicekit",
    version="0.1.1",
    author="Yash Kumar Firoziya",
    description="Simple Python package for text-to-speech and speech-to-text",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/firoziya/pyvoicekit",
    packages=find_packages(),
    install_requires=[
        "pyttsx3",
        "SpeechRecognition",
        "pyaudio"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)