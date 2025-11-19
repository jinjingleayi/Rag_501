#!/bin/bash

# RAG 应用启动脚本

cd /Users/jinjingyi/Qishi_AI/Rag_501

# 激活虚拟环境
source venv/bin/activate

# 设置 OpenAI API Key（从环境变量读取，如果没有则提示）
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  警告: OPENAI_API_KEY 环境变量未设置"
    echo "请运行: export OPENAI_API_KEY='your-api-key'"
    exit 1
fi

# 检查向量索引是否存在
if [ ! -d "faiss_index" ]; then
    echo "⚠️  向量索引不存在，正在创建..."
    python ingest.py
fi

# 启动应用
echo "🚀 启动 RAG 应用..."
echo "📍 应用地址: http://localhost:8080"
echo "⏹️  按 Ctrl+C 停止应用"
echo ""

python app.py

