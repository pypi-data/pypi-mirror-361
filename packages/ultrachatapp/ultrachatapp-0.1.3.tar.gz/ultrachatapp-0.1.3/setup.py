
from setuptools import setup, find_packages
from pathlib import Path

# Read README.md safely
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='ultrachatapp',
    version='0.1.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "cryptography",
        "pymongo",
        "sqlalchemy",
        "boto3",
        "python-dotenv",
        "python-multipart",
        "rapidfuzz",
        "requests",
    ],
    entry_points={
        'console_scripts': [
            'ultrachat=ultrachatapp.main:main',
        ],
    },
    author='ultraxpert',
    author_email='ultraxpertoffice@gmail.com',
    description='UltraXpert Chat App',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/UltraCreation-IT-Solution/UltraXpertChatApp.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
