# 部署步骤详细指南

本文档提供了从零开始部署 RAG 应用的完整步骤。

## 前置要求

1. **AWS 账户**（已配置 AWS CLI）
2. **GitHub 账户**（仓库：https://github.com/jinjingleayi/Rag_501）
3. **OpenAI API Key**
4. **已安装工具**：
   - Terraform (>= 1.0)
   - AWS CLI
   - Git
   - Docker (可选，用于本地测试)

## 步骤 1: 使用 Terraform 创建 AWS 基础设施

### 1.1 配置 Terraform 变量

在项目根目录下，设置以下环境变量：

```bash
export TF_VAR_manage_apprunner_via_terraform=false  # 让 GitHub Actions 创建服务
export TF_VAR_github_org_or_user=jinjingleayi
export TF_VAR_github_repo_name=Rag_501
export TF_VAR_openai_api_key="your-openai-api-key-here"
```

### 1.2 初始化并应用 Terraform

```bash
# 初始化 Terraform
terraform init

# 查看将要创建的资源
terraform plan

# 应用配置（创建所有 AWS 资源）
terraform apply
```

当提示确认时，输入 `yes`。

### 1.3 保存 Terraform 输出值

Terraform 完成后，会输出以下重要值。**请务必保存这些值**：

```bash
# 查看所有输出
terraform output
```

您需要保存以下输出值：

1. `github_actions_role_arn` - 用于 GitHub Secret: `AWS_IAM_ROLE_TO_ASSUME`
2. `ecr_repository_name` - 用于 GitHub Secret: `ECR_REPOSITORY`
3. `apprunner_service_arn` - 用于 GitHub Secret: `APP_RUNNER_ARN`（可能为空，如果服务由 GitHub Actions 创建）
4. `apprunner_access_role_arn` - 用于 GitHub Secret: `APP_RUNNER_ACCESS_ROLE_ARN`
5. `apprunner_instance_role_arn` - 用于 GitHub Secret: `APP_RUNNER_INSTANCE_ROLE_ARN`

## 步骤 2: 配置 GitHub Secrets

1. 访问您的 GitHub 仓库：https://github.com/jinjingleayi/Rag_501
2. 进入 **Settings** > **Secrets and variables** > **Actions**
3. 点击 **New repository secret**
4. 添加以下 6 个 Secrets：

| Secret 名称 | 值来源 | 说明 |
|------------|--------|------|
| `AWS_REGION` | 固定值 | `us-east-1` |
| `ECR_REPOSITORY` | Terraform output | `ecr_repository_name` 的值 |
| `APP_RUNNER_ARN` | Terraform output | `apprunner_service_arn` 的值（如果为空，可以留空） |
| `AWS_IAM_ROLE_TO_ASSUME` | Terraform output | `github_actions_role_arn` 的值 |
| `APP_RUNNER_ACCESS_ROLE_ARN` | Terraform output | `apprunner_access_role_arn` 的值 |
| `APP_RUNNER_INSTANCE_ROLE_ARN` | Terraform output | `apprunner_instance_role_arn` 的值 |

## 步骤 3: 推送代码到 GitHub

```bash
# 如果还没有初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: RAG app with CI/CD"

# 添加远程仓库（如果还没有）
git remote add origin https://github.com/jinjingleayi/Rag_501.git

# 推送到 main 分支（这将触发 GitHub Actions）
git branch -M main
git push -u origin main
```

## 步骤 4: 验证 GitHub Actions 部署

1. 访问 GitHub 仓库的 **Actions** 标签页
2. 查看工作流执行状态
3. 等待所有步骤完成（大约 10-15 分钟）

如果遇到错误：
- 检查 GitHub Secrets 是否正确配置
- 查看 Actions 日志获取详细错误信息
- 确保 Terraform 已成功创建所有资源

## 步骤 5: 获取 App Runner URL

部署完成后，获取 App Runner 服务 URL：

### 方法 1: 通过 AWS Console

1. 登录 AWS Console
2. 进入 **App Runner** 服务
3. 找到服务 `bee-edu-rag-service`
4. 复制服务 URL（格式：`https://xxxxx.us-east-1.awsapprunner.com`）

### 方法 2: 通过 AWS CLI

```bash
aws apprunner list-services --region us-east-1
aws apprunner describe-service --service-arn <SERVICE_ARN> --region us-east-1
```

## 步骤 6: 测试应用

1. 访问 App Runner URL
2. 在网页中输入问题，例如："什么是人工智能？"
3. 验证 RAG 系统是否正常工作

## 步骤 7: 配置 Cloudflare 域名（可选）

1. 登录您的 Cloudflare 账户
2. 选择您的域名
3. 进入 **DNS** 设置
4. 添加 **CNAME** 记录：
   - **名称**：`rag`（或您想要的子域名）
   - **目标**：App Runner 的 URL（例如：`xxxxx.us-east-1.awsapprunner.com`）
   - **代理状态**：已代理（橙色云朵）
5. 等待 DNS 传播（通常几分钟）
6. 访问 `https://rag.yourdomain.com` 测试

## 故障排除

### Terraform 错误

**问题**：`Error: No valid credential sources found`

**解决**：确保 AWS CLI 已配置正确的凭证
```bash
aws configure
```

**问题**：`Error: InvalidParameterException`

**解决**：检查变量是否正确设置，特别是 `github_org_or_user` 和 `github_repo_name`

### GitHub Actions 失败

**问题**：`Error: AccessDenied`

**解决**：
- 检查 GitHub Secrets 是否正确配置
- 验证 IAM 角色权限
- 确保 OIDC 信任关系正确配置

**问题**：`Error: AccessRoleArn is required but not found`

**解决**：确保 `APP_RUNNER_ACCESS_ROLE_ARN` 和 `APP_RUNNER_INSTANCE_ROLE_ARN` 已在 GitHub Secrets 中配置

### App Runner 部署失败

**问题**：服务无法启动

**解决**：
- 检查 Docker 镜像是否成功推送到 ECR
- 验证 Secrets Manager 中的 OpenAI API Key
- 查看 App Runner 服务日志

**问题**：应用返回错误

**解决**：
- 检查健康检查端点：`https://your-url/health`
- 查看应用日志
- 验证 OpenAI API Key 是否正确

### 应用无法访问

**问题**：502 Bad Gateway

**解决**：
- 检查 App Runner 服务状态是否为 "Running"
- 验证端口配置（应为 8080）
- 检查应用日志

## 清理资源

如果需要删除所有 AWS 资源：

```bash
terraform destroy
```

**注意**：这将删除所有通过 Terraform 创建的资源，包括：
- ECR 仓库
- Secrets Manager secret
- IAM 角色和策略
- OIDC 提供商

## 下一步

- 添加更多知识库数据到 `data.txt`
- 优化 RAG 提示模板
- 添加用户认证
- 实现更复杂的查询功能

## 参考资源

- [LangChain 文档](https://python.langchain.com/)
- [AWS App Runner 文档](https://docs.aws.amazon.com/apprunner/)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

