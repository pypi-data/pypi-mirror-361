import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from setuptools.command.develop import develop
import shutil
import stat

class CMakeBuild(build_py):
    def initialize_options(self):
        super().initialize_options()
        self.build_temp = None  

    def finalize_options(self):
        super().finalize_options()
        if self.build_temp is None:
            self.build_temp = os.path.join(self.build_lib, "build_temp")
        os.makedirs(self.build_temp, exist_ok=True)

    def run(self):
        os.makedirs(self.build_temp, exist_ok=True)
        os.makedirs(self.build_lib, exist_ok=True)

        config = "Release"
        cmake_cmd = [
            "cmake",
            "-S", ".",
            "-B", self.build_temp,
            f"-DCMAKE_BUILD_TYPE={config}",
            f"-DCMAKE_INSTALL_PREFIX={os.path.abspath(self.build_temp)}"
        ]

        self.announce("Configuring CMake project", level=3)
        subprocess.check_call(cmake_cmd)

        self.announce("Building C++ executable", level=3)
        build_cmd = ["cmake", "--build", self.build_temp, "--config", config]
        subprocess.check_call(build_cmd)

        self.announce("Installing executable", level=3)
        install_cmd = [
            "cmake", "--install", self.build_temp,
            "--prefix", os.path.abspath(self.build_temp)
        ]
        subprocess.check_call(install_cmd)

        target_dir = os.path.join(self.build_lib, "codeseg", "bin")
        os.makedirs(target_dir, exist_ok=True)

        exe_name = "CoDeSEG"
        if os.name == "nt":
            exe_name += ".exe"
        src_exe_path = os.path.join(self.build_temp, "bin", exe_name)
        dst_exe_path = os.path.join(target_dir, exe_name)

        self.announce(f"Copying executable {src_exe_path} to {dst_exe_path}", level=3)
        shutil.copyfile(src_exe_path, dst_exe_path)

        if os.path.exists(dst_exe_path):
            st = os.stat(dst_exe_path)
            os.chmod(dst_exe_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            self.announce(f"Set executable permission for {dst_exe_path}", level=3)
        else:
            self.announce(f"Executable {dst_exe_path} not found, cannot set permission", level=3)

        super().run()


class CustomInstall(install):
    def run(self):
        self.run_command('build_py')
        super().run()

class CustomDevelop(develop):
    def run(self):
        self.run_command('build_py')
        super().run()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codeseg",
    version="1.0.0",
    author="Pu Li",
    author_email="lipu2024626@gmail.com",
    description="CoDeSEG Community Detection Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kust-lp/CoDeSEG",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    package_data={
        "codeseg": ["bin/CoDeSEG", "bin/CoDeSEG.exe"],  
    },
    include_package_data=True,
    cmdclass={
        'build_py': CMakeBuild,
        'install': CustomInstall,
        'develop': CustomDevelop,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    python_requires=">=3.8",
    keywords="community detection, graph clustering",
    zip_safe=False,
)
