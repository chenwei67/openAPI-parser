#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版Swagger/OpenAPI解析器
支持Swagger 2.0和OpenAPI 3.x格式的JSON文件解析
用于递归遍历所有请求和响应的结构，找到命名有time子串的字段
"""

import json
import re


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


class EnhancedSwaggerParser:
    """增强版Swagger/OpenAPI解析器，支持2.0和3.x版本"""
    
    def __init__(self):
        self.time_pattern = re.compile(r'time', re.IGNORECASE)
        self.apis = []
        self.schemas = {}  # 统一的schema存储，兼容definitions和components/schemas
        self.visited_refs = set()
        self.spec_version = None  # 'swagger2' 或 'openapi3'
    
    def parse_file(self, file_path):
        """解析Swagger/OpenAPI JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError("无法读取或解析文件: {}".format(e))
        
        return self.parse_data(spec_data)
    
    def parse_data(self, spec_data):
        """解析Swagger/OpenAPI数据"""
        # 检测规范版本
        if 'swagger' in spec_data:
            if spec_data.get('swagger') == '2.0':
                self.spec_version = 'swagger2'
                return self._parse_swagger2(spec_data)
            else:
                raise ValueError("不支持的Swagger版本: {}".format(spec_data.get('swagger')))
        elif 'openapi' in spec_data:
            openapi_version = spec_data.get('openapi', '')
            if openapi_version.startswith('3.'):
                self.spec_version = 'openapi3'
                return self._parse_openapi3(spec_data)
            else:
                raise ValueError("不支持的OpenAPI版本: {}".format(openapi_version))
        else:
            raise ValueError("无法识别的API规范格式，缺少swagger或openapi字段")
    
    def _parse_swagger2(self, swagger_data):
        """解析Swagger 2.0格式"""
        self.schemas = swagger_data.get('definitions', {})
        self.apis = []
        
        # 获取服务信息
        service_name = swagger_data.get('info', {}).get('title', 'unknown')
        base_path = swagger_data.get('basePath', '')
        
        paths = swagger_data.get('paths', {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    api_info = self._parse_swagger2_operation(
                        service_name, base_path + path, method, operation
                    )
                    if api_info.time_fields:  # 只保留有时间字段的API
                        self.apis.append(api_info)
        
        return self.apis
    
    def _parse_openapi3(self, openapi_data):
        """解析OpenAPI 3.x格式"""
        # OpenAPI 3.x中schemas在components下
        components = openapi_data.get('components', {})
        self.schemas = components.get('schemas', {})
        self.apis = []
        
        # 获取服务信息
        service_name = openapi_data.get('info', {}).get('title', 'unknown')
        
        # OpenAPI 3.x中servers替代了basePath
        servers = openapi_data.get('servers', [])
        base_url = servers[0].get('url', '') if servers else ''
        
        paths = openapi_data.get('paths', {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    api_info = self._parse_openapi3_operation(
                        service_name, base_url + path, method, operation
                    )
                    if api_info.time_fields:  # 只保留有时间字段的API
                        self.apis.append(api_info)
        
        return self.apis
    
    def _parse_swagger2_operation(self, service_name, path, method, operation):
        """解析Swagger 2.0的单个API操作"""
        description = operation.get('summary', operation.get('description', ''))
        time_fields = []
        
        # 重置访问过的引用
        self.visited_refs = set()
        
        # 解析参数
        parameters = operation.get('parameters', [])
        for param in parameters:
            param_time_fields = self._find_time_fields_in_swagger2_parameter(param)
            time_fields.extend(param_time_fields)
        
        # 解析响应
        responses = operation.get('responses', {})
        for status_code, response in responses.items():
            response_time_fields = self._find_time_fields_in_swagger2_response(response, status_code)
            time_fields.extend(response_time_fields)
        
        return APIInfo(
            service_name=service_name,
            path=path,
            method=method.upper(),
            description=description,
            time_fields=time_fields
        )
    
    def _parse_openapi3_operation(self, service_name, path, method, operation):
        """解析OpenAPI 3.x的单个API操作"""
        description = operation.get('summary', operation.get('description', ''))
        time_fields = []
        
        # 重置访问过的引用
        self.visited_refs = set()
        
        # 解析参数
        parameters = operation.get('parameters', [])
        for param in parameters:
            param_time_fields = self._find_time_fields_in_openapi3_parameter(param)
            time_fields.extend(param_time_fields)
        
        # 解析请求体 (OpenAPI 3.x特有)
        if 'requestBody' in operation:
            request_body = operation['requestBody']
            request_time_fields = self._find_time_fields_in_openapi3_request_body(request_body)
            time_fields.extend(request_time_fields)
        
        # 解析响应
        responses = operation.get('responses', {})
        for status_code, response in responses.items():
            response_time_fields = self._find_time_fields_in_openapi3_response(response, status_code)
            time_fields.extend(response_time_fields)
        
        return APIInfo(
            service_name=service_name,
            path=path,
            method=method.upper(),
            description=description,
            time_fields=time_fields
        )
    
    def _find_time_fields_in_swagger2_parameter(self, param):
        """在Swagger 2.0参数中查找时间字段"""
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
    
    def _find_time_fields_in_openapi3_parameter(self, param):
        """在OpenAPI 3.x参数中查找时间字段"""
        time_fields = []
        param_name = param.get('name', '')
        param_in = param.get('in', '')
        description = param.get('description', '')
        
        # 检查参数名是否包含time
        if self.time_pattern.search(param_name):
            # OpenAPI 3.x中参数类型在schema中
            param_type = 'unknown'
            if 'schema' in param:
                param_type = param['schema'].get('type', 'unknown')
            
            location = "{}参数".format(param_in)
            time_fields.append(TimeField(
                field_path=param_name,
                field_type=param_type,
                description=description,
                location=location
            ))
        
        # 递归解析schema
        if 'schema' in param:
            schema_time_fields = self._find_time_fields_in_schema(
                param['schema'], "{}参数".format(param_in), param_name
            )
            time_fields.extend(schema_time_fields)
        
        return time_fields
    
    def _find_time_fields_in_openapi3_request_body(self, request_body):
        """在OpenAPI 3.x请求体中查找时间字段"""
        time_fields = []
        content = request_body.get('content', {})
        
        for media_type, media_type_obj in content.items():
            if 'schema' in media_type_obj:
                location = "请求体({})".format(media_type)
                schema_time_fields = self._find_time_fields_in_schema(
                    media_type_obj['schema'], location, ""
                )
                time_fields.extend(schema_time_fields)
        
        return time_fields
    
    def _find_time_fields_in_swagger2_response(self, response, status_code):
        """在Swagger 2.0响应中查找时间字段"""
        time_fields = []
        
        if 'schema' in response:
            location = "响应体({})".format(status_code)
            schema_time_fields = self._find_time_fields_in_schema(
                response['schema'], location, ""
            )
            time_fields.extend(schema_time_fields)
        
        return time_fields
    
    def _find_time_fields_in_openapi3_response(self, response, status_code):
        """在OpenAPI 3.x响应中查找时间字段"""
        time_fields = []
        content = response.get('content', {})
        
        for media_type, media_type_obj in content.items():
            if 'schema' in media_type_obj:
                location = "响应体({}, {})".format(status_code, media_type)
                schema_time_fields = self._find_time_fields_in_schema(
                    media_type_obj['schema'], location, ""
                )
                time_fields.extend(schema_time_fields)
        
        return time_fields
    
    def _find_time_fields_in_schema(self, schema, location, parent_path=""):
        """在schema中递归查找时间字段（兼容两种格式）"""
        time_fields = []
        
        # 处理$ref引用
        if '$ref' in schema:
            ref_path = schema['$ref']
            if ref_path in self.visited_refs:
                return time_fields  # 避免循环引用
            
            self.visited_refs.add(ref_path)
            
            # 解析引用路径（兼容两种格式）
            def_name = None
            if ref_path.startswith('#/definitions/'):  # Swagger 2.0
                def_name = ref_path.replace('#/definitions/', '')
            elif ref_path.startswith('#/components/schemas/'):  # OpenAPI 3.x
                def_name = ref_path.replace('#/components/schemas/', '')
            
            if def_name and def_name in self.schemas:
                ref_schema = self.schemas[def_name]
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
        
        # 处理allOf, oneOf, anyOf (主要在OpenAPI 3.x中使用)
        for composition_key in ['allOf', 'oneOf', 'anyOf']:
            if composition_key in schema:
                for sub_schema in schema[composition_key]:
                    composition_time_fields = self._find_time_fields_in_schema(
                        sub_schema, location, parent_path
                    )
                    time_fields.extend(composition_time_fields)
        
        return time_fields
    
    def generate_markdown_table(self, apis=None):
        """生成Markdown表格"""
        if apis is None:
            apis = self.apis
        
        if not apis:
            return "没有找到包含时间字段的API。"
        
        lines = [
            "| 规范版本 | 服务名 | API | Method | API描述 | 时间相关字段 |",
            "| --- | --- | --- | --- | --- | --- |"
        ]
        
        spec_version_display = {
            'swagger2': 'Swagger 2.0',
            'openapi3': 'OpenAPI 3.x'
        }.get(self.spec_version, self.spec_version)
        
        for api in apis:
            for time_field in api.time_fields:
                field_info = "{} {} {}".format(time_field.location, time_field.field_path, time_field.field_type)
                if time_field.description:
                    field_info += " {}".format(time_field.description)
                
                lines.append(
                    "| {} | {} | {} | {} | {} | {} |".format(
                        spec_version_display, api.service_name, api.path, 
                        api.method, api.description, field_info
                    )
                )
        
        return "\n".join(lines)
    
    def get_supported_versions(self):
        """获取支持的API规范版本"""
        return {
            'swagger': ['2.0'],
            'openapi': ['3.0.x', '3.1.x']
        }


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) != 2:
        print("使用方法: python enhanced_swagger_parser.py <api_spec_file>")
        print("支持的格式:")
        print("  - Swagger 2.0")
        print("  - OpenAPI 3.0.x")
        print("  - OpenAPI 3.1.x")
        sys.exit(1)
    
    spec_file = sys.argv[1]
    
    try:
        parser = EnhancedSwaggerParser()
        apis = parser.parse_file(spec_file)
        
        print("检测到的API规范版本: {}".format({
            'swagger2': 'Swagger 2.0',
            'openapi3': 'OpenAPI 3.x'
        }.get(parser.spec_version, parser.spec_version)))
        print("\n找到 {} 个包含时间字段的API\n".format(len(apis)))
        
        markdown_table = parser.generate_markdown_table(apis)
        print(markdown_table)
        
    except Exception as e:
        print("错误: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()