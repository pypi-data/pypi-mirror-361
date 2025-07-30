"""
GeoPOINormalizer基本用法示例
"""

from geo_poi_normalizer import GeoPOINormalizer

def main():
    # 创建归一化器，输出范围设为[-1, 1]
    normalizer = GeoPOINormalizer(output_range=(-1, 1))

    # 添加POI点
    points = [
        (116.4074, 39.9042),  # 北京
        (121.4737, 31.2304),  # 上海
        (113.2644, 23.1291),  # 广州
        (114.0579, 22.5431),  # 深圳
        (120.1551, 30.2741),  # 杭州
        (118.7969, 32.0603),  # 南京
        (117.2009, 39.0842)   # 天津
    ]
    normalizer.add_points(points)

    # 计算归一化参数
    normalizer.compute_projection()
    normalizer.compute_normalization_params()

    # 归一化所有点
    normalized_points = normalizer.normalize_points()
    print("归一化后的点:")
    for i, point in enumerate(normalized_points):
        city_name = ["北京", "上海", "广州", "深圳", "杭州", "南京", "天津"][i]
        print(f"{city_name}: ({point[0]:.4f}, {point[1]:.4f})")

    # 反归一化示例
    original_point = normalizer.denormalize_point(normalized_points[0][0], normalized_points[0][1])
    print("\n反归一化第一个点(北京):")
    print(f"原始经纬度: (116.4074, 39.9042)")
    print(f"反归一化结果: ({original_point[0]:.6f}, {original_point[1]:.6f})")

    # 距离归一化示例
    distance_km = 100  # 100公里
    normalized_dist = normalizer.normalize_distance(distance_km * 1000)
    print(f"\n100公里归一化距离: {normalized_dist:.6f}")

    # 反归一化距离
    original_dist = normalizer.denormalize_distance(normalized_dist) / 1000
    print(f"反归一化距离: {original_dist:.2f}公里")

    # 打印报告
    normalizer.print_report()

if __name__ == "__main__":
    main()