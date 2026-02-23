from setuptools import setup, find_packages

setup(
    name='chemical-calculations',
    version='1.0.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'PyQt5>=5.15.0',
        'sympy>=1.12',
        'matplotlib>=3.7.0',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'PyMySQL>=1.1.0',
        'pydantic>=2.0.0',
        'pydantic-settings>=2.0.0',
    ],
    extras_require={
        'dev': [
            'black>=23.0.0',
            'isort>=5.12.0',
            'ruff>=0.1.0',
            'mypy>=1.5.0',
            'pytest>=7.4.0',
        ],
    },
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'chem-calc=src.main:main',
        ],
    },
    author='Артём Оленев, Владислав Коровин',
    description='Приложение для расчётов физико-химических процессов в газах',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)