# 本地测试指南

## 前置要求

1. **Python 3.9+** （推荐 3.9 或 3.10）
2. **OpenAI API Key** （如果没有，去 https://platform.openai.com/api-keys 申请）

## 测试步骤

### 步骤 1: 创建 Python 虚拟环境（推荐）

```bash
# 进入项目目录
cd /Users/jinjingyi/Qishi_AI/Rag_501

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 你会看到命令提示符前面有 (venv)
```

### 步骤 2: 安装依赖包

```bash
# 确保虚拟环境已激活
pip install --upgrade pip
pip install -r requirements.txt
```

**注意**：如果安装过程中遇到错误，可能需要安装系统依赖：
```bash
# macOS
brew install cmake

# 或者如果遇到问题，可以尝试只安装核心依赖
pip install flask langchain==0.0.350 openai==0.28.1 faiss-cpu==1.7.4
```

### 步骤 3: 设置 OpenAI API Key

```bash
# 设置环境变量（临时，只在当前终端有效）
export OPENAI_API_KEY="your-openai-api-key-here"

# 验证是否设置成功
echo $OPENAI_API_KEY
```

**重要**：将 `your-openai-api-key-here` 替换为你的真实 OpenAI API Key

### 步骤 4: 运行数据摄取（创建向量索引）

```bash
# 确保 OPENAI_API_KEY 已设置
python ingest.py
```

**预期输出**：
```
Loading document from data.txt...
Splitting documents into chunks...
Split into X chunks
Creating embeddings...
Creating vector store...
Saving vector store to faiss_index...
Ingestion complete! Vector store saved to faiss_index/
```

**如果成功**：会创建一个 `faiss_index/` 文件夹

### 步骤 5: 启动 Flask 应用

```bash
# 确保 OPENAI_API_KEY 已设置
python app.py
```

**预期输出**：
```
RAG system initialized successfully
 * Serving Flask app 'app'
 * Running on http://0.0.0.0:8080
```

### 步骤 6: 测试应用

1. **打开浏览器**，访问：http://localhost:8080
2. **在输入框中输入问题**，例如：
   - "什么是人工智能？"
   - "什么是 RAG？"
   - "什么是 Docker？"
3. **点击"提交问题"**
4. **查看答案**

### 步骤 7: 测试 API（可选）

你也可以直接测试 API：

```bash
# 在另一个终端窗口
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是人工智能？"}'
```

## 常见问题

### 问题 1: `ModuleNotFoundError: No module named 'xxx'`

**解决**：
```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

### 问题 2: `Error: OpenAI API Key not found`

**解决**：
```bash
# 检查环境变量
echo $OPENAI_API_KEY

# 如果没有输出，重新设置
export OPENAI_API_KEY="your-api-key"
```

### 问题 3: `Error: No such file or directory: 'data.txt'`

**解决**：
```bash
# 确保在项目根目录
pwd
# 应该显示 /Users/jinjingyi/Qishi_AI/Rag_501

# 检查文件是否存在
ls -la data.txt
```

### 问题 4: `faiss_index` 文件夹不存在

**解决**：
```bash
# 重新运行 ingest.py
python ingest.py
```

### 问题 5: 端口 8080 已被占用

**解决**：
```bash
# 查找占用端口的进程
lsof -i :8080

# 杀死进程（替换 PID 为实际进程号）
kill -9 <PID>

# 或者修改 app.py 中的端口号
```

## 验证清单

- [ ] Python 3.9+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖包已安装
- [ ] OpenAI API Key 已设置
- [ ] `ingest.py` 运行成功，生成了 `faiss_index/` 文件夹
- [ ] `app.py` 启动成功，显示 "Running on http://0.0.0.0:8080"
- [ ] 浏览器可以访问 http://localhost:8080
- [ ] 可以正常提问并获得答案

## 下一步

如果本地测试成功，就可以继续：
1. 使用 Terraform 创建 AWS 基础设施
2. 配置 GitHub Secrets
3. 推送代码到 GitHub
4. 等待自动部署

参考 `DEPLOYMENT_STEPS.md` 了解详细部署步骤。

