import os
import boto3
import json
from flask import Flask, request, jsonify, render_template_string

# 使用与已安装版本兼容的导入
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

app = Flask(__name__)

# 从环境变量或 Secrets Manager 获取 OpenAI API Key
def get_openai_api_key():
    # 首先检查环境变量
    api_key = os.getenv('OPENAI_API_KEY')
    
    # 如果环境变量不存在，尝试从 Secrets Manager 获取
    if not api_key:
        try:
            secret_name = "bee-edu-openai-key-secret"
            region_name = os.getenv('AWS_REGION', 'us-east-1')
            
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=region_name
            )
            
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
            # Secrets Manager 返回的 SecretString 可能是字符串或 JSON
            secret_string = get_secret_value_response['SecretString']
            try:
                # 尝试解析为 JSON
                api_key = json.loads(secret_string)
            except json.JSONDecodeError:
                # 如果不是 JSON，直接使用字符串
                api_key = secret_string
        except Exception as e:
            print(f"Error retrieving secret: {e}")
            # 如果 Secrets Manager 也失败，尝试直接读取（用于本地开发）
            api_key = os.getenv('OPENAI_API_KEY')
    
    return api_key

# 初始化 RAG 系统
def init_rag_system():
    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError("OpenAI API Key not found")
    
    os.environ['OPENAI_API_KEY'] = api_key
    
    # 加载向量数据库
    embeddings = OpenAIEmbeddings()
    
    # 检查是否存在 FAISS 索引
    if os.path.exists("faiss_index"):
        vectorstore = FAISS.load_local("faiss_index", embeddings)
    else:
        # 如果索引不存在，创建一个空的向量存储
        # 这通常不应该发生，因为 ingest.py 应该已经创建了索引
        vectorstore = None
        print("Warning: FAISS index not found. Please run ingest.py first.")
    
    # 创建 LLM
    llm = OpenAI(temperature=0)
    
    # 创建提示模板
    prompt_template = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    
    Context: {context}
    
    Question: {question}
    
    Answer:"""
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # 创建检索链
    if vectorstore:
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    else:
        qa_chain = None
    
    return qa_chain

# 全局变量存储 RAG 系统
qa_chain = None

# 初始化函数（在应用启动时调用）
def initialize():
    global qa_chain
    try:
        qa_chain = init_rag_system()
        print("RAG system initialized successfully")
    except Exception as e:
        print(f"Error initializing RAG system: {e}")
        qa_chain = None

# 主页
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>RAG 问答系统</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: bold;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background-color: #45a049;
        }
        .answer {
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-left: 4px solid #4CAF50;
            border-radius: 5px;
        }
        .loading {
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 RAG 问答系统</h1>
        <form id="qaForm">
            <div class="input-group">
                <label for="question">请输入您的问题：</label>
                <input type="text" id="question" name="question" placeholder="例如：什么是人工智能？" required>
            </div>
            <button type="submit">提交问题</button>
        </form>
        <div id="answer" class="answer" style="display:none;"></div>
    </div>
    
    <script>
        document.getElementById('qaForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const question = document.getElementById('question').value;
            const answerDiv = document.getElementById('answer');
            
            answerDiv.style.display = 'block';
            answerDiv.innerHTML = '<div class="loading">正在思考...</div>';
            
            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: question })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    answerDiv.innerHTML = '<p style="color: red;">错误: ' + data.error + '</p>';
                } else {
                    answerDiv.innerHTML = '<h3>答案：</h3><p>' + data.answer + '</p>';
                }
            } catch (error) {
                answerDiv.innerHTML = '<p style="color: red;">请求失败: ' + error.message + '</p>';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# API 端点：查询
@app.route('/api/query', methods=['POST'])
def query():
    global qa_chain
    
    if not qa_chain:
        return jsonify({"error": "RAG system not initialized"}), 500
    
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        # 执行查询
        result = qa_chain({"query": question})
        
        answer = result.get('result', 'No answer found')
        source_documents = result.get('source_documents', [])
        
        return jsonify({
            "answer": answer,
            "sources": [doc.page_content[:100] + "..." for doc in source_documents[:3]]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 健康检查端点
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # 在启动时初始化
    try:
        initialize()
        print("✅ RAG system initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        import traceback
        traceback.print_exc()
        # 即使初始化失败，也启动应用（至少健康检查可以工作）
        qa_chain = None
    
    port = int(os.getenv('PORT', 8080))
    print(f"🚀 Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)

