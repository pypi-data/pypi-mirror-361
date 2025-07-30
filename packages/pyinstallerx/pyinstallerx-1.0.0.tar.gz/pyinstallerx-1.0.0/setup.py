from setuptools import setup, find_packages

setup(
    name='pyinstallerx',
    version='1.0.0',
    description='Install, uninstall, and update Python packages programmatically.',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    author='Kiran Soorya.R.S',
    author_email='hemalathakiransoorya2099@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires = ['setuptools'],
    entry_points={"console_scripts": ["pyinstallerx = pyinstallerx:PythonLibInstaller"],},
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent', 
        'License :: OSI Approved :: MIT License',
    ],
    license='MIT',
)
