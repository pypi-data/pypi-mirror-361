# GeoPOINormalizer：地理POI归一化库

GeoPOINormalizer是一个专业的Python库，用于地理位置POI(兴趣点)数据的科学归一化处理。它采用投影转换+各向同性缩放方案，解决了地理数据直接归一化导致的空间关系失真问题。

## 核心特性

- **保持距离比例**：通过UTM投影和各向同性缩放，确保归一化后的POI点保持原始空间关系
- **双向转换**：支持坐标和距离的归一化与反归一化，确保数据可逆性
- **灵活输出**：支持[0,1]和[-1,1]两种标准化输出范围
- **GIS集成**：直接从Shapefile读取地理数据
- **详细报告**：生成归一化过程的详细分析报告

## 安装

```bash
pip install geo-poi-normalizer
```

### 依赖项

- Python >= 3.6
- numpy >= 1.18.0
- pyproj >= 2.6.0
- pyshp >= 2.1.0

## 基本用法

```python
from geo_poi_normalizer import GeoPOINormalizer

# 创建归一化器，输出范围设为[-1, 1]
normalizer = GeoPOINormalizer(output_range=(-1, 1))

# 添加POI点
points = [
    (116.4074, 39.9042),  # 北京
    (121.4737, 31.2304),  # 上海
    (113.2644, 23.1291),  # 广州
    (114.0579, 22.5431)   # 深圳
]
normalizer.add_points(points)

# 计算归一化参数
normalizer.compute_projection()
normalizer.compute_normalization_params()

# 归一化所有点
normalized_points = normalizer.normalize_points()
print("归一化后的点:")
for point in normalized_points:
    print(f"({point[0]:.4f}, {point[1]:.4f})")

# 反归一化示例
original_point = normalizer.denormalize_point(normalized_points[0][0], normalized_points[0][1])
print("\n反归一化第一个点:", original_point)

# 打印报告
normalizer.print_report()
```

## 高级功能

### 从Shapefile加载数据

```python
# 创建归一化器，输出范围设为[0, 1]
normalizer = GeoPOINormalizer(output_range=(0, 1))

# 从shapefile加载POI
normalizer.load_from_shapefile("poi_data.shp", lat_field="latitude", lon_field="longitude")

# 计算并应用归一化
normalizer.compute_projection()
normalized_points = normalizer.normalize_points()
```

### 距离归一化

```python
# 归一化距离
distance_km = 100  # 100公里
normalized_dist = normalizer.normalize_distance(distance_km * 1000)
print(f"100公里归一化距离: {normalized_dist:.6f}")

# 反归一化距离
original_dist = normalizer.denormalize_distance(normalized_dist) / 1000
print(f"反归一化距离: {original_dist:.2f}公里")
```

## API参考

### GeoPOINormalizer类

```python
GeoPOINormalizer(output_range=(0, 1))
```

**参数**:
- `output_range`: 输出范围，支持(0,1)或(-1,1)

**主要方法**:

- `add_point(lon, lat, *attributes)`: 添加单个POI点
- `add_points(points)`: 批量添加POI点
- `load_from_shapefile(shp_path, lat_field=None, lon_field=None)`: 从shapefile加载POI点
- `compute_projection(ref_lon=None, ref_lat=None)`: 计算最优投影参数
- `compute_normalization_params()`: 计算归一化参数
- `normalize_points()`: 归一化所有点
- `normalize_point(lon, lat)`: 归一化单个点
- `denormalize_point(x_norm, y_norm)`: 反归一化单个点
- `normalize_distance(distance_meters)`: 归一化距离(米)
- `denormalize_distance(norm_distance)`: 反归一化距离
- `get_normalization_report()`: 获取归一化报告
- `print_report()`: 打印归一化报告

## 技术原理

### 1. 投影转换
使用UTM投影将经纬度$(λ, φ)$转换为平面坐标$(x, y)$：
$$(x, y) = \text{UTM}(λ, φ)$$

### 2. 各向同性归一化
计算缩放因子：
$$s = \max(x_{\max} - x_{\min}, y_{\max} - y_{\min})$$

归一化坐标：
$$x_{\text{norm}} = \frac{x - x_{\min}}{s}$$
$$y_{\text{norm}} = \frac{y - y_{\min}}{s}$$

### 3. 输出范围调整
对于[-1, 1]范围：
$$x_{\text{final}} = 2x_{\text{norm}} - 1$$
$$y_{\text{final}} = 2y_{\text{norm}} - 1$$

## 应用场景

- **强化学习环境**：为地理位置状态表示提供标准化输入
- **空间数据分析**：保持空间关系的数据预处理
- **地理特征工程**：为机器学习模型准备地理特征
- **位置敏感的AI模型**：提供空间感知的标准化输入

## 为什么需要GeoPOINormalizer？

直接将经纬度归一化会导致以下问题：

1. **距离失真**：经纬度直接归一化会导致不同方向的距离比例失真
2. **形状扭曲**：长宽比例失衡的区域会被严重扭曲
3. **精度不均**：不同纬度的经度精度不同

GeoPOINormalizer通过UTM投影和各向同性缩放解决了这些问题，确保：

1. **距离比例保持**：各个方向的距离比例关系保持一致
2. **形状保持**：区域的几何形状基本保持不变
3. **高精度**：在300km范围内提供高精度的距离计算

## 许可证

MIT