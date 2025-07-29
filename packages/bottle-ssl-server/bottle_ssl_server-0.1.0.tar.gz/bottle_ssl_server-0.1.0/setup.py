from setuptools import setup, find_packages

setup(
    name='bottle-ssl-server',
    version='0.1.0',
    description='A lightweight SSL-enabled Bottle server with file upload and logging capabilities',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Olawale Momurede Abdulsalam',
    author_email='muredesalam@example.com',
    url='https://github.com/omegadev21/bottle-ssl-server',
    packages=find_packages(),
    install_requires=[
        'bottle>=0.12.18',
        'cheroot>=8.5.2',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'bottle-ssl-server = bottle_ssl_server.server:main',
        ],
    },
)