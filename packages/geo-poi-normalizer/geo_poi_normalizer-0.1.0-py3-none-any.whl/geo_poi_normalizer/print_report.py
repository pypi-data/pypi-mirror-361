def print_report(self):
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