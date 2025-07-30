#!/usr/bin/env python3
"""
JSON 精度控制功能演示脚本

展示不同精度设置下的数据大小变化效果。
"""
import json
import math
from pathlib import Path

from lims2.utils import round_floats, get_json_size, format_file_size


def generate_test_data():
    """生成包含大量浮点数的测试数据"""
    # 生成 Plotly 散点图数据
    plotly_data = {
        "data": [{
            "x": [i * 3.141592653589793 for i in range(200)],
            "y": [i * 2.718281828459045 for i in range(200)],
            "type": "scatter",
            "mode": "markers+lines",
            "name": "高精度数据",
            "marker": {
                "size": [5.5 + i * 0.123456789 for i in range(200)],
                "color": [i * 1.618033988749895 for i in range(200)]
            }
        }],
        "layout": {
            "title": "高精度浮点数图表",
            "xaxis": {"title": "X轴 (π倍数)"},
            "yaxis": {"title": "Y轴 (e倍数)"},
            "width": 800.123456789,
            "height": 600.987654321,
            "margin": {
                "t": 50.111111,
                "b": 50.222222,
                "l": 60.333333,
                "r": 60.444444
            }
        }
    }
    
    # 生成 Cytoscape 网络图数据
    cytoscape_data = {
        "elements": []
    }
    
    # 添加节点
    for i in range(50):
        cytoscape_data["elements"].append({
            "data": {
                "id": f"node_{i}",
                "label": f"Node {i}",
                "weight": i * 2.718281828459045,
                "value": i * 3.141592653589793
            },
            "position": {
                "x": i * 12.34567890123456,
                "y": (50-i) * 9.87654321098765
            }
        })
    
    # 添加边
    for i in range(40):
        cytoscape_data["elements"].append({
            "data": {
                "id": f"edge_{i}",
                "source": f"node_{i}",
                "target": f"node_{i+1}",
                "weight": (i+1) * 1.618033988749895,
                "score": math.sin(i) * 100.123456789
            }
        })
    
    return plotly_data, cytoscape_data


def test_precision_effects():
    """测试不同精度设置的效果"""
    print("=" * 60)
    print("JSON 精度控制功能演示")
    print("=" * 60)
    
    # 生成测试数据
    plotly_data, cytoscape_data = generate_test_data()
    
    # 测试 Plotly 数据
    print("\n📊 Plotly 图表数据测试:")
    print("-" * 40)
    
    test_data_with_precisions("Plotly 散点图", plotly_data)
    
    # 测试 Cytoscape 数据
    print("\n🕸️  Cytoscape 网络图数据测试:")
    print("-" * 40)
    
    test_data_with_precisions("Cytoscape 网络图", cytoscape_data)
    
    # 测试特殊值处理
    print("\n⚠️  特殊值处理测试:")
    print("-" * 40)
    
    test_special_values()
    
    # 测试现有示例文件
    print("\n📁 现有示例文件测试:")
    print("-" * 40)
    
    test_example_files()


def test_data_with_precisions(data_name, data):
    """测试指定数据在不同精度下的效果"""
    print(f"\n{data_name}:")
    
    original_size = get_json_size(data)
    print(f"  原始大小: {format_file_size(original_size)}")
    
    # 测试不同精度
    for precision in [0, 1, 2, 3, 4]:
        processed_data = round_floats(data, precision=precision)
        processed_size = get_json_size(processed_data)
        reduction_percent = (1 - processed_size / original_size) * 100 if original_size > 0 else 0
        
        print(f"  精度 {precision}: {format_file_size(processed_size)} "
              f"(减少 {reduction_percent:.1f}%)")


def test_special_values():
    """测试特殊值的处理"""
    special_data = {
        "normal_values": [1.23456, 2.34567, 3.45678],
        "nan_value": float('nan'),
        "inf_value": float('inf'),
        "neg_inf_value": float('-inf'),
        "nested": {
            "values": [1.111111, float('nan'), 2.222222, float('inf')],
            "coordinates": {
                "x": 3.333333,
                "y": float('-inf'),
                "z": 4.444444
            }
        }
    }
    
    print("\n  原始数据（特殊值）:")
    print(f"    NaN: {special_data['nan_value']}")
    print(f"    Infinity: {special_data['inf_value']}")
    print(f"    -Infinity: {special_data['neg_inf_value']}")
    
    processed_data = round_floats(special_data, precision=2)
    
    print("\n  处理后数据:")
    print(f"    NaN -> {processed_data['nan_value']}")
    print(f"    Infinity -> {processed_data['inf_value']}")
    print(f"    -Infinity -> {processed_data['neg_inf_value']}")
    print(f"    嵌套数组中的特殊值也被处理: {processed_data['nested']['values']}")


def test_example_files():
    """测试现有示例文件的效果"""
    examples_dir = Path(__file__).parent
    
    json_files = [
        "gene_expression_bar.json",
        "simple_scatter.json",
        "ppi_network.json"
    ]
    
    for filename in json_files:
        file_path = examples_dir / filename
        if file_path.exists():
            print(f"\n  {filename}:")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                original_size = get_json_size(data)
                print(f"    原始大小: {format_file_size(original_size)}")
                
                # 测试精度 2
                processed_data = round_floats(data, precision=2)
                processed_size = get_json_size(processed_data)
                
                if processed_size < original_size:
                    reduction_percent = (1 - processed_size / original_size) * 100
                    print(f"    精度控制后: {format_file_size(processed_size)} "
                          f"(减少 {reduction_percent:.1f}%)")
                else:
                    print(f"    精度控制后: 无变化（没有高精度浮点数）")
                    
            except Exception as e:
                print(f"    读取失败: {e}")
        else:
            print(f"  {filename}: 文件不存在")




def demonstrate_api_usage():
    """演示 API 使用方式"""
    print("\n" + "=" * 60)
    print("API 使用示例")
    print("=" * 60)
    
    # 生成示例数据
    chart_data = {
        "data": [{
            "x": [1.234567890, 2.345678901, 3.456789012],
            "y": [4.567890123, 5.678901234, 6.789012345],
            "type": "scatter"
        }],
        "layout": {"title": "示例图表"}
    }
    
    print("\n📋 代码示例:")
    print("-" * 40)
    
    print("\n1. 使用 Python API (模拟):")
    print("```python")
    print("from lims2 import Lims2Client")
    print()
    print("client = Lims2Client()")
    print("result = client.chart.upload(")
    print("    chart_data, 'proj_001', '图表名称',")
    print("    precision=3  # 保留3位小数（默认）")
    print(")")
    print("```")
    
    print("\n2. 使用便捷函数 (模拟):")
    print("```python")
    print("from lims2 import upload_chart_from_data")
    print()
    print("result = upload_chart_from_data(")
    print("    '图表名称', 'proj_001', chart_data,")
    print("    precision=3")
    print(")")
    print("```")
    
    print("\n3. 使用 CLI 命令:")
    print("```bash")
    print("lims2 chart upload chart.json -p proj_001 -n '图表名称' --precision 3")
    print("```")
    
    # 显示实际的大小变化
    print("\n📊 实际效果:")
    print("-" * 40)
    original_size = get_json_size(chart_data)
    processed_data = round_floats(chart_data, 3)
    processed_size = get_json_size(processed_data)
    reduction_percent = (1 - processed_size / original_size) * 100 if original_size > 0 else 0
    
    print(f"原始大小: {format_file_size(original_size)}")
    print(f"处理后大小: {format_file_size(processed_size)}")
    print(f"减少: {reduction_percent:.1f}%")


if __name__ == "__main__":
    test_precision_effects()
    demonstrate_api_usage()
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n💡 建议:")
    print("  - 对于大多数生物信息学数据，precision=3（默认）是一个很好的平衡")
    print("  - 精度控制可以显著减少数据大小，特别是对于包含大量浮点数的数据")
    print("  - NaN 和 Infinity 值会被安全地转换为 null，确保 JSON 兼容性")
    print("  - 精度控制是可选的，不会影响现有代码的兼容性")