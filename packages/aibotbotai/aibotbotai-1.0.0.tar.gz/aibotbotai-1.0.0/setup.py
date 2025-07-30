from setuptools import setup, find_packages

setup(
    name='aibotbotai',
    version='1.0.0',
    author='Ahmed Helmy Ali Eletr',
    author_email='ahmedhelmy.stem@gmail.com',
    description='The official Python library for the MindBot API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AhmedHelmy-STEM',
    packages=find_packages(),
    install_requires=[
        'google-generativeai',
        'Flask',
        'pandas',
        'Pillow',
        'requests',
        'fpdf',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
