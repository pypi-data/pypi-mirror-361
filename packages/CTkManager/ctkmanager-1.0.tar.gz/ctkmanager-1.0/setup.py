from setuptools import setup, find_packages

setup(
    name='CTkManager',
    version='1.0',
    author='McDjXdLol',
    description='CTkManager is a helper library designed to streamline CustomTkinter GUI development. It integrates PIL for image support and uses Enum to keep configuration clean and easy.',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'customtkinter',
        'Pillow'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
