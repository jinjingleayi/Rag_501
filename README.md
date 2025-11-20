# RAG 问答应用 - 自动化 CI/CD 部署

这是一个基于 LangChain 的 RAG（Retrieval-Augmented Generation）问答应用，通过 GitHub Actions (OIDC) 自动部署到 AWS App Runner。

## 项目结构

```
Rag_501/
├── app.py                 # Flask Web 应用主文件
├── ingest.py              # 数据摄取脚本，创建向量索引
├── data.txt               # 知识库数据文件
├── requirements.txt       # Python 依赖
├── Dockerfile             # Docker 镜像构建文件
├── main.tf                # Terraform 基础设施配置
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Actions CI/CD 工作流
└── README.md              # 本文件
```

## 部署步骤

### 1. 准备工作

确保您已安装：
- [Terraform](https://www.terraform.io/downloads) (>= 1.0)
- [AWS CLI](https://aws.amazon.com/cli/) 并已配置凭证
- [Docker](https://www.docker.com/) (用于本地测试)

### 2. 使用 Terraform 创建 AWS 基础设施

在项目根目录下运行以下命令：

```bash
# 初始化 Terraform
terraform init

# 应用配置（创建所有 AWS 资源）
TF_VAR_manage_apprunner_via_terraform=true \
TF_VAR_github_org_or_user=jinjingleayi \
TF_VAR_github_repo_name=Rag_501 \
TF_VAR_openai_api_key="your-openai-api-key-here" \
terraform apply -auto-approve
```

**重要输出值**：Terraform 会输出以下值，请保存它们：

- `github_actions_role_arn` → 用于 GitHub Secret: `AWS_IAM_ROLE_TO_ASSUME`
- `ecr_repository_name` → 用于 GitHub Secret: `ECR_REPOSITORY`
- `apprunner_service_arn` → 用于 GitHub Secret: `APP_RUNNER_ARN`（如果服务由 GitHub Actions 创建，此值可能为空）
- `apprunner_access_role_arn` → 用于 GitHub Secret: `APP_RUNNER_ACCESS_ROLE_ARN`
- `apprunner_instance_role_arn` → 用于 GitHub Secret: `APP_RUNNER_INSTANCE_ROLE_ARN`

### 3. 配置 GitHub Secrets

在您的 GitHub 仓库 `https://github.com/jinjingleayi/Rag_501` 中：

1. 进入 **Settings** > **Secrets and variables** > **Actions**
2. 点击 **New repository secret**
3. 添加以下 6 个 Secrets：

| Secret 名称 | 值来源 | 示例值 |
|------------|--------|--------|
| `AWS_REGION` | 固定值 | `us-east-1` |
| `ECR_REPOSITORY` | Terraform output `ecr_repository_name` | `bee-edu-rag-app` |
| `APP_RUNNER_ARN` | Terraform output `apprunner_service_arn` | `arn:aws:apprunner:us-east-1:...`（可选，如果服务由 GitHub Actions 创建） |
| `AWS_IAM_ROLE_TO_ASSUME` | Terraform output `github_actions_role_arn` | `arn:aws:iam::...:role/github-actions-deploy-role` |
| `APP_RUNNER_ACCESS_ROLE_ARN` | Terraform output `apprunner_access_role_arn` | `arn:aws:iam::...:role/bee-edu-apprunner-role` |
| `APP_RUNNER_INSTANCE_ROLE_ARN` | Terraform output `apprunner_instance_role_arn` | `arn:aws:iam::...:role/bee-edu-apprunner-instance-role` |

### 4. 推送代码到 GitHub

```bash
# 初始化 Git 仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: RAG app with CI/CD"

# 添加远程仓库
git remote add origin https://github.com/jinjingleayi/Rag_501.git

# 推送到 main 分支（这将触发 GitHub Actions）
git branch -M main
git push -u origin main
```

### 5. 验证部署

1. **检查 GitHub Actions**：
   - 进入仓库的 **Actions** 标签页
   - 查看工作流执行状态
   - 确保所有步骤都成功

2. **获取 App Runner URL**：
   - 登录 AWS Console
   - 进入 App Runner 服务
   - 找到服务 `bee-edu-rag-service`
   - 复制服务 URL（格式：`https://xxxxx.us-east-1.awsapprunner.com`）

3. **测试应用**：
   - 访问 App Runner URL
   - 在网页中输入问题测试 RAG 功能

### 6. Configure Cloudflare Custom Domain (Optional)

To use a custom domain with your App Runner service:

#### Step 1: Add Custom Domain in App Runner

First, you need to associate your custom domain with the App Runner service:

```bash
# Get your service ARN
SERVICE_ARN=$(aws apprunner list-services \
  --region us-east-1 \
  --query "ServiceSummaryList[?ServiceName=='bee-edu-rag-service'].ServiceArn" \
  --output text)

# Associate custom domain
aws apprunner associate-custom-domain \
  --service-arn "$SERVICE_ARN" \
  --domain-name rag.yourdomain.com \
  --region us-east-1
```

This will return DNS validation records that need to be added to Cloudflare.

#### Step 2: Configure DNS in Cloudflare

1. Log in to your Cloudflare account: https://dash.cloudflare.com/
2. Select your domain
3. Go to **DNS** → **Records**
4. Add the main **CNAME** record:
   - **Type**: CNAME
   - **Name**: `rag` (or your desired subdomain)
   - **Target**: Your App Runner URL (e.g., `ugxaymsvp3.us-east-1.awsapprunner.com`)
   - **Proxy status**: ⚪ **DNS only** (gray cloud, **NOT** proxied/orange cloud)
   - Click **Save**

5. Add SSL certificate validation records:
   - App Runner will provide 2-3 CNAME records for SSL certificate validation
   - Add each validation record as a CNAME:
     - **Type**: CNAME
     - **Name**: The validation record name (e.g., `_xxxxx.rag`)
     - **Target**: The validation target (e.g., `_xxxxx.acm-validations.aws.`)
     - **Proxy status**: ⚪ **DNS only** (gray cloud, **required** for validation)
   - These are temporary records for SSL certificate validation

#### Step 3: Wait for SSL Certificate Validation

- Wait 10-30 minutes for AWS to validate the DNS records and issue the SSL certificate
- Check the status:
  ```bash
  aws apprunner describe-custom-domains \
    --service-arn "$SERVICE_ARN" \
    --region us-east-1
  ```
- When status changes to `active`, your custom domain is ready

#### Step 4: Verify Access

Once the domain status is `active`, you can access your application at:
- `https://rag.yourdomain.com`

**Important Notes:**
- Use **DNS only** (gray cloud) for all CNAME records, not Proxied (orange cloud)
- App Runner handles SSL certificates automatically through AWS Certificate Manager
- DNS propagation typically takes 5-15 minutes
- SSL certificate validation may take 10-30 minutes

## 本地开发

### 运行数据摄取

```bash
# 设置 OpenAI API Key
export OPENAI_API_KEY="your-api-key"

# 运行摄取脚本
python ingest.py
```

### 运行应用

```bash
# 设置 OpenAI API Key
export OPENAI_API_KEY="your-api-key"

# 运行 Flask 应用
python app.py
```

应用将在 `http://localhost:8080` 启动。

### 本地 Docker 测试

```bash
# 构建镜像
docker build -t rag-app:local .

# 运行容器
docker run -p 8080:8080 -e OPENAI_API_KEY="your-api-key" rag-app:local
```

## CI/CD 工作流说明

`.github/workflows/deploy.yml` 工作流在每次推送到 `main` 分支时自动执行：

1. **Checkout code**：检出代码
2. **Configure AWS credentials**：使用 OIDC 无密钥认证登录 AWS
3. **Log in to ECR**：登录 Amazon ECR
4. **Build and push Docker image**：构建 Docker 镜像并推送到 ECR
5. **Get App Runner service details**：获取 App Runner 服务配置
6. **Deploy to AWS App Runner**：部署新镜像到 App Runner

## 技术栈

- **后端框架**：Flask
- **AI 框架**：LangChain
- **向量数据库**：FAISS
- **LLM**：OpenAI GPT
- **容器化**：Docker
- **基础设施即代码**：Terraform
- **CI/CD**：GitHub Actions
- **云服务**：AWS (ECR, App Runner, Secrets Manager, IAM)

## 故障排除

### Terraform 错误

- 确保 AWS CLI 已配置正确的凭证
- 检查 Terraform 版本（需要 >= 1.0）
- 确保所有必需的变量都已设置

### GitHub Actions 失败

- 检查所有 GitHub Secrets 是否正确配置
- 验证 IAM 角色权限
- 查看 Actions 日志获取详细错误信息

### App Runner 部署失败

- 检查 Docker 镜像是否成功推送到 ECR
- 验证 Secrets Manager 中的 OpenAI API Key
- 查看 App Runner 服务日志

### 应用无法访问

- 检查 App Runner 服务状态是否为 "Running"
- 验证健康检查端点：`https://your-url/health`
- 检查 Cloudflare DNS 配置

## 许可证

本项目用于教育目的。

## 参考资源

- [LangChain 文档](https://python.langchain.com/)
- [AWS App Runner 文档](https://docs.aws.amazon.com/apprunner/)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

