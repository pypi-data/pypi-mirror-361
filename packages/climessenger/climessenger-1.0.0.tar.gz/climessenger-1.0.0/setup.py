from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='climessenger',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'Flask>=2.0.0',
        'requests>=2.25.0',
        'cryptography>=41.0.0'
    ],
    python_requires='>=3.8',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'climessenger=climessenger.app:main',
        ],
    },

    author='RUIS',
    author_email='ruslan@ruisvip.ru',
    description='Exchange text messages directly in the terminal. Fast, minimalistic, and secure',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Ruslan-Isaev/climessenger',
    project_urls={
        'GitHub': 'https://github.com/Ruslan-Isaev/climessenger',
        'Bug Tracker': 'https://github.com/Ruslan-Isaev/climessenger/issues',
    },
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
)

