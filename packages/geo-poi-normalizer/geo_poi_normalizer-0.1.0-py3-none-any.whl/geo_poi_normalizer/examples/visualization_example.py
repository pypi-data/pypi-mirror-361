"""
GeoPOINormalizer可视化分析示例

这个示例展示了如何使用GeoPOINormalizer库进行地理POI数据的可视化分析。
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from geo_poi_normalizer import GeoPOINormalizer


def visualize_poi_data(output_dir="./output"):
    """
    可视化POI数据分析示例
    
    :param output_dir: 输出目录，用于保存生成的图像
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 准备示例数据：中国主要城市
    cities = [
        (116.4074, 39.9042, "北京", "首都"),
        (121.4737, 31.2304, "上海", "直辖市"),
        (113.2644, 23.1291, "广州", "省会"),
        (114.0579, 22.5431, "深圳", "特区"),
        (120.1551, 30.2741, "杭州", "省会"),
        (118.7969, 32.0603, "南京", "省会"),
        (117.2009, 39.0842, "天津", "直辖市"),
        (104.0668, 30.5728, "成都", "省会"),
        (108.9402, 34.3416, "西安", "省会"),
        (126.6424, 45.7575, "哈尔滨", "省会"),
        (123.4315, 41.8057, "沈阳", "省会"),
        (91.1409, 29.6456, "拉萨", "省会")
    ]
    
    # 提取坐标和标签
    points = [(city[0], city[1], city[2], city[3]) for city in cities]
    labels = [city[2] for city in cities]
    
    print("1. 创建归一化器...")
    # 创建归一化器，输出范围设为[-1, 1]
    normalizer = GeoPOINormalizer(output_range=(-1, 1))
    
    # 添加POI点
    for point in points:
        normalizer.add_point(point[0], point[1], point[2], point[3])
    
    print("2. 计算归一化参数...")
    # 计算归一化参数
    normalizer.compute_projection()
    normalizer.compute_normalization_params()
    
    # 归一化所有点
    normalized_points = normalizer.normalize_points()
    
    print("3. 生成归一化报告...")
    # 打印报告
    normalizer.print_report()
    
    print("\n4. 可视化原始经纬度分布...")
    # 可视化原始经纬度分布
    plt.figure(figsize=(10, 8))
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    plt.scatter(lons, lats, c='blue', marker='o')
    
    for i, label in enumerate(labels):
        plt.annotate(label, (lons[i], lats[i]))
    
    plt.title('中国主要城市分布 (原始经纬度)')
    plt.xlabel('经度')
    plt.ylabel('纬度')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "original_distribution.png"), dpi=300)
    
    print("5. 可视化归一化后的分布...")
    # 可视化归一化后的分布
    plt.figure(figsize=(10, 8))
    norm_xs = [p[0] for p in normalized_points]
    norm_ys = [p[1] for p in normalized_points]
    plt.scatter(norm_xs, norm_ys, c='red', marker='o')
    
    for i, label in enumerate(labels):
        plt.annotate(label, (norm_xs[i], norm_ys[i]))
    
    plt.title('中国主要城市分布 (归一化坐标 [-1,1])')
    plt.xlabel('X_norm')
    plt.ylabel('Y_norm')
    plt.xlim(-1.1, 1.1)
    plt.ylim(-1.1, 1.1)
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "normalized_distribution.png"), dpi=300)
    
    print("6. 分析城市间距离关系...")
    # 分析城市间距离关系
    # 计算北京到其他城市的实际距离和归一化距离
    beijing_idx = labels.index("北京")
    beijing_norm = normalized_points[beijing_idx]
    
    distances = []
    for i, city in enumerate(points):
        if i != beijing_idx:
            # 计算实际距离（简化计算，仅作示例）
            lon1, lat1 = points[beijing_idx][0], points[beijing_idx][1]
            lon2, lat2 = city[0], city[1]
            
            # 使用GeoPOINormalizer计算投影后的距离
            x1, y1 = normalizer.transformer_to_proj.transform(lon1, lat1)
            x2, y2 = normalizer.transformer_to_proj.transform(lon2, lat2)
            actual_dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2) / 1000  # 转换为公里
            
            # 计算归一化距离
            norm_x1, norm_y1 = beijing_norm[0], beijing_norm[1]
            norm_x2, norm_y2 = normalized_points[i][0], normalized_points[i][1]
            norm_dist = np.sqrt((norm_x2 - norm_x1)**2 + (norm_y2 - norm_y1)**2)
            
            distances.append((city[2], actual_dist, norm_dist))
    
    # 可视化距离关系
    plt.figure(figsize=(12, 6))
    cities_names = [d[0] for d in distances]
    actual_distances = [d[1] for d in distances]
    norm_distances = [d[2] * 1000 for d in distances]  # 缩放以便于可视化
    
    x = np.arange(len(cities_names))
    width = 0.35
    
    plt.bar(x - width/2, actual_distances, width, label='实际距离 (公里)')
    plt.bar(x + width/2, norm_distances, width, label='归一化距离 × 1000')
    
    plt.xlabel('城市')
    plt.ylabel('距离')
    plt.title('北京到其他城市的距离比较')
    plt.xticks(x, cities_names, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "distance_comparison.png"), dpi=300)
    
    print("7. 可视化距离归一化效果...")
    # 可视化距离归一化效果
    plt.figure(figsize=(10, 8))
    plt.scatter(norm_xs, norm_ys, c='red', marker='o')
    
    for i, label in enumerate(labels):
        plt.annotate(label, (norm_xs[i], norm_ys[i]))
    
    # 绘制从北京出发的100公里、500公里和1000公里的圆
    distances_km = [100, 500, 1000]
    for dist_km in distances_km:
        norm_dist = normalizer.normalize_distance(dist_km * 1000)
        circle = plt.Circle((beijing_norm[0], beijing_norm[1]), norm_dist, 
                           fill=False, color='blue', linestyle='--')
        plt.gca().add_patch(circle)
        plt.text(beijing_norm[0], beijing_norm[1] + norm_dist, f"{dist_km}公里", 
                ha='center', va='bottom')
    
    plt.title('距离归一化效果 (从北京出发)')
    plt.xlabel('X_norm')
    plt.ylabel('Y_norm')
    plt.xlim(-1.1, 1.1)
    plt.ylim(-1.1, 1.1)
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "distance_circles.png"), dpi=300)
    
    print(f"\n分析完成! 所有图像已保存到 {output_dir} 目录")


if __name__ == "__main__":
    visualize_poi_data()