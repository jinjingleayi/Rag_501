import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
try:
    # 尝试新版本导入
    from langchain_community.embeddings import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
except ImportError:
    # 回退到旧版本导入
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import FAISS

def ingest_documents():
    """
    读取文档，分割文本，创建嵌入向量，并保存到 FAISS 向量数据库
    """
    # 获取 OpenAI API Key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # 检查数据文件是否存在
    data_file = "data.txt"
    if not os.path.exists(data_file):
        print(f"Warning: {data_file} not found. Creating a sample file...")
        # 创建示例数据文件
        with open(data_file, 'w', encoding='utf-8') as f:
            f.write("""
人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。

机器学习是人工智能的一个子领域，它使计算机能够从数据中学习，而无需明确编程。

深度学习是机器学习的一个子集，它使用神经网络来模拟人脑的工作方式。

自然语言处理（NLP）是人工智能的一个分支，专注于计算机与人类语言之间的交互。

计算机视觉是人工智能的一个领域，使机器能够解释和理解视觉信息。

强化学习是一种机器学习方法，其中智能体通过与环境交互来学习最优行为。

神经网络是受生物神经网络启发的计算模型，由相互连接的节点（神经元）组成。

大数据是指传统数据处理软件无法有效处理的庞大而复杂的数据集。

云计算是通过互联网提供计算服务（包括服务器、存储、数据库、网络、软件）的模型。

容器化是一种操作系统级虚拟化方法，用于部署和运行分布式应用程序。

DevOps 是开发和运维的结合，旨在缩短开发生命周期并提供高质量的持续交付。

CI/CD（持续集成/持续部署）是一种软件开发实践，允许团队频繁地将代码更改集成到共享存储库中。

微服务架构是一种将应用程序构建为小型、独立服务集合的方法。

API（应用程序编程接口）是一组定义和协议，用于构建和集成应用程序软件。

REST（表述性状态传递）是一种用于设计网络应用程序的架构风格。

Docker 是一个用于开发、部署和运行应用程序的开源容器化平台。

Kubernetes 是一个用于自动化容器化应用程序的部署、扩展和管理的开源系统。

AWS（Amazon Web Services）是亚马逊提供的云计算平台。

Terraform 是一个用于构建、更改和版本控制基础设施的开源工具。

Git 是一个分布式版本控制系统，用于跟踪源代码更改。
            """)
        print(f"Sample {data_file} created.")
    
    # 加载文档
    print(f"Loading document from {data_file}...")
    loader = TextLoader(data_file, encoding='utf-8')
    documents = loader.load()
    
    # 分割文本
    print("Splitting documents into chunks...")
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} chunks")
    
    # 创建嵌入向量
    print("Creating embeddings...")
    embeddings = OpenAIEmbeddings()
    
    # 创建向量存储
    print("Creating vector store...")
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    # 保存向量数据库
    print("Saving vector store to faiss_index...")
    vectorstore.save_local("faiss_index")
    print("Ingestion complete! Vector store saved to faiss_index/")
    
    return vectorstore

if __name__ == "__main__":
    ingest_documents()

