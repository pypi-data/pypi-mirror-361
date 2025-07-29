from setuptools import setup, find_packages
import pathlib

# Set your module/package name here
module_name = "android_mirror"

# Read version from __version__.py
version_ns = {}
exec((pathlib.Path(f"{module_name}") / "__version__.py").read_text(), version_ns)
version = version_ns["__version__"]

# Load README.md
this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    license="MIT",
    name=module_name,
    version=version,
    description="A fixed-version Android screen mirroring tool using bundled scrcpy",
    keywords="scrcpy android mirror screen cast cli adb",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kuldeep Singh",
    url=f"https://github.com/kdiitg/{module_name}",
    project_urls={
        "Documentation": f"https://github.com/kdiitg/{module_name}",
        "Source": f"https://github.com/kdiitg/{module_name}",
        "Bug Tracker": f"https://github.com/kdiitg/{module_name}/issues"
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            f'{module_name}={module_name}.__main__:main',
            'adm=android_mirror.__main__:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
)
