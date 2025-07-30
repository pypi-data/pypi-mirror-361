import os
import subprocess
import shutil
import stat
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from setuptools.command.develop import develop

class CMakeBuild(build_py):
    def run(self):
        # Check cmake version first
        try:
            cmake_output = subprocess.check_output(['cmake', '--version']).decode()
            version_line = cmake_output.split('\n')[0]
            version_str = version_line.split('version')[1].strip()
            major, minor, patch = map(int, version_str.split('.')[:3])
            if (major, minor, patch) < (3, 22, 1):
                raise RuntimeError("CMake >= 3.22.1 is required.")
        except Exception as e:
            raise RuntimeError(f"CMake check failed: {e}")

        build_temp = os.path.join(self.build_lib, "build_temp")
        os.makedirs(build_temp, exist_ok=True)

        self.announce("Configuring CMake project", level=3)
        subprocess.check_call([
            "cmake",
            "-S", ".",
            "-B", build_temp,
            "-DCMAKE_BUILD_TYPE=Release",
            f"-DCMAKE_INSTALL_PREFIX={os.path.abspath(build_temp)}"
        ])

        self.announce("Building project", level=3)
        subprocess.check_call(["cmake", "--build", build_temp, "--config", "Release"])

        self.announce("Installing project", level=3)
        subprocess.check_call(["cmake", "--install", build_temp])

        # Move executable to package bin
        target_dir = os.path.join(self.build_lib, "codeseg", "bin")
        os.makedirs(target_dir, exist_ok=True)
        exe_name = "CoDeSEG"
        if os.name == "nt":
            exe_name += ".exe"

        built_exe = os.path.join(build_temp, "bin", exe_name)
        dst_exe = os.path.join(target_dir, exe_name)

        shutil.copyfile(built_exe, dst_exe)

        # Set executable permission
        st = os.stat(dst_exe)
        os.chmod(dst_exe, st.st_mode | stat.S_IEXEC)
        self.announce(f"Executable copied and permission set: {dst_exe}", level=3)

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
    version="1.0.2",
    author="Pu Li",
    author_email="lipu2024626@gmail.com",
    description="CoDeSEG Community Detection Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kust-lp/CoDeSEG",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    package_data={"codeseg": ["bin/CoDeSEG", "bin/CoDeSEG.exe"]},
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
