"""
GeoPOINormalizer：地理POI归一化处理器
采用投影转换+各向同性缩放方案处理地理位置数据
"""

import math
import numpy as np
import shapefile
from pyproj import Proj, Transformer
from typing import List, Tuple, Union, Optional

class GeoPOINormalizer:
    """
    地理POI归一化处理器
    采用投影转换+各向同性缩放方案处理地理位置数据
    
    主要功能:
    - 从多种来源加载POI数据(经纬度列表、shapefile)
    - 自动计算最优投影参数
    - 支持自定义输出范围([0,1]或[-1,1])
    - 归一化和反归一化坐标
    - 归一化和反归一化距离
    - 生成归一化报告
    
    归一化原理:
    1. 将经纬度转换为平面坐标(米)
    2. 计算所有POI的边界框
    3. 使用各向同性缩放(保持距离比例)
    4. 缩放到指定输出范围
    """
    
    def __init__(self, output_range: Tuple[float, float] = (0, 1)):
        """
        初始化归一化器
        
        :param output_range: 输出范围，支持(0,1)或(-1,1)
        """
        self.points = []  # 原始POI列表: [(lon, lat, *attrs), ...]
        self.projected_points = []  # 投影后的POI: [(x, y, *attrs), ...]
        self.normalized_points = []  # 归一化后的POI: [(x_norm, y_norm, *attrs), ...]
        
        self.ref_lon = None  # 参考经度(投影中心)
        self.ref_lat = None  # 参考纬度(投影中心)
        self.projection = None  # 投影方法
        self.transformer_to_proj = None  # 经纬度转投影坐标的转换器
        self.transformer_to_geo = None  # 投影坐标转经纬度的转换器
        
        self.x_min = self.y_min = float('inf')
        self.x_max = self.y_max = float('-inf')
        self.scale = None  # 各向同性缩放因子
        self.output_range = output_range  # 输出范围
        
        # 验证输出范围
        if output_range not in [(0, 1), (-1, 1)]:
            raise ValueError("输出范围必须是(0,1)或(-1,1)")
    
    def add_point(self, lon: float, lat: float, *attributes):
        """
        添加单个POI点
        
        :param lon: 经度
        :param lat: 纬度
        :param attributes: 可选属性数据
        """
        self.points.append((lon, lat) + attributes)
    
    def add_points(self, points: List[Tuple[float, float]]):
        """
        批量添加POI点
        
        :param points: POI列表，格式为[(lon1, lat1), (lon2, lat2), ...]
        """
        for point in points:
            if len(point) < 2:
                raise ValueError("每个点必须包含至少经度和纬度")
            self.add_point(point[0], point[1], *point[2:])
    
    def load_from_shapefile(self, shp_path: str, lat_field: str = None, lon_field: str = None):
        """
        从shapefile加载POI点
        
        :param shp_path: shapefile路径(不带扩展名)
        :param lat_field: 纬度字段名(可选)
        :param lon_field: 经度字段名(可选)
        """
        try:
            sf = shapefile.Reader(shp_path)
        except Exception as e:
            raise IOError(f"无法读取shapefile: {e}")
        
        # 获取所有几何和属性
        shapes = sf.shapes()
        records = sf.records()
        
        for i, shape in enumerate(shapes):
            if shape.shapeType != shapefile.POINT:
                print(f"警告: 忽略非点要素(索引 {i})")
                continue
            
            # 获取点坐标
            lon, lat = shape.points[0]
            
            # 获取属性
            attrs = records[i] if records else ()
            
            # 如果指定了经纬度字段，则覆盖坐标
            if lat_field and lon_field:
                try:
                    lat_idx = sf.fields.index([lat_field, *sf.fields[0]]) - 1
                    lon_idx = sf.fields.index([lon_field, *sf.fields[0]]) - 1
                    lat = float(records[i][lat_idx])
                    lon = float(records[i][lon_idx])
                except (ValueError, IndexError):
                    pass
            
            self.add_point(lon, lat, *attrs)
    
    def compute_projection(self, ref_lon: float = None, ref_lat: float = None):
        """
        计算最优投影参数
        
        :param ref_lon: 手动指定参考经度(可选)
        :param ref_lat: 手动指定参考纬度(可选)
        """
        if not self.points:
            raise ValueError("没有可处理的POI点")
        
        # 确定参考点(投影中心)
        if ref_lon is None or ref_lat is None:
            lons = [p[0] for p in self.points]
            lats = [p[1] for p in self.points]
            self.ref_lon = sum(lons) / len(lons)
            self.ref_lat = sum(lats) / len(lats)
        else:
            self.ref_lon = ref_lon
            self.ref_lat = ref_lat
        
        # 创建UTM投影(自动确定最佳UTM带)
        utm_zone = int((self.ref_lon + 180) / 6) + 1
        hemisphere = 'north' if self.ref_lat >= 0 else 'south'
        
        # 创建投影
        self.projection = Proj(
            proj='utm', 
            zone=utm_zone, 
            ellps='WGS84', 
            datum='WGS84', 
            units='m', 
            preserve_units=True,
            south=(hemisphere == 'south')
        )
        
        # 创建转换器
        self.transformer_to_proj = Transformer.from_proj(
            Proj('epsg:4326'),  # WGS84
            self.projection,
            always_xy=True
        )
        
        self.transformer_to_geo = Transformer.from_proj(
            self.projection,
            Proj('epsg:4326'),  # WGS84
            always_xy=True
        )
    
    def project_points(self):
        """将经纬度投影到平面坐标(米)"""
        if not self.transformer_to_proj:
            self.compute_projection()
        
        self.projected_points = []
        for point in self.points:
            lon, lat = point[0], point[1]
            x, y = self.transformer_to_proj.transform(lon, lat)
            self.projected_points.append((x, y) + point[2:])
    
    def compute_normalization_params(self):
        """计算归一化参数"""
        if not self.projected_points:
            self.project_points()
        
        # 计算边界框
        xs = [p[0] for p in self.projected_points]
        ys = [p[1] for p in self.projected_points]
        
        self.x_min, self.x_max = min(xs), max(xs)
        self.y_min, self.y_max = min(ys), max(ys)
        
        # 计算各向同性缩放因子
        width = self.x_max - self.x_min
        height = self.y_max - self.y_min
        
        # 防止只有一个点时缩放因子为零
        if width == 0 and height == 0:
            # 如果只有一个点，使用默认缩放因子（1公里）
            self.scale = 1000.0
        else:
            self.scale = max(width, height)
    
    def normalize_points(self) -> List[Tuple[float, float]]:
        """
        归一化所有点
        
        :return: 归一化后的点列表
        """
        if self.scale is None:
            self.compute_normalization_params()
        
        self.normalized_points = []
        
        for point in self.projected_points:
            x, y = point[0], point[1]
            
            # 应用各向同性缩放
            x_norm = (x - self.x_min) / self.scale
            y_norm = (y - self.y_min) / self.scale
            
            # 调整输出范围
            if self.output_range == (-1, 1):
                x_norm = x_norm * 2 - 1
                y_norm = y_norm * 2 - 1
            
            self.normalized_points.append((x_norm, y_norm) + point[2:])
        
        return self.normalized_points
    
    def normalize_point(self, lon: float, lat: float) -> Tuple[float, float]:
        """
        归一化单个点
        
        :param lon: 经度
        :param lat: 纬度
        :return: 归一化后的坐标(x, y)
        """
        # 投影点
        x, y = self.transformer_to_proj.transform(lon, lat)
        
        # 归一化
        x_norm = (x - self.x_min) / self.scale
        y_norm = (y - self.y_min) / self.scale
        
        # 调整输出范围
        if self.output_range == (-1, 1):
            x_norm = x_norm * 2 - 1
            y_norm = y_norm * 2 - 1
        
        return x_norm, y_norm
    
    def denormalize_point(self, x_norm: float, y_norm: float) -> Tuple[float, float]:
        """
        反归一化单个点
        
        :param x_norm: 归一化x坐标
        :param y_norm: 归一化y坐标
        :return: 经纬度(lon, lat)
        """
        if self.output_range == (-1, 1):
            # 转换到[0,1]范围
            x_norm = (x_norm + 1) / 2
            y_norm = (y_norm + 1) / 2
        
        # 反归一化到投影坐标
        x = x_norm * self.scale + self.x_min
        y = y_norm * self.scale + self.y_min
        
        # 转换回经纬度
        lon, lat = self.transformer_to_geo.transform(x, y)
        
        return lon, lat
    
    def normalize_distance(self, distance_meters: float) -> float:
        """
        归一化距离(米)
        
        :param distance_meters: 实际距离(米)
        :return: 归一化距离
        """
        return distance_meters / self.scale
    
    def denormalize_distance(self, norm_distance: float) -> float:
        """
        反归一化距离
        
        :param norm_distance: 归一化距离
        :return: 实际距离(米)
        """
        return norm_distance * self.scale
    
    def get_normalization_report(self) -> dict:
        """获取归一化报告"""
        if not self.points:
            return {"status": "no points"}
        
        if not self.projected_points:
            self.project_points()
        
        if not self.scale:
            self.compute_normalization_params()
        
        # 计算实际地理范围
        min_lon = min(p[0] for p in self.points)
        max_lon = max(p[0] for p in self.points)
        min_lat = min(p[1] for p in self.points)
        max_lat = max(p[1] for p in self.points)
        
        # 计算地理中心
        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2
        
        # 计算投影坐标范围
        width = self.x_max - self.x_min
        height = self.y_max - self.y_min
        aspect_ratio = width / height if height != 0 else float('inf')
        
        # 计算归一化后范围
        if self.output_range == (0, 1):
            norm_width = width / self.scale
            norm_height = height / self.scale
        else:  # (-1, 1)
            norm_width = (width / self.scale) * 2
            norm_height = (height / self.scale) * 2
        
        return {
            "point_count": len(self.points),
            "geographic_range": {
                "min_lon": min_lon,
                "max_lon": max_lon,
                "min_lat": min_lat,
                "max_lat": max_lat,
                "center_lon": center_lon,
                "center_lat": center_lat
            },
            "projection": {
                "type": "UTM",
                "zone": int((self.ref_lon + 180) / 6) + 1,
                "hemisphere": 'north' if self.ref_lat >= 0 else 'south',
                "ref_lon": self.ref_lon,
                "ref_lat": self.ref_lat
            },
            "projected_range": {
                "x_min": self.x_min,
                "x_max": self.x_max,
                "y_min": self.y_min,
                "y_max": self.y_max,
                "width_m": width,
                "height_m": height,
                "aspect_ratio": aspect_ratio
            },
            "normalization": {
                "scale_factor": self.scale,
                "output_range": self.output_range,
                "normalized_width": norm_width,
                "normalized_height": norm_height,
                "normalized_aspect_ratio": norm_width / norm_height if norm_height != 0 else float('inf')
            }
        }
    
    def print_report(self):
        """打印归一化报告"""
        report = self.get_normalization_report()
        """打印归一化报告"""
        report = self.get_normalization_report()
        
        if "status" in report:
            print("无可用POI点")
            return
        
        print("\n=== GEO POI 归一化报告 ===")
        print(f"POI数量: {report['point_count']}")
        
        geo = report['geographic_range']
        print(f"\n地理范围:")
        print(f"  经度: {geo['min_lon']:.6f} → {geo['max_lon']:.6f}")
        print(f"  纬度: {geo['min_lat']:.6f} → {geo['max_lat']:.6f}")
        print(f"  中心点: ({geo['center_lon']:.6f}, {geo['center_lat']:.6f})")
        
        proj = report['projection']
        print(f"\n投影参数:")
        print(f"  类型: UTM Zone {proj['zone']} ({proj['hemisphere']})")
        print(f"  参考点: ({proj['ref_lon']:.6f}, {proj['ref_lat']:.6f})")
        
        proj_range = report['projected_range']
        print(f"\n投影坐标范围(米):")
        print(f"  X: {proj_range['x_min']:.2f} → {proj_range['x_max']:.2f} (宽: {proj_range['width_m']:.2f}m)")
        print(f"  Y: {proj_range['y_min']:.2f} → {proj_range['y_max']:.2f} (高: {proj_range['height_m']:.2f}m)")
        print(f"  宽高比: {proj_range['aspect_ratio']:.2f}:1")
        
        norm = report['normalization']
        range_str = f"{norm['output_range'][0]} to {norm['output_range'][1]}"
        print(f"\n归一化参数:")
        print(f"  缩放因子: {norm['scale_factor']:.2f}m")
        print(f"  输出范围: {range_str}")
        print(f"  归一化宽度: {norm['normalized_width']:.6f}")
        print(f"  归一化高度: {norm['normalized_height']:.6f}")
        print(f"  归一化宽高比: {norm['normalized_aspect_ratio']:.6f}:1")
        print("="*30)