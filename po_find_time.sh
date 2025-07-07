#!/bin/bash

# 定义时间相关关键词的列表（可根据需要扩展）
TIME_KEYWORDS=("time" "begin" "end" "start" "finish" "duration" "date" "hour" "minute" "second" "clock" "timer" "deadline")

# 将关键词转换为grep兼容的正则表达式模式
# 格式为: %\(.*(keyword).*\)s
build_pattern() {
    local pattern="%\\("
    for ((i=0; i<${#TIME_KEYWORDS[@]}; i++)); do
        if [[ $i -gt 0 ]]; then
            pattern+="|"
        fi
        pattern+=".*${TIME_KEYWORDS[$i]}.*"
    done
    pattern+="\\)s"
    echo "$pattern"
}

# 检查是否提供了文件参数
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <file1> [file2 ...]"
    exit 1
fi

# 构建不区分大小写的grep选项
GREP_OPTIONS="-i -E"

# 构建完整的grep模式
PATTERN=$(build_pattern)

# 执行grep命令
for file in "$@"; do
    if [[ ! -f "$file" ]]; then
        echo "Warning: $file is not a regular file, skipping"
        continue
    fi
    
    echo "Searching in $file:"
    grep $GREP_OPTIONS "$PATTERN" "$file"
done