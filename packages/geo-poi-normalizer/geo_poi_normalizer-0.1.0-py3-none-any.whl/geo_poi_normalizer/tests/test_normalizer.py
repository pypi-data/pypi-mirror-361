"""
GeoPOINormalizer类的单元测试
"""

import unittest
import numpy as np
from geo_poi_normalizer import GeoPOINormalizer


class TestGeoPOINormalizer(unittest.TestCase):
    """测试GeoPOINormalizer类的核心功能"""

    def setUp(self):
        """每个测试前的设置"""
        # 创建一个标准测试数据集
        self.test_points = [
            (116.4074, 39.9042),  # 北京
            (121.4737, 31.2304),  # 上海
            (113.2644, 23.1291),  # 广州
            (114.0579, 22.5431),  # 深圳
        ]
        
        # 创建默认归一化器 [0,1] 范围
        self.normalizer_01 = GeoPOINormalizer(output_range=(0, 1))
        
        # 创建 [-1,1] 范围的归一化器
        self.normalizer_11 = GeoPOINormalizer(output_range=(-1, 1))

    def test_initialization(self):
        """测试初始化和参数验证"""
        # 测试默认参数
        normalizer = GeoPOINormalizer()
        self.assertEqual(normalizer.output_range, (0, 1))
        
        # 测试自定义输出范围
        normalizer = GeoPOINormalizer(output_range=(-1, 1))
        self.assertEqual(normalizer.output_range, (-1, 1))
        
        # 测试无效输出范围
        with self.assertRaises(ValueError):
            GeoPOINormalizer(output_range=(0, 2))

    def test_add_points(self):
        """测试点的添加功能"""
        # 测试单点添加
        self.normalizer_01.add_point(116.4074, 39.9042)
        self.assertEqual(len(self.normalizer_01.points), 1)
        self.assertEqual(self.normalizer_01.points[0][0], 116.4074)
        self.assertEqual(self.normalizer_01.points[0][1], 39.9042)
        
        # 测试带属性的点添加
        self.normalizer_01.add_point(121.4737, 31.2304, "上海", "直辖市")
        self.assertEqual(len(self.normalizer_01.points), 2)
        self.assertEqual(self.normalizer_01.points[1][2], "上海")
        
        # 测试批量添加
        normalizer = GeoPOINormalizer()
        normalizer.add_points(self.test_points)
        self.assertEqual(len(normalizer.points), 4)

    def test_projection(self):
        """测试投影计算"""
        normalizer = GeoPOINormalizer()
        normalizer.add_points(self.test_points)
        
        # 测试自动计算投影
        normalizer.compute_projection()
        self.assertIsNotNone(normalizer.projection)
        self.assertIsNotNone(normalizer.ref_lon)
        self.assertIsNotNone(normalizer.ref_lat)
        
        # 测试手动指定参考点
        normalizer.compute_projection(ref_lon=120.0, ref_lat=30.0)
        self.assertEqual(normalizer.ref_lon, 120.0)
        self.assertEqual(normalizer.ref_lat, 30.0)
        
        # 测试投影点
        normalizer.project_points()
        self.assertEqual(len(normalizer.projected_points), 4)
        self.assertIsInstance(normalizer.projected_points[0][0], float)

    def test_normalization_params(self):
        """测试归一化参数计算"""
        normalizer = GeoPOINormalizer()
        normalizer.add_points(self.test_points)
        normalizer.compute_projection()
        normalizer.compute_normalization_params()
        
        # 验证边界框和缩放因子
        self.assertIsNotNone(normalizer.x_min)
        self.assertIsNotNone(normalizer.x_max)
        self.assertIsNotNone(normalizer.y_min)
        self.assertIsNotNone(normalizer.y_max)
        self.assertIsNotNone(normalizer.scale)
        
        # 验证缩放因子是正数
        self.assertGreater(normalizer.scale, 0)

    def test_normalize_points(self):
        """测试点归一化"""
        # 测试 [0,1] 范围归一化
        self.normalizer_01.add_points(self.test_points)
        self.normalizer_01.compute_projection()
        self.normalizer_01.compute_normalization_params()
        norm_points_01 = self.normalizer_01.normalize_points()
        
        # 验证归一化结果在 [0,1] 范围内
        for point in norm_points_01:
            self.assertGreaterEqual(point[0], 0)
            self.assertLessEqual(point[0], 1)
            self.assertGreaterEqual(point[1], 0)
            self.assertLessEqual(point[1], 1)
        
        # 测试 [-1,1] 范围归一化
        self.normalizer_11.add_points(self.test_points)
        self.normalizer_11.compute_projection()
        self.normalizer_11.compute_normalization_params()
        norm_points_11 = self.normalizer_11.normalize_points()
        
        # 验证归一化结果在 [-1,1] 范围内
        for point in norm_points_11:
            self.assertGreaterEqual(point[0], -1)
            self.assertLessEqual(point[0], 1)
            self.assertGreaterEqual(point[1], -1)
            self.assertLessEqual(point[1], 1)

    def test_normalize_single_point(self):
        """测试单点归一化"""
        # 先归一化一组点以设置参数
        self.normalizer_01.add_points(self.test_points)
        self.normalizer_01.compute_projection()
        self.normalizer_01.compute_normalization_params()
        self.normalizer_01.normalize_points()
        
        # 测试单点归一化
        test_point = (116.4074, 39.9042)  # 北京
        norm_point = self.normalizer_01.normalize_point(*test_point)
        
        # 验证结果是二元组且在范围内
        self.assertEqual(len(norm_point), 2)
        self.assertGreaterEqual(norm_point[0], 0)
        self.assertLessEqual(norm_point[0], 1)
        self.assertGreaterEqual(norm_point[1], 0)
        self.assertLessEqual(norm_point[1], 1)

    def test_denormalize_point(self):
        """测试点反归一化"""
        # 先归一化一组点以设置参数
        self.normalizer_01.add_points(self.test_points)
        self.normalizer_01.compute_projection()
        self.normalizer_01.compute_normalization_params()
        norm_points = self.normalizer_01.normalize_points()
        
        # 测试反归一化
        original_point = self.test_points[0]
        norm_point = norm_points[0]
        denorm_point = self.normalizer_01.denormalize_point(norm_point[0], norm_point[1])
        
        # 验证反归一化结果接近原始点
        self.assertAlmostEqual(denorm_point[0], original_point[0], places=4)
        self.assertAlmostEqual(denorm_point[1], original_point[1], places=4)

    def test_distance_normalization(self):
        """测试距离归一化和反归一化"""
        # 先归一化一组点以设置参数
        self.normalizer_01.add_points(self.test_points)
        self.normalizer_01.compute_projection()
        self.normalizer_01.compute_normalization_params()
        self.normalizer_01.normalize_points()
        
        # 测试距离归一化
        distance_m = 100000  # 100公里
        norm_distance = self.normalizer_01.normalize_distance(distance_m)
        
        # 验证归一化距离是正数
        self.assertGreater(norm_distance, 0)
        
        # 测试距离反归一化
        denorm_distance = self.normalizer_01.denormalize_distance(norm_distance)
        
        # 验证反归一化距离接近原始距离
        self.assertAlmostEqual(denorm_distance, distance_m, delta=0.001)

    def test_report_generation(self):
        """测试报告生成"""
        # 先归一化一组点以设置参数
        self.normalizer_01.add_points(self.test_points)
        self.normalizer_01.compute_projection()
        self.normalizer_01.compute_normalization_params()
        self.normalizer_01.normalize_points()
        
        # 获取报告
        report = self.normalizer_01.get_normalization_report()
        
        # 验证报告包含所有必要字段
        self.assertIn("point_count", report)
        self.assertIn("geographic_range", report)
        self.assertIn("projection", report)
        self.assertIn("projected_range", report)
        self.assertIn("normalization", report)
        
        # 验证点数量正确
        self.assertEqual(report["point_count"], 4)
        
        # 验证输出范围正确
        self.assertEqual(report["normalization"]["output_range"], (0, 1))


if __name__ == "__main__":
    unittest.main()