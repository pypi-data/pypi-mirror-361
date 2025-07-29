from setuptools import setup, find_packages

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tutor-contrib-pok",
    version="18.0.0",
    description="Tutor plugin to integrate POK certificates into Open edX",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Aulasneo",
    author_email="andres@aulasneo.com",
    url="https://github.com/aulasneo/tutor-contrib-pok",
    license="AGPL-3.0-only",
    packages=find_packages(include=['tutorpok*']),
    include_package_data=True,
    install_requires=[
        "tutor>=19.0.0,<20.0.0",
    ],
    entry_points={
        "tutor.plugin.v1": [
            "pok = tutorpok.plugin"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    python_requires=">=3.9",
)
