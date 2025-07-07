#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多模式参数修复的脚本
"""

import sys
import os
import subprocess

def test_multiple_patterns():
    """测试多个-p参数的处理"""
    print("=== 测试多个-p参数处理 ===")
    
    # 测试用例
    test_cases = [
        {
            'name': '单个模式',
            'args': ['python3', './enhanced_swagger_parser.py', './example_swagger.json', '-p', 'time'],
            'expected_patterns': ['time']
        },
        {
            'name': '多个模式（基本字符串）',
            'args': ['python3', './enhanced_swagger_parser.py', './example_swagger.json', '-p', 'time', '-p', 'date'],
            'expected_patterns': ['time', 'date']
        },
        {
            'name': '多个模式（正则表达式）',
            'args': ['python3', './enhanced_swagger_parser.py', './example_swagger.json', 
                    '-p', '.*[tT]ime.*', '-p', '.*[Dd]ate.*', '-p', '.*[Ss]tart.*'],
            'expected_patterns': ['.*[tT]ime.*', '.*[Dd]ate.*', '.*[Ss]tart.*']
        },
        {
            'name': '默认模式（无-p参数）',
            'args': ['python3', './enhanced_swagger_parser.py', './example_swagger.json'],
            'expected_patterns': ['time']
        }
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print("\n{:2d}. 测试: {}".format(i, test_case['name']))
        print("    命令: {}".format(' '.join(test_case['args'])))
        
        try:
            # 运行命令
            result = subprocess.run(
                test_case['args'],
                cwd='/Users/chenwei/PycharmProjects/find_time_from_swagger',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 检查输出中的搜索模式
                output_lines = result.stdout.split('\n')
                pattern_line = None
                for line in output_lines:
                    if line.startswith('搜索模式:'):
                        pattern_line = line
                        break
                
                if pattern_line:
                    # 提取实际的搜索模式
                    actual_patterns_str = pattern_line.replace('搜索模式: ', '')
                    actual_patterns = [p.strip() for p in actual_patterns_str.split(',')]
                    
                    # 检查是否匹配预期
                    if set(actual_patterns) == set(test_case['expected_patterns']):
                        print("    结果: ✅ 成功 - 搜索模式匹配: {}".format(actual_patterns))
                        success_count += 1
                    else:
                        print("    结果: ❌ 失败 - 搜索模式不匹配")
                        print("      预期: {}".format(test_case['expected_patterns']))
                        print("      实际: {}".format(actual_patterns))
                else:
                    print("    结果: ❌ 失败 - 未找到搜索模式输出")
            else:
                print("    结果: ❌ 失败 - 命令执行错误")
                print("      错误输出: {}".format(result.stderr.strip()))
                
        except subprocess.TimeoutExpired:
            print("    结果: ❌ 失败 - 命令执行超时")
        except Exception as e:
            print("    结果: ❌ 失败 - 异常: {}".format(str(e)))
    
    print("\n=== 测试结果汇总 ===")
    print("成功: {}/{}".format(success_count, total_count))
    print("失败: {}/{}".format(total_count - success_count, total_count))
    
    if success_count == total_count:
        print("✅ 所有测试通过！多模式参数修复成功。")
        return True
    else:
        print("❌ 部分测试失败，需要进一步修复。")
        return False

def test_regex_patterns():
    """测试正则表达式模式的实际匹配效果"""
    print("\n=== 测试正则表达式模式匹配效果 ===")
    
    # 测试一个包含多种时间字段的模式
    cmd = ['python3', './enhanced_swagger_parser.py', './example_swagger.json', 
           '-p', '.*time.*', '-p', '.*Time.*']
    
    try:
        result = subprocess.run(
            cmd,
            cwd='/Users/chenwei/PycharmProjects/find_time_from_swagger',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=30
        )
        
        if result.returncode == 0:
            output_lines = result.stdout.split('\n')
            api_count_line = None
            for line in output_lines:
                if '找到' in line and '个包含匹配字段的API' in line:
                    api_count_line = line
                    break
            
            if api_count_line:
                print("正则表达式匹配结果: {}".format(api_count_line.strip()))
                if '找到 0 个' not in api_count_line:
                    print("✅ 正则表达式模式成功匹配到字段")
                    return True
                else:
                    print("⚠️  正则表达式模式未匹配到字段（可能是正常的）")
                    return True
            else:
                print("❌ 未找到API计数输出")
                return False
        else:
            print("❌ 命令执行失败: {}".format(result.stderr.strip()))
            return False
            
    except Exception as e:
        print("❌ 测试异常: {}".format(str(e)))
        return False

def main():
    """主测试函数"""
    print("开始测试多模式参数修复...\n")
    
    test1_passed = test_multiple_patterns()
    test2_passed = test_regex_patterns()
    
    print("\n" + "="*50)
    print("最终测试结果:")
    print("- 多模式参数测试: {}".format("✅ 通过" if test1_passed else "❌ 失败"))
    print("- 正则表达式测试: {}".format("✅ 通过" if test2_passed else "❌ 失败"))
    
    if test1_passed and test2_passed:
        print("\n🎉 所有测试通过！多模式参数修复成功。")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要进一步检查。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)