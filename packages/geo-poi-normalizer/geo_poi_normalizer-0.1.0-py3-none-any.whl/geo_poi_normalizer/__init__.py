"""
GeoPOINormalizer：地理POI归一化库

这个库提供了一种科学的方法来归一化地理POI数据，
采用投影转换+各向同性缩放方案，保持距离比例关系。

主要功能:
- 将经纬度坐标通过投影转换+各向同性缩放进行归一化
- 支持[0,1]和[-1,1]两种输出范围
- 提供坐标和距离的双向归一化/反归一化
- 支持从Shapefile读取地理数据
- 生成详细的归一化分析报告

基本用法:
```python
from geo_poi_normalizer import GeoPOINormalizer

# 创建归一化器
normalizer = GeoPOINormalizer(output_range=(-1, 1))

# 添加POI点
normalizer.add_point(116.4074, 39.9042)  # 北京

# 归一化
normalizer.compute_projection()
normalizer.normalize_points()

# 打印报告
normalizer.print_report()
```
"""

from .normalizer import GeoPOINormalizer

__version__ = '0.1.0'