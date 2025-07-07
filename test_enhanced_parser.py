#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版swagger_time_parser.py的多模式搜索功能
"""

import subprocess
import sys
import os

def run_command(cmd):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def test_enhanced_parser():
    """测试增强版解析器的各种功能"""
    print("=== 测试增强版swagger_time_parser.py功能 ===")
    print()
    
    # 检查文件是否存在
    swagger_file = "example_swagger.json"
    if not os.path.exists(swagger_file):
        print("警告: {} 文件不存在，跳过测试".format(swagger_file))
        return
    
    test_cases = [
        {
            "name": "默认搜索time字段",
            "command": "python swagger_time_parser.py {}".format(swagger_file)
        },
        {
            "name": "搜索time和date字段",
            "command": "python swagger_time_parser.py {} -p time -p date".format(swagger_file)
        },
        {
            "name": "搜索create相关字段（正则表达式）",
            "command": "python swagger_time_parser.py {} -p 'create.*'".format(swagger_file)
        },
        {
            "name": "搜索update相关字段",
            "command": "python swagger_time_parser.py {} -p 'update.*time'".format(swagger_file)
        },
        {
            "name": "搜索多种时间相关字段",
            "command": "python swagger_time_parser.py {} -p time -p date -p timestamp -p created -p updated".format(swagger_file)
        },
        {
            "name": "搜索ID字段",
            "command": "python swagger_time_parser.py {} -p id".format(swagger_file)
        },
        {
            "name": "显示帮助信息",
            "command": "python swagger_time_parser.py -h"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print("测试 {}: {}".format(i, test_case["name"]))
        print("命令: {}".format(test_case["command"]))
        print("-" * 50)
        
        returncode, stdout, stderr = run_command(test_case["command"])
        
        if returncode == 0:
            print("✅ 执行成功")
            if stdout:
                print("输出:")
                print(stdout)
        else:
            print("❌ 执行失败 (返回码: {})".format(returncode))
            if stderr:
                print("错误信息:")
                print(stderr)
        
        print("=" * 60)
        print()

def test_pattern_matching():
    """测试模式匹配功能"""
    print("=== 测试模式匹配功能 ===")
    print()
    
    # 导入解析器类进行单元测试
    try:
        from swagger_time_parser import SwaggerTimeParser
        
        test_patterns = [
            (['time'], ['createTime', 'updateTime', 'timestamp'], ['userId', 'name']),
            (['date'], ['createDate', 'birthDate'], ['createTime', 'userId']),
            (['create.*'], ['createTime', 'createDate', 'created'], ['updateTime', 'userId']),
            (['.*id'], ['userId', 'orderId', 'productId'], ['userName', 'createTime']),
            (['time', 'date'], ['createTime', 'birthDate', 'timestamp'], ['userName', 'status'])
        ]
        
        for patterns, should_match, should_not_match in test_patterns:
            print("测试模式: {}".format(patterns))
            parser = SwaggerTimeParser(patterns)
            
            # 测试应该匹配的字段
            for field in should_match:
                if parser._matches_any_pattern(field):
                    print("  ✅ '{}' 匹配".format(field))
                else:
                    print("  ❌ '{}' 应该匹配但没有匹配".format(field))
            
            # 测试不应该匹配的字段
            for field in should_not_match:
                if not parser._matches_any_pattern(field):
                    print("  ✅ '{}' 正确不匹配".format(field))
                else:
                    print("  ❌ '{}' 不应该匹配但匹配了".format(field))
            
            print()
            
    except ImportError as e:
        print("无法导入swagger_time_parser模块: {}".format(e))

def main():
    """主函数"""
    print("增强版Swagger解析器功能测试")
    print("=" * 60)
    print()
    
    # 测试命令行功能
    test_enhanced_parser()
    
    # 测试模式匹配功能
    test_pattern_matching()
    
    print("测试完成！")

if __name__ == "__main__":
    main()