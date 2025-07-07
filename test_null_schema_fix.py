#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试空值schema修复的脚本
验证_find_time_fields_in_schema方法对None和无效schema的处理
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_swagger_parser import EnhancedSwaggerParser

def test_null_schema_handling():
    """测试空值schema处理"""
    print("=== 测试空值schema处理 ===")
    
    parser = EnhancedSwaggerParser(['time'])
    
    # 测试用例
    test_cases = [
        (None, "None schema"),
        ({}, "空字典schema"),
        ([], "列表类型schema"),
        ("string", "字符串类型schema"),
        (123, "数字类型schema"),
        ({"type": "object", "properties": None}, "properties为None的schema"),
        ({"type": "array", "items": None}, "items为None的schema"),
        ({"$ref": None}, "$ref为None的schema"),
        ({"allOf": [None, {"type": "string"}]}, "allOf包含None的schema")
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, (schema, description) in enumerate(test_cases, 1):
        try:
            print("\n{:2d}. 测试: {}".format(i, description))
            print("    Schema: {}".format(repr(schema)))
            
            # 调用可能出错的方法
            result = parser._find_time_fields_in_schema(schema, "测试位置", "测试路径")
            
            print("    结果: 成功处理，返回 {} 个字段".format(len(result)))
            success_count += 1
            
        except Exception as e:
            print("    结果: 发生错误 - {}: {}".format(type(e).__name__, str(e)))
    
    print("\n=== 测试结果汇总 ===")
    print("成功: {}/{}".format(success_count, total_count))
    print("失败: {}/{}".format(total_count - success_count, total_count))
    
    if success_count == total_count:
        print("✅ 所有测试通过！空值处理修复成功。")
        return True
    else:
        print("❌ 部分测试失败，需要进一步修复。")
        return False

def test_complex_nested_schema():
    """测试复杂嵌套schema处理"""
    print("\n=== 测试复杂嵌套schema处理 ===")
    
    parser = EnhancedSwaggerParser(['time', 'date'])
    
    # 模拟可能导致问题的复杂schema
    complex_schema = {
        "type": "object",
        "properties": {
            "user_info": {
                "type": "object",
                "properties": {
                    "create_time": {"type": "string", "description": "创建时间"},
                    "profile": {
                        "type": "object",
                        "properties": {
                            "last_login_time": {"type": "string"},
                            "nested_data": None  # 这里故意设置为None
                        }
                    }
                }
            },
            "metadata": {
                "allOf": [
                    {"type": "object", "properties": {"update_time": {"type": "string"}}},
                    None,  # 故意包含None
                    {"type": "object", "properties": {"version": {"type": "string"}}}
                ]
            }
        }
    }
    
    try:
        result = parser._find_time_fields_in_schema(complex_schema, "复杂测试", "")
        print("成功处理复杂schema，找到 {} 个时间字段:".format(len(result)))
        for field in result:
            print("  - {}: {} ({})".format(field.field_path, field.field_type, field.location))
        return True
    except Exception as e:
        print("处理复杂schema时发生错误: {}: {}".format(type(e).__name__, str(e)))
        return False

def main():
    """主测试函数"""
    print("开始测试空值schema修复...\n")
    
    test1_passed = test_null_schema_handling()
    test2_passed = test_complex_nested_schema()
    
    print("\n" + "="*50)
    print("最终测试结果:")
    print("- 空值处理测试: {}".format("✅ 通过" if test1_passed else "❌ 失败"))
    print("- 复杂schema测试: {}".format("✅ 通过" if test2_passed else "❌ 失败"))
    
    if test1_passed and test2_passed:
        print("\n🎉 所有测试通过！代码修复成功。")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要进一步检查。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)