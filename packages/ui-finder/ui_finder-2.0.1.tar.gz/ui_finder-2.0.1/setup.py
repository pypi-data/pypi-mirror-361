from setuptools import setup, find_packages
import pathlib


module_name = "ui_finder" # Change this to your module name
# Read version from __version__.py
version_ns = {}
exec((pathlib.Path(f"{module_name}") / "__version__.py").read_text(), version_ns)
version = version_ns["__version__"]

# Load README.md for PyPI
this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    license="MIT",
    name=module_name,
    version=version,
    description="Android UI elements inspector for automating UI testing and development.",
    keywords="android, ui, inspector, automation, testing, development, adb",
    author="Kuldeep Singh",
    author_email="kdiitg@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/kdiitg/{module_name}",
    project_urls={
        "Documentation": "https://github.com/kdiitg/{module_name}",
        "Source": "https://github.com/kdiitg/{module_name}",
        "Bug Tracker": "https://github.com/kdiitg/{module_name}/issues"
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Pillow~=11.2.1",
        "qrcode~=8.2",
        "requests~=2.32.4",
    ],
    entry_points={
        'console_scripts': [
            f'{module_name}={module_name}.main:main',
            f'android_inspector={module_name}.main:main',
            f'uif={module_name}.main:main',
            f'adr={module_name}.main:main',

        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: File Transfer Protocol (FTP)",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
)
