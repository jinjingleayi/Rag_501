#!/bin/bash

# 本地测试脚本
# 使用方法: ./test_local.sh

set -e  # 遇到错误立即退出

echo "🚀 开始本地测试..."
echo ""

# 检查 Python
echo "📋 检查 Python 版本..."
python3 --version
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ 依赖安装完成"
echo ""

# 检查 OpenAI API Key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  警告: OPENAI_API_KEY 环境变量未设置"
    echo "请运行: export OPENAI_API_KEY='your-api-key'"
    echo ""
    read -p "是否现在设置 API Key? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入你的 OpenAI API Key: " api_key
        export OPENAI_API_KEY="$api_key"
    else
        echo "❌ 请先设置 OPENAI_API_KEY 后再运行此脚本"
        exit 1
    fi
fi

echo "✅ OpenAI API Key 已设置"
echo ""

# 检查数据文件
if [ ! -f "data.txt" ]; then
    echo "❌ 错误: data.txt 文件不存在"
    exit 1
fi

# 运行数据摄取
echo "📚 运行数据摄取（创建向量索引）..."
python ingest.py
echo "✅ 数据摄取完成"
echo ""

# 检查向量索引
if [ ! -d "faiss_index" ]; then
    echo "❌ 错误: faiss_index 文件夹未创建"
    exit 1
fi

echo "✅ 向量索引已创建"
echo ""

# 启动应用
echo "🌐 启动 Flask 应用..."
echo "应用将在 http://localhost:8080 运行"
echo "按 Ctrl+C 停止应用"
echo ""
echo "=========================================="
echo ""

python app.py

