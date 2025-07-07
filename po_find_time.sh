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

# 检查是否提供了文件或目录参数
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <file1|dir1> [file2|dir2 ...]"
    echo "Supports both files and directories (recursive search)"
    exit 1
fi

# 构建不区分大小写的grep选项
GREP_OPTIONS="-i -E"

# 构建完整的grep模式
PATTERN=$(build_pattern)

# 搜索文件的函数
search_file() {
    local file="$1"
    echo "Searching in $file:"
    grep $GREP_OPTIONS "$PATTERN" "$file"
}

# 递归搜索目录的函数
search_directory() {
    local dir="$1"
    echo "Searching in directory: $dir"
    
    # 使用find命令递归查找所有文件
    find "$dir" -type f -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.txt" -o -name "*.md" | while read -r file; do
        if [[ -r "$file" ]]; then
            search_file "$file"
        fi
    done
}

# 执行搜索命令
for target in "$@"; do
    if [[ -f "$target" ]]; then
        # 如果是文件，直接搜索
        search_file "$target"
    elif [[ -d "$target" ]]; then
        # 如果是目录，递归搜索
        search_directory "$target"
    else
        echo "Warning: $target is neither a regular file nor a directory, skipping"
        continue
    fi
done