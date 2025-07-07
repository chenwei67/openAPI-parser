#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析器对比测试脚本
用于演示原版解析器和增强版解析器的差异
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from swagger_time_parser import SwaggerTimeParser
from enhanced_swagger_parser import EnhancedSwaggerParser


def test_swagger2_file():
    """测试Swagger 2.0文件解析"""
    print("=" * 60)
    print("测试 Swagger 2.0 文件解析")
    print("=" * 60)
    
    swagger2_file = "example_swagger.json"
    
    if not os.path.exists(swagger2_file):
        print("警告: {} 文件不存在，跳过Swagger 2.0测试".format(swagger2_file))
        return
    
    print("\n使用原版解析器解析 {}:".format(swagger2_file))
    print("-" * 40)
    try:
        original_parser = SwaggerTimeParser()
        original_apis = original_parser.parse_swagger_file(swagger2_file)
        original_result = original_parser.generate_markdown_table(original_apis)
        print(original_result)
        print("\n找到 {} 个包含时间字段的API".format(len(original_apis)))
    except Exception as e:
        print("原版解析器错误: {}".format(e))
    
    print("\n使用增强版解析器解析 {}:".format(swagger2_file))
    print("-" * 40)
    try:
        enhanced_parser = EnhancedSwaggerParser()
        enhanced_apis = enhanced_parser.parse_file(swagger2_file)
        enhanced_result = enhanced_parser.generate_markdown_table(enhanced_apis)
        print("检测到的规范版本: {}".format(enhanced_parser.spec_version))
        print(enhanced_result)
        print("\n找到 {} 个包含时间字段的API".format(len(enhanced_apis)))
    except Exception as e:
        print("增强版解析器错误: {}".format(e))


def test_openapi3_file():
    """测试OpenAPI 3.x文件解析"""
    print("\n" + "=" * 60)
    print("测试 OpenAPI 3.x 文件解析")
    print("=" * 60)
    
    openapi3_file = "example_openapi3.json"
    
    if not os.path.exists(openapi3_file):
        print("警告: {} 文件不存在，跳过OpenAPI 3.x测试".format(openapi3_file))
        return
    
    print("\n使用原版解析器解析 {}:".format(openapi3_file))
    print("-" * 40)
    try:
        original_parser = SwaggerTimeParser()
        original_apis = original_parser.parse_swagger_file(openapi3_file)
        original_result = original_parser.generate_markdown_table(original_apis)
        print(original_result)
        print("\n找到 {} 个包含时间字段的API".format(len(original_apis)))
    except Exception as e:
        print("原版解析器错误: {}".format(e))
        print("这是预期的错误，因为原版解析器不支持OpenAPI 3.x格式")
    
    print("\n使用增强版解析器解析 {}:".format(openapi3_file))
    print("-" * 40)
    try:
        enhanced_parser = EnhancedSwaggerParser()
        enhanced_apis = enhanced_parser.parse_file(openapi3_file)
        enhanced_result = enhanced_parser.generate_markdown_table(enhanced_apis)
        print("检测到的规范版本: {}".format(enhanced_parser.spec_version))
        print(enhanced_result)
        print("\n找到 {} 个包含时间字段的API".format(len(enhanced_apis)))
    except Exception as e:
        print("增强版解析器错误: {}".format(e))


def test_version_detection():
    """测试版本检测功能"""
    print("\n" + "=" * 60)
    print("测试版本检测功能")
    print("=" * 60)
    
    # 测试数据
    test_cases = [
        {
            "name": "Swagger 2.0",
            "data": {
                "swagger": "2.0",
                "info": {"title": "Test API", "version": "1.0.0"},
                "paths": {}
            }
        },
        {
            "name": "OpenAPI 3.0.0",
            "data": {
                "openapi": "3.0.0",
                "info": {"title": "Test API", "version": "1.0.0"},
                "paths": {}
            }
        },
        {
            "name": "OpenAPI 3.1.0",
            "data": {
                "openapi": "3.1.0",
                "info": {"title": "Test API", "version": "1.0.0"},
                "paths": {}
            }
        },
        {
            "name": "无效格式",
            "data": {
                "info": {"title": "Test API", "version": "1.0.0"},
                "paths": {}
            }
        }
    ]
    
    enhanced_parser = EnhancedSwaggerParser()
    
    for test_case in test_cases:
        print("\n测试 {}:".format(test_case['name']))
        try:
            enhanced_parser.parse_data(test_case['data'])
            print("  检测到版本: {}".format(enhanced_parser.spec_version))
        except Exception as e:
            print("  错误: {}".format(e))


def analyze_parsing_differences():
    """分析解析差异"""
    print("\n" + "=" * 60)
    print("解析差异分析")
    print("=" * 60)
    
    # 检查支持的功能
    print("\n功能支持对比:")
    print("-" * 30)
    
    features = [
        ("Swagger 2.0支持", "✅", "✅"),
        ("OpenAPI 3.x支持", "❌", "✅"),
        ("自动版本检测", "❌", "✅"),
        ("requestBody解析", "❌", "✅"),
        ("多媒体类型支持", "❌", "✅"),
        ("allOf/oneOf/anyOf", "❌", "✅"),
        ("components/schemas", "❌", "✅")
    ]
    
    print("{:<20} {:<8} {:<8}".format('功能', '原版', '增强版'))
    print("-" * 40)
    for feature, original, enhanced in features:
        print("{:<20} {:<8} {:<8}".format(feature, original, enhanced))
    
    # 检查支持的版本
    enhanced_parser = EnhancedSwaggerParser()
    supported_versions = enhanced_parser.get_supported_versions()
    
    print("\n增强版解析器支持的版本:")
    print("-" * 30)
    for spec_type, versions in supported_versions.items():
        print("{}: {}".format(spec_type.upper(), ', '.join(versions)))


def main():
    """主函数"""
    print("Swagger/OpenAPI 解析器对比测试")
    print("=" * 60)
    
    # 测试Swagger 2.0文件
    test_swagger2_file()
    
    # 测试OpenAPI 3.x文件
    test_openapi3_file()
    
    # 测试版本检测
    test_version_detection()
    
    # 分析解析差异
    analyze_parsing_differences()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    print("\n总结:")
    print("1. 原版解析器只支持Swagger 2.0格式")
    print("2. 增强版解析器同时支持Swagger 2.0和OpenAPI 3.x格式")
    print("3. 增强版解析器提供更详细的解析信息和错误处理")
    print("4. 对于新项目，推荐使用增强版解析器")


if __name__ == "__main__":
    main()