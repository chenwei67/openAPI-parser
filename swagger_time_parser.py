#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swagger 2.0 JSON文件解析器
用于递归遍历所有请求和响应的结构，找到命名有time子串的字段
"""

import json
import re
# from typing import Dict, List, Any, Tuple, Set  # Python 3.5类型注解支持有限
# from dataclasses import dataclass  # Python 3.5不支持
# from pathlib import Path  # 暂时不需要


class TimeField:
    """时间字段信息"""
    def __init__(self, field_path, field_type, description, location):
        self.field_path = field_path  # 字段路径，如 "StoragePoolReq.Block.LastCheckTime"
        self.field_type = field_type  # 字段类型
        self.description = description  # 字段描述
        self.location = location  # 位置：请求体/响应体/参数等


class APIInfo:
    """API信息"""
    def __init__(self, service_name, path, method, description, time_fields):
        self.service_name = service_name  # 服务名
        self.path = path  # API路径
        self.method = method  # HTTP方法
        self.description = description  # API描述
        self.time_fields = time_fields  # 时间相关字段列表


class SwaggerTimeParser:
    """Swagger 2.0时间字段解析器"""
    
    def __init__(self):
        self.time_pattern = re.compile(r'time', re.IGNORECASE)
        self.apis = []
        self.definitions = {}
        self.visited_refs = set()
    
    def parse_swagger_file(self, file_path):
        """解析Swagger JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                swagger_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError("无法读取或解析Swagger文件: {}".format(e))
        
        return self.parse_swagger_data(swagger_data)
    
    def parse_swagger_data(self, swagger_data):
        """解析Swagger数据"""
        if swagger_data.get('swagger') != '2.0':
            raise ValueError("仅支持Swagger 2.0格式")
        
        self.definitions = swagger_data.get('definitions', {})
        self.apis = []
        
        # 获取服务名（从info.title或basePath推断）
        service_name = swagger_data.get('info', {}).get('title', 'unknown')
        base_path = swagger_data.get('basePath', '')
        
        paths = swagger_data.get('paths', {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    api_info = self._parse_operation(service_name, base_path + path, method, operation)
                    if api_info.time_fields:  # 只保留有时间字段的API
                        self.apis.append(api_info)
        
        return self.apis
    
    def _parse_operation(self, service_name, path, method, operation):
        """解析单个API操作"""
        description = operation.get('summary', operation.get('description', ''))
        time_fields = []
        
        # 重置访问过的引用
        self.visited_refs = set()
        
        # 解析参数
        parameters = operation.get('parameters', [])
        for param in parameters:
            param_time_fields = self._find_time_fields_in_parameter(param)
            time_fields.extend(param_time_fields)
        
        # 解析响应
        responses = operation.get('responses', {})
        for status_code, response in responses.items():
            response_time_fields = self._find_time_fields_in_response(response, status_code)
            time_fields.extend(response_time_fields)
        
        return APIInfo(
            service_name=service_name,
            path=path,
            method=method.upper(),
            description=description,
            time_fields=time_fields
        )
    
    def _find_time_fields_in_parameter(self, param):
        """在参数中查找时间字段"""
        time_fields = []
        param_name = param.get('name', '')
        param_in = param.get('in', '')
        param_type = param.get('type', '')
        description = param.get('description', '')
        
        # 检查参数名是否包含time
        if self.time_pattern.search(param_name):
            location = "{}参数".format(param_in)
            time_fields.append(TimeField(
                field_path=param_name,
                field_type=param_type,
                description=description,
                location=location
            ))
        
        # 如果参数有schema，递归解析
        if 'schema' in param:
            schema_time_fields = self._find_time_fields_in_schema(
                param['schema'], "{}参数".format(param_in), param_name
            )
            time_fields.extend(schema_time_fields)
        
        return time_fields
    
    def _find_time_fields_in_response(self, response, status_code):
        """在响应中查找时间字段"""
        time_fields = []
        
        if 'schema' in response:
            location = "响应体({})".format(status_code)
            schema_time_fields = self._find_time_fields_in_schema(
                response['schema'], location, ""
            )
            time_fields.extend(schema_time_fields)
        
        return time_fields
    
    def _find_time_fields_in_schema(self, schema, location, parent_path=""):
        """在schema中递归查找时间字段"""
        time_fields = []
        
        # 处理$ref引用
        if '$ref' in schema:
            ref_path = schema['$ref']
            if ref_path in self.visited_refs:
                return time_fields  # 避免循环引用
            
            self.visited_refs.add(ref_path)
            
            # 解析引用路径
            if ref_path.startswith('#/definitions/'):
                def_name = ref_path.replace('#/definitions/', '')
                if def_name in self.definitions:
                    ref_schema = self.definitions[def_name]
                    new_parent_path = def_name if not parent_path else "{}.{}".format(parent_path, def_name)
                    ref_time_fields = self._find_time_fields_in_schema(ref_schema, location, new_parent_path)
                    time_fields.extend(ref_time_fields)
            
            self.visited_refs.remove(ref_path)
            return time_fields
        
        # 处理数组类型
        if schema.get('type') == 'array' and 'items' in schema:
            items_time_fields = self._find_time_fields_in_schema(
                schema['items'], location, parent_path
            )
            time_fields.extend(items_time_fields)
        
        # 处理对象类型
        elif schema.get('type') == 'object' or 'properties' in schema:
            properties = schema.get('properties', {})
            for prop_name, prop_schema in properties.items():
                new_path = prop_name if not parent_path else "{}.{}".format(parent_path, prop_name)
                
                # 检查属性名是否包含time
                if self.time_pattern.search(prop_name):
                    prop_type = prop_schema.get('type', 'unknown')
                    prop_description = prop_schema.get('description', '')
                    time_fields.append(TimeField(
                        field_path=new_path,
                        field_type=prop_type,
                        description=prop_description,
                        location=location
                    ))
                
                # 递归处理嵌套属性
                nested_time_fields = self._find_time_fields_in_schema(
                    prop_schema, location, new_path
                )
                time_fields.extend(nested_time_fields)
        
        return time_fields
    
    def generate_markdown_table(self, apis=None):
        """生成Markdown表格"""
        if apis is None:
            apis = self.apis
        
        if not apis:
            return "没有找到包含时间字段的API。"
        
        lines = [
            "| 服务名 | API | Method | API描述 | 时间相关字段 |",
            "| --- | --- | --- | --- | --- |"
        ]
        
        for api in apis:
            for time_field in api.time_fields:
                field_info = "{} {} {}".format(time_field.location, time_field.field_path, time_field.field_type)
                if time_field.description:
                    field_info += " {}".format(time_field.description)
                
                lines.append(
                    "| {} | {} | {} | {} | {} |".format(api.service_name, api.path, api.method, api.description, field_info)
                )
        
        return "\n".join(lines)


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) != 2:
        print("使用方法: python swagger_time_parser.py <swagger_json_file>")
        sys.exit(1)
    
    swagger_file = sys.argv[1]
    
    try:
        parser = SwaggerTimeParser()
        apis = parser.parse_swagger_file(swagger_file)
        markdown_table = parser.generate_markdown_table(apis)
        print(markdown_table)
    except Exception as e:
        print("错误: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()