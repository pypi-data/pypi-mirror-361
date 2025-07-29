from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setup(
    name='CTkManager',
    version='1.0.1',
    author='McDjXdLol',
    author_email='mcdjxdlol@gmail.com',
    description='CTkManager is a helper library designed to streamline CustomTkinter GUI development. It integrates PIL for image support and uses Enum to keep configuration clean and easy.',
    long_description=long_description,
    long_description_content_type='text/markdown',
  
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