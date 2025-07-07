#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swagger时间字段解析器的单元测试
"""

import unittest
import json
import tempfile
import os
from swagger_time_parser import SwaggerTimeParser, TimeField, APIInfo


class TestSwaggerTimeParser(unittest.TestCase):
    """SwaggerTimeParser单元测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.parser = SwaggerTimeParser()
        
        # 创建测试用的Swagger数据
        self.test_swagger_data = {
            "swagger": "2.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "basePath": "/api/v1",
            "paths": {
                "/users": {
                    "get": {
                        "summary": "获取用户列表",
                        "parameters": [
                            {
                                "name": "start_time",
                                "in": "query",
                                "type": "string",
                                "description": "开始时间"
                            },
                            {
                                "name": "limit",
                                "in": "query",
                                "type": "integer",
                                "description": "限制数量"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "成功",
                                "schema": {
                                    "$ref": "#/definitions/UserListResponse"
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "创建用户",
                        "parameters": [
                            {
                                "name": "body",
                                "in": "body",
                                "schema": {
                                    "$ref": "#/definitions/CreateUserRequest"
                                }
                            }
                        ],
                        "responses": {
                            "201": {
                                "description": "创建成功",
                                "schema": {
                                    "$ref": "#/definitions/User"
                                }
                            }
                        }
                    }
                },
                "/storage/pools/{pool_id}": {
                    "post": {
                        "summary": "创建存储池",
                        "parameters": [
                            {
                                "name": "pool_id",
                                "in": "path",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "body",
                                "in": "body",
                                "schema": {
                                    "$ref": "#/definitions/StoragePoolReq"
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "成功",
                                "schema": {
                                    "$ref": "#/definitions/StoragePoolResponse"
                                }
                            }
                        }
                    }
                }
            },
            "definitions": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "用户ID"
                        },
                        "name": {
                            "type": "string",
                            "description": "用户名"
                        },
                        "created_time": {
                            "type": "string",
                            "format": "date-time",
                            "description": "创建时间"
                        },
                        "last_login_time": {
                            "type": "string",
                            "format": "date-time",
                            "description": "最后登录时间"
                        }
                    }
                },
                "UserListResponse": {
                    "type": "object",
                    "properties": {
                        "users": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/User"
                            }
                        },
                        "total": {
                            "type": "integer",
                            "description": "总数"
                        },
                        "query_time": {
                            "type": "string",
                            "format": "date-time",
                            "description": "查询时间"
                        }
                    }
                },
                "CreateUserRequest": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "用户名"
                        },
                        "email": {
                            "type": "string",
                            "description": "邮箱"
                        }
                    }
                },
                "StoragePoolReq": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "存储池名称"
                        },
                        "block": {
                            "$ref": "#/definitions/BlockInfo"
                        }
                    }
                },
                "BlockInfo": {
                    "type": "object",
                    "properties": {
                        "size": {
                            "type": "integer",
                            "description": "大小"
                        },
                        "last_check_time": {
                            "type": "string",
                            "format": "date-time",
                            "description": "上次检查时间"
                        },
                        "disk_info": {
                            "type": "string",
                            "description": "从宿主机获取的磁盘信息"
                        }
                    }
                },
                "StoragePoolResponse": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "存储池ID"
                        },
                        "status": {
                            "type": "string",
                            "description": "状态"
                        },
                        "creation_time": {
                            "type": "string",
                            "format": "date-time",
                            "description": "创建时间"
                        }
                    }
                }
            }
        }
    
    def test_parse_swagger_data_basic(self):
        """测试基本的Swagger数据解析"""
        apis = self.parser.parse_swagger_data(self.test_swagger_data)
        
        # 应该找到包含时间字段的API
        self.assertGreater(len(apis), 0)
        
        # 检查是否正确识别了时间字段
        time_field_paths = []
        for api in apis:
            for time_field in api.time_fields:
                time_field_paths.append(time_field.field_path)
        
        # 应该包含这些时间字段
        expected_fields = ['start_time', 'User.created_time', 'User.last_login_time', 
                          'UserListResponse.query_time', 'BlockInfo.last_check_time',
                          'StoragePoolResponse.creation_time']
        
        for expected_field in expected_fields:
            self.assertTrue(any(expected_field in path for path in time_field_paths),
                          "未找到预期的时间字段: {}".format(expected_field))
    
    def test_invalid_swagger_version(self):
        """测试无效的Swagger版本"""
        invalid_data = {"swagger": "3.0.0"}
        
        with self.assertRaises(ValueError) as context:
            self.parser.parse_swagger_data(invalid_data)
        
        self.assertIn("仅支持Swagger 2.0格式", str(context.exception))
    
    def test_parameter_time_fields(self):
        """测试参数中的时间字段识别"""
        apis = self.parser.parse_swagger_data(self.test_swagger_data)
        
        # 找到GET /users API
        get_users_api = None
        for api in apis:
            if api.path == "/api/v1/users" and api.method == "GET":
                get_users_api = api
                break
        
        self.assertIsNotNone(get_users_api, "未找到GET /users API")
        
        # 检查是否找到了start_time参数
        start_time_field = None
        for time_field in get_users_api.time_fields:
            if time_field.field_path == "start_time":
                start_time_field = time_field
                break
        
        self.assertIsNotNone(start_time_field, "未找到start_time参数")
        self.assertEqual(start_time_field.location, "query参数")
        self.assertEqual(start_time_field.field_type, "string")
        self.assertEqual(start_time_field.description, "开始时间")
    
    def test_nested_schema_time_fields(self):
        """测试嵌套schema中的时间字段识别"""
        apis = self.parser.parse_swagger_data(self.test_swagger_data)
        
        # 找到POST /storage/pools/{pool_id} API
        storage_api = None
        for api in apis:
            if "/storage/pools/" in api.path and api.method == "POST":
                storage_api = api
                break
        
        self.assertIsNotNone(storage_api, "未找到存储池API")
        
        # 检查是否找到了嵌套的时间字段
        nested_time_fields = [tf for tf in storage_api.time_fields 
                             if "last_check_time" in tf.field_path]
        
        self.assertGreater(len(nested_time_fields), 0, "未找到嵌套的时间字段")
        
        # 检查字段路径是否正确
        field_paths = [tf.field_path for tf in nested_time_fields]
        self.assertTrue(any("BlockInfo.last_check_time" in path for path in field_paths),
                       "未找到正确的嵌套字段路径")
    
    def test_response_time_fields(self):
        """测试响应中的时间字段识别"""
        apis = self.parser.parse_swagger_data(self.test_swagger_data)
        
        # 检查响应中的时间字段
        response_time_fields = []
        for api in apis:
            for time_field in api.time_fields:
                if "响应体" in time_field.location:
                    response_time_fields.append(time_field)
        
        self.assertGreater(len(response_time_fields), 0, "未找到响应中的时间字段")
    
    def test_generate_markdown_table(self):
        """测试Markdown表格生成"""
        apis = self.parser.parse_swagger_data(self.test_swagger_data)
        markdown_table = self.parser.generate_markdown_table(apis)
        
        # 检查表格格式
        lines = markdown_table.split('\n')
        self.assertGreater(len(lines), 2, "表格行数不足")
        
        # 检查表头
        header = lines[0]
        self.assertIn("服务名", header)
        self.assertIn("API", header)
        self.assertIn("Method", header)
        self.assertIn("API描述", header)
        self.assertIn("时间相关字段", header)
        
        # 检查分隔符
        separator = lines[1]
        self.assertIn("---", separator)
        
        # 检查数据行
        data_lines = lines[2:]
        self.assertGreater(len(data_lines), 0, "没有数据行")
        
        # 检查是否包含预期的API信息
        table_content = markdown_table
        self.assertIn("Test API", table_content)  # 服务名
        self.assertIn("/api/v1/users", table_content)  # API路径
        self.assertIn("GET", table_content)  # HTTP方法
    
    def test_empty_swagger_data(self):
        """测试空的Swagger数据"""
        empty_data = {
            "swagger": "2.0",
            "info": {"title": "Empty API", "version": "1.0.0"},
            "paths": {}
        }
        
        apis = self.parser.parse_swagger_data(empty_data)
        self.assertEqual(len(apis), 0, "空数据应该返回空列表")
        
        markdown_table = self.parser.generate_markdown_table(apis)
        self.assertEqual(markdown_table, "没有找到包含时间字段的API。")
    
    def test_circular_reference_handling(self):
        """测试循环引用处理"""
        circular_data = {
            "swagger": "2.0",
            "info": {"title": "Circular API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "summary": "测试循环引用",
                        "responses": {
                            "200": {
                                "description": "成功",
                                "schema": {
                                    "$ref": "#/definitions/Node"
                                }
                            }
                        }
                    }
                }
            },
            "definitions": {
                "Node": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "create_time": {
                            "type": "string",
                            "description": "创建时间"
                        },
                        "children": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/Node"
                            }
                        }
                    }
                }
            }
        }
        
        # 应该能够处理循环引用而不会无限递归
        apis = self.parser.parse_swagger_data(circular_data)
        self.assertGreater(len(apis), 0, "应该找到包含时间字段的API")
        
        # 检查是否找到了时间字段
        time_fields = []
        for api in apis:
            time_fields.extend(api.time_fields)
        
        self.assertGreater(len(time_fields), 0, "应该找到时间字段")
        
        # 检查字段路径
        field_paths = [tf.field_path for tf in time_fields]
        self.assertTrue(any("create_time" in path for path in field_paths),
                       "应该找到create_time字段")
    
    def test_file_parsing(self):
        """测试文件解析功能"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_swagger_data, f, ensure_ascii=False, indent=2)
            temp_file_path = f.name
        
        try:
            # 测试文件解析
            apis = self.parser.parse_swagger_file(temp_file_path)
            self.assertGreater(len(apis), 0, "从文件解析应该找到API")
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
    
    def test_file_not_found(self):
        """测试文件不存在的情况"""
        with self.assertRaises(ValueError) as context:
            self.parser.parse_swagger_file("nonexistent_file.json")
        
        self.assertIn("无法读取或解析Swagger文件", str(context.exception))
    
    def test_invalid_json_file(self):
        """测试无效JSON文件"""
        # 创建包含无效JSON的临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {")
            temp_file_path = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                self.parser.parse_swagger_file(temp_file_path)
            
            self.assertIn("无法读取或解析Swagger文件", str(context.exception))
        finally:
            os.unlink(temp_file_path)
    
    def test_case_insensitive_time_matching(self):
        """测试大小写不敏感的时间字段匹配"""
        case_test_data = {
            "swagger": "2.0",
            "info": {"title": "Case Test API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "summary": "测试大小写",
                        "parameters": [
                            {"name": "startTime", "in": "query", "type": "string"},
                            {"name": "END_TIME", "in": "query", "type": "string"},
                            {"name": "updatetime", "in": "query", "type": "string"},
                            {"name": "TimeStamp", "in": "query", "type": "string"}
                        ],
                        "responses": {"200": {"description": "成功"}}
                    }
                }
            }
        }
        
        apis = self.parser.parse_swagger_data(case_test_data)
        self.assertGreater(len(apis), 0, "应该找到包含时间字段的API")
        
        # 检查所有时间字段都被找到
        time_field_names = [tf.field_path for api in apis for tf in api.time_fields]
        expected_names = ["startTime", "END_TIME", "updatetime", "TimeStamp"]
        
        for expected_name in expected_names:
            self.assertIn(expected_name, time_field_names,
                         "未找到时间字段: {}".format(expected_name))


if __name__ == '__main__':
    unittest.main()