#!/usr/bin/env python3
"""
GeoPOINormalizer测试运行器

这个脚本用于运行GeoPOINormalizer库的所有测试，包括单元测试和可视化测试。
"""

import unittest
import argparse
import sys
import os

# 确保可以导入测试模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_normalizer import TestGeoPOINormalizer
from tests.test_visualization import test_china_cities, test_distance_visualization


def run_unit_tests():
    """运行单元测试"""
    print("运行GeoPOINormalizer单元测试...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGeoPOINormalizer)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()


def run_visualization_tests():
    """运行可视化测试"""
    print("\n运行GeoPOINormalizer可视化测试...")
    
    try:
        # 测试中国城市归一化可视化
        print("\n1. 中国城市归一化可视化测试")
        test_china_cities()
        print("中国城市归一化可视化测试完成，图像已保存为 china_cities_norm_01.png 和 china_cities_norm_11.png")
        
        # 测试距离归一化可视化
        print("\n2. 距离归一化可视化测试")
        test_distance_visualization()
        print("距离归一化可视化测试完成，图像已保存为 distance_visualization.png")
        
        return True
    except Exception as e:
        print(f"可视化测试失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行GeoPOINormalizer测试')
    parser.add_argument('--unit', action='store_true', help='只运行单元测试')
    parser.add_argument('--visual', action='store_true', help='只运行可视化测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    
    args = parser.parse_args()
    
    # 如果没有指定任何参数，默认运行所有测试
    if not (args.unit or args.visual or args.all):
        args.all = True
    
    success = True
    
    # 运行单元测试
    if args.unit or args.all:
        unit_success = run_unit_tests()
        success = success and unit_success
    
    # 运行可视化测试
    if args.visual or args.all:
        visual_success = run_visualization_tests()
        success = success and visual_success
    
    # 返回测试结果
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())