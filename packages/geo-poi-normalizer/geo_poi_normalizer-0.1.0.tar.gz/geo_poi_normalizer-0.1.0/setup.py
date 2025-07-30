"""
GeoPOINormalizer库的安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geo-poi-normalizer",
    version="0.1.0",
    author="Tencent Cloud",
    author_email="example@example.com",
    description="地理POI归一化处理库，采用投影转换+各向同性缩放方案",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/geo-poi-normalizer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.18.0",
        "pyproj>=2.6.0",
        "pyshp>=2.1.0",
    ],
    keywords="gis, normalization, poi, geospatial, coordinates, projection, utm",
)