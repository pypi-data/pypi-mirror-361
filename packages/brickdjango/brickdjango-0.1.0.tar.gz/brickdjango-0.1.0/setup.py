from setuptools import setup, find_packages

setup(
    name='brickdjango',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'brickdjango = django_custom_structure.__main__:main',
        ]
    },
    author='Amol Balpande',
    author_email='amolbalpande2020@gmail.com',
    description='A clean, modular Django project structure with environment and Docker support.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
)
