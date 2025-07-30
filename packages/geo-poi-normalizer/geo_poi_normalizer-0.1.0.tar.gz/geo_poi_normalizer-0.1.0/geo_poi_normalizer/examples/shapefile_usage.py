"""
GeoPOINormalizer从Shapefile加载数据示例
"""

from geo_poi_normalizer import GeoPOINormalizer
import os

def main():
    # 创建归一化器，输出范围设为[0, 1]
    normalizer = GeoPOINormalizer(output_range=(0, 1))

    # 假设shapefile路径
    shp_path = "data/poi_data"  # 不包含扩展名
    
    # 检查文件是否存在
    if not os.path.exists(shp_path + ".shp"):
        print(f"示例Shapefile不存在: {shp_path}.shp")
        print("这是一个演示代码，需要您提供自己的Shapefile数据。")
        print("\n模拟加载一些点以展示功能...")
        
        # 添加一些模拟点
        points = [
            (116.4074, 39.9042, "北京", "首都"),
            (121.4737, 31.2304, "上海", "直辖市"),
            (113.2644, 23.1291, "广州", "省会"),
            (114.0579, 22.5431, "深圳", "特区"),
            (120.1551, 30.2741, "杭州", "省会"),
        ]
        for point in points:
            normalizer.add_point(point[0], point[1], point[2], point[3])
    else:
        # 从shapefile加载POI
        print(f"从Shapefile加载POI: {shp_path}.shp")
        normalizer.load_from_shapefile(shp_path, lat_field="latitude", lon_field="longitude")

    # 计算并应用归一化
    normalizer.compute_projection()
    normalizer.compute_normalization_params()
    normalized_points = normalizer.normalize_points()

    # 打印前5个归一化点
    print("\n前5个归一化点:")
    for i, point in enumerate(normalized_points[:5]):
        if len(point) > 2:
            print(f"{point[2]}: ({point[0]:.4f}, {point[1]:.4f})")
        else:
            print(f"点{i+1}: ({point[0]:.4f}, {point[1]:.4f})")

    # 打印报告
    normalizer.print_report()

    # 归一化单个点
    sample_point = (116.4074, 39.9042)  # 北京
    normalized_sample = normalizer.normalize_point(*sample_point)
    print(f"\n样本点(北京)归一化结果: ({normalized_sample[0]:.6f}, {normalized_sample[1]:.6f})")

    # 距离归一化示例
    distance_km = 100  # 100公里
    normalized_dist = normalizer.normalize_distance(distance_km * 1000)
    print(f"100公里归一化距离: {normalized_dist:.6f}")

    # 反归一化距离
    original_dist = normalizer.denormalize_distance(normalized_dist) / 1000
    print(f"反归一化距离: {original_dist:.2f}公里")

if __name__ == "__main__":
    main()