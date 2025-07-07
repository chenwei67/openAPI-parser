# Swagger Time Field Parser

这是一个用于解析Swagger 2.0 JSON文件的Python脚本，能够递归遍历请求和响应结构，找到命名中包含"time"子串的字段及其关联的请求，并以Markdown表格形式输出结果。

## 功能特性

- 解析Swagger 2.0 JSON文件
- 递归查找包含"time"子串的字段（不区分大小写）
- 支持参数、请求体、响应体中的时间字段识别
- 处理嵌套schema和引用（$ref）
- 生成格式化的Markdown表格输出
- 防止循环引用导致的无限递归

## 使用方法

### 命令行使用

```bash
python swagger_time_parser.py <swagger_json_file>
```

例如：
```bash
python swagger_time_parser.py example_swagger.json
```

### 编程使用

```python
from swagger_time_parser import SwaggerTimeParser

# 创建解析器实例
parser = SwaggerTimeParser()

# 解析文件
apis = parser.parse_swagger_file('your_swagger_file.json')

# 生成Markdown表格
markdown_table = parser.generate_markdown_table(apis)
print(markdown_table)
```

## 输出格式

脚本会生成包含以下列的Markdown表格：

| 服务名 | API | Method | API描述 | 时间相关字段 |
| --- | --- | --- | --- | --- |
| service_name | /api/path | GET | API描述 | 字段位置 字段名 字段类型 字段描述 |

## 运行测试

```bash
python test_swagger_time_parser.py
```

或者使用unittest模块：

```bash
python -m unittest test_swagger_time_parser.py -v
```

## 系统要求

- Python 3.5+
- 标准库模块：json, re, unittest

## 文件说明

- `swagger_time_parser.py` - 主脚本文件
- `test_swagger_time_parser.py` - 单元测试文件
- `example_swagger.json` - 示例Swagger文件
- `README.md` - 使用说明文档# openAPI-parser
