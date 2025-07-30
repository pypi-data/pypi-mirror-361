from setuptools import setup, find_packages

setup(
    name='roblox-mcp-server',
    version='1.0.0',
    author='Yuchan Han',
    author_email='serltretu24@gmail.com',
    description='With the help of the AI Client, you can easily search for Roblox games, check your friends’ statuses, and launch games with ease!',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/h053698/roblox-mcp-server',
    packages=find_packages(),
    py_modules=['main', 'credential_manager'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'roblox-mcp-server = main:main',
        ],
    },
    install_requires=[
        'fastmcp',
        'keyring',
        "tk"
    ]
)