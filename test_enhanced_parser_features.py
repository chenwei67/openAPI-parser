#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版enhanced_swagger_parser.py的多模式搜索功能
"""

import subprocess
import sys
import os

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def test_enhanced_parser():
    """测试增强版解析器的各种功能"""
    print("=== 测试增强版enhanced_swagger_parser.py功能 ===")
    
    # 检查测试文件是否存在
    test_file = "example_swagger.json"
    if not os.path.exists(test_file):
        print("错误: 测试文件 {} 不存在".format(test_file))
        return False
    
    tests = [
        {
            "name": "默认搜索(time字段)",
            "cmd": "python enhanced_swagger_parser.py {}".format(test_file),
            "expected_patterns": ["time"]
        },
        {
            "name": "多模式搜索(time和date)",
            "cmd": "python enhanced_swagger_parser.py {} -p time date".format(test_file),
            "expected_patterns": ["time", "date"]
        },
        {
            "name": "正则表达式搜索(.*time.*)",
            "cmd": "python enhanced_swagger_parser.py {} -p \".*time.*\"".format(test_file),
            "expected_patterns": [".*time.*"]
        },
        {
            "name": "自定义字段搜索(id和name)",
            "cmd": "python enhanced_swagger_parser.py {} -p id name".format(test_file),
            "expected_patterns": ["id", "name"]
        },
        {
            "name": "帮助信息",
            "cmd": "python enhanced_swagger_parser.py -h",
            "expected_patterns": ["usage", "pattern"]
        }
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for i, test in enumerate(tests, 1):
        print("\n--- 测试 {}/{}: {} ---".format(i, total_tests, test['name']))
        print("命令: {}".format(test['cmd']))
        
        returncode, stdout, stderr = run_command(test['cmd'])
        
        if returncode == 0 or (test['name'] == "帮助信息" and returncode != 0):
            print("✅ 命令执行成功")
            
            # 检查输出是否包含预期的模式
            output = stdout.lower()
            patterns_found = []
            for pattern in test['expected_patterns']:
                if pattern.lower() in output:
                    patterns_found.append(pattern)
            
            if test['name'] == "帮助信息":
                if "usage" in output and "pattern" in output:
                    print("✅ 帮助信息显示正常")
                    success_count += 1
                else:
                    print("❌ 帮助信息不完整")
            else:
                if "搜索模式:" in stdout:
                    print("✅ 搜索模式信息显示正常")
                    success_count += 1
                else:
                    print("❌ 搜索模式信息未显示")
            
            # 显示部分输出
            print("输出预览:")
            lines = stdout.split('\n')[:10]
            for line in lines:
                if line.strip():
                    print("  {}".format(line))
            if len(stdout.split('\n')) > 10:
                print("  ...")
                
        else:
            print("❌ 命令执行失败 (返回码: {})".format(returncode))
            if stderr:
                print("错误信息: {}".format(stderr))
    
    print("\n=== 测试结果: {}/{} 通过 ===".format(success_count, total_tests))
    return success_count == total_tests

def test_pattern_matching():
    """测试模式匹配功能"""
    print("\n=== 测试模式匹配功能 ===")
    
    # 导入解析器进行单元测试
    try:
        from enhanced_swagger_parser import EnhancedSwaggerParser
        
        test_cases = [
            {
                "patterns": ["time"],
                "field_names": ["start_time", "end_time", "timestamp", "date", "id"],
                "expected_matches": ["start_time", "end_time", "timestamp"]
            },
            {
                "patterns": ["time", "date"],
                "field_names": ["start_time", "end_date", "user_id", "creation_date"],
                "expected_matches": ["start_time", "end_date", "creation_date"]
            },
            {
                "patterns": [".*id.*"],
                "field_names": ["user_id", "order_id", "name", "timestamp", "uuid"],
                "expected_matches": ["user_id", "order_id", "uuid"]
            }
        ]
        
        success_count = 0
        for i, test_case in enumerate(test_cases, 1):
            print("\n--- 模式匹配测试 {} ---".format(i))
            print("搜索模式: {}".format(test_case['patterns']))
            print("测试字段: {}".format(test_case['field_names']))
            
            parser = EnhancedSwaggerParser(search_patterns=test_case['patterns'])
            actual_matches = []
            
            for field_name in test_case['field_names']:
                if parser._matches_any_pattern(field_name):
                    actual_matches.append(field_name)
            
            expected = set(test_case['expected_matches'])
            actual = set(actual_matches)
            
            if expected == actual:
                print("✅ 匹配结果正确: {}".format(actual_matches))
                success_count += 1
            else:
                print("❌ 匹配结果错误")
                print("   期望: {}".format(test_case['expected_matches']))
                print("   实际: {}".format(actual_matches))
        
        print("\n模式匹配测试结果: {}/{} 通过".format(success_count, len(test_cases)))
        return success_count == len(test_cases)
        
    except ImportError as e:
        print("❌ 无法导入enhanced_swagger_parser: {}".format(e))
        return False

def main():
    """主函数"""
    print("开始测试增强版enhanced_swagger_parser.py...\n")
    
    # 测试命令行功能
    cli_success = test_enhanced_parser()
    
    # 测试模式匹配功能
    pattern_success = test_pattern_matching()
    
    print("\n" + "="*50)
    if cli_success and pattern_success:
        print("🎉 所有测试通过！增强版解析器功能正常。")
        return 0
    else:
        print("❌ 部分测试失败，请检查代码。")
        return 1

if __name__ == "__main__":
    sys.exit(main())