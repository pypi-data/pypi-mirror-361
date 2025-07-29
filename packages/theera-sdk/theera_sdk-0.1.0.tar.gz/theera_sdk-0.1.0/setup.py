from setuptools import setup, find_packages

# Load README.md content
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='theera_sdk',
    version='0.1.0',
    description='SDK for sending events to Theera event tracking API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Theera',
    author_email='theera.connect@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 3 - Alpha"
    ],
)
