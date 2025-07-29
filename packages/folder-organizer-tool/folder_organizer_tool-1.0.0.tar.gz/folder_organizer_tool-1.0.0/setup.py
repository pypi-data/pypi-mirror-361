from setuptools import setup, find_packages

setup(
    name='folder-organizer-tool',
    author='Qazi Arsalan Shah',
    version='1.0.0',
    description='A CLI tool to organize files based on file type and extension.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    project_urls={
        'Source': 'https://github.com/qazi112',
        'Tracker': 'https://github.com/qazi112',
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'rich>=13.0',
    ],
    entry_points={
        'console_scripts': [
            'folder-organizer=organizer.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
