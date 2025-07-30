"""
GeoPOINormalizer可视化测试

这个模块提供了可视化测试功能，用于展示归一化前后的POI点分布。
"""

import matplotlib.pyplot as plt
import numpy as np
from geo_poi_normalizer import GeoPOINormalizer


def visualize_normalization_process(points, labels=None, output_range=(0, 1), save_path=None):
    """
    可视化归一化过程
    
    :param points: POI点列表，格式为[(lon1, lat1), (lon2, lat2), ...]
    :param labels: 点的标签列表，可选
    :param output_range: 归一化输出范围，默认为(0, 1)
    :param save_path: 保存图像的路径，如果为None则显示图像
    """
    # 创建归一化器
    normalizer = GeoPOINormalizer(output_range=output_range)
    normalizer.add_points(points)
    
    # 计算投影和归一化参数
    normalizer.compute_projection()
    normalizer.project_points()
    normalizer.compute_normalization_params()
    
    # 归一化点
    normalized_points = normalizer.normalize_points()
    
    # 反归一化点
    denormalized_points = []
    for point in normalized_points:
        denorm_point = normalizer.denormalize_point(point[0], point[1])
        denormalized_points.append(denorm_point)
    
    # 提取坐标
    original_lons = [p[0] for p in points]
    original_lats = [p[1] for p in points]
    
    projected_xs = [p[0] for p in normalizer.projected_points]
    projected_ys = [p[1] for p in normalizer.projected_points]
    
    normalized_xs = [p[0] for p in normalized_points]
    normalized_ys = [p[1] for p in normalized_points]
    
    denormalized_lons = [p[0] for p in denormalized_points]
    denormalized_lats = [p[1] for p in denormalized_points]
    
    # 创建图形
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 原始经纬度分布
    ax1 = fig.add_subplot(221)
    ax1.scatter(original_lons, original_lats, c='blue', marker='o')
    if labels:
        for i, label in enumerate(labels):
            ax1.annotate(label, (original_lons[i], original_lats[i]))
    ax1.set_title('Original Geographic Distribution')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.grid(True)
    
    # 2. 投影后的平面坐标分布
    ax2 = fig.add_subplot(222)
    ax2.scatter(projected_xs, projected_ys, c='green', marker='o')
    if labels:
        for i, label in enumerate(labels):
            ax2.annotate(label, (projected_xs[i], projected_ys[i]))
    ax2.set_title('Projected Coordinates (meters)')
    ax2.set_xlabel('X (meters)')
    ax2.set_ylabel('Y (meters)')
    ax2.grid(True)
    
    # 3. 归一化后的坐标分布
    ax3 = fig.add_subplot(223)
    ax3.scatter(normalized_xs, normalized_ys, c='red', marker='o')
    if labels:
        for i, label in enumerate(labels):
            ax3.annotate(label, (normalized_xs[i], normalized_ys[i]))
    
    # 设置坐标轴范围
    if output_range == (0, 1):
        ax3.set_xlim(-0.1, 1.1)
        ax3.set_ylim(-0.1, 1.1)
        ax3.set_title('Normalized Coordinates [0,1]')
    else:
        ax3.set_xlim(-1.1, 1.1)
        ax3.set_ylim(-1.1, 1.1)
        ax3.set_title('Normalized Coordinates [-1,1]')
    
    ax3.set_xlabel('X_norm')
    ax3.set_ylabel('Y_norm')
    ax3.grid(True)
    
    # 4. 反归一化后与原始坐标的对比
    ax4 = fig.add_subplot(224)
    ax4.scatter(original_lons, original_lats, c='blue', marker='o', label='Original')
    ax4.scatter(denormalized_lons, denormalized_lats, c='purple', marker='x', label='Denormalized')
    if labels:
        for i, label in enumerate(labels):
            ax4.annotate(label, (original_lons[i], original_lats[i]))
    ax4.set_title('Original vs Denormalized Coordinates')
    ax4.set_xlabel('Longitude')
    ax4.set_ylabel('Latitude')
    ax4.legend()
    ax4.grid(True)
    
    # 添加归一化报告
    report = normalizer.get_normalization_report()
    report_text = (
        f"POI Count: {report['point_count']}\n"
        f"Projection: UTM Zone {report['projection']['zone']}\n"
        f"Scale Factor: {report['normalization']['scale_factor']:.2f}m\n"
        f"Normalized Width: {report['normalization']['normalized_width']:.6f}\n"
        f"Normalized Height: {report['normalization']['normalized_height']:.6f}\n"
    )
    fig.text(0.02, 0.02, report_text, fontsize=10)
    
    plt.tight_layout()
    
    # 保存或显示图像
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()
    
    return normalizer


def test_china_cities():
    """测试中国主要城市的归一化可视化"""
    # 中国主要城市
    cities = [
        (116.4074, 39.9042, "Beijing"),
        (121.4737, 31.2304, "Shanghai"),
        (113.2644, 23.1291, "Guangzhou"),
        (114.0579, 22.5431, "Shenzhen"),
        (120.1551, 30.2741, "Hangzhou"),
        (118.7969, 32.0603, "Nanjing"),
        (117.2009, 39.0842, "Tianjin"),
        (104.0668, 30.5728, "Chengdu"),
        (108.9402, 34.3416, "Xi'an"),
        (126.6424, 45.7575, "Harbin"),
        (123.4315, 41.8057, "Shenyang"),
        (91.1409, 29.6456, "Lhasa")
    ]
    
    # 提取坐标和标签
    points = [(city[0], city[1]) for city in cities]
    labels = [city[2] for city in cities]
    
    # 测试 [0,1] 范围归一化
    print("Testing [0,1] range normalization...")
    normalizer_01 = visualize_normalization_process(points, labels, output_range=(0, 1), 
                                                  save_path="china_cities_norm_01.png")
    
    # 测试 [-1,1] 范围归一化
    print("Testing [-1,1] range normalization...")
    normalizer_11 = visualize_normalization_process(points, labels, output_range=(-1, 1), 
                                                  save_path="china_cities_norm_11.png")
    
    # 打印归一化报告
    print("\n[0,1] Range Normalization Report:")
    normalizer_01.print_report()
    
    print("\n[-1,1] Range Normalization Report:")
    normalizer_11.print_report()


def test_distance_visualization():
    """测试距离归一化可视化"""
    # 创建一个测试场景：北京为中心，周围添加几个点以创建合理的缩放范围
    beijing = (116.4074, 39.9042)
    
    # 添加北京周围约100公里的几个点
    points = [
        beijing,  # 北京
        (116.4074, 40.8042),  # 北京北部约100公里
        (116.4074, 39.0042),  # 北京南部约100公里
        (117.3074, 39.9042),  # 北京东部约100公里
        (115.5074, 39.9042),  # 北京西部约100公里
    ]
    
    # 创建归一化器
    normalizer = GeoPOINormalizer(output_range=(0, 1))
    normalizer.add_points(points)
    normalizer.add_point(*beijing, "Beijing")  # 再次添加北京点，用于标记
    
    # 计算投影和归一化参数
    normalizer.compute_projection()
    normalizer.project_points()
    normalizer.compute_normalization_params()
    
    # 计算100公里的归一化距离
    distance_km = 100
    norm_distance = normalizer.normalize_distance(distance_km * 1000)
    print(f"Normalized distance for 100 km: {norm_distance:.6f}")
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # 绘制北京点
    norm_beijing = normalizer.normalize_point(*beijing)
    ax.scatter(norm_beijing[0], norm_beijing[1], c='red', marker='o', s=100)
    ax.annotate("Beijing", (norm_beijing[0], norm_beijing[1]))
    
    # 绘制100公里半径圆
    circle = plt.Circle((norm_beijing[0], norm_beijing[1]), norm_distance, 
                        fill=False, color='blue', linestyle='--')
    ax.add_patch(circle)
    ax.text(norm_beijing[0], norm_beijing[1] + norm_distance + 0.02, 
            f"100 km (normalized distance: {norm_distance:.6f})", 
            ha='center')
    
    # 设置坐标轴
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('Distance normalized visualization (100 km radius)')
    ax.set_xlabel('X_norm')
    ax.set_ylabel('Y_norm')
    ax.grid(True)
    
    plt.savefig("distance_visualization.png", dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    print("运行中国城市归一化可视化测试...")
    test_china_cities()
    
    print("\n运行距离归一化可视化测试...")
    test_distance_visualization()