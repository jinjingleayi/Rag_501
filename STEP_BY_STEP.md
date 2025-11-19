# 逐步部署指南

## 📋 执行顺序（重要！）

### 步骤 1️⃣: 初始化 Git 并 Push 到 GitHub（设置为 Public）

**目的**：让 Terraform 知道仓库存在，配置 OIDC

**操作**：
```bash
cd /Users/jinjingyi/Qishi_AI/Rag_501

# 初始化 Git
git init

# 添加所有文件（.gitignore 会自动排除不需要的文件）
git add .

# 提交
git commit -m "Initial commit: RAG app with CI/CD"

# 添加远程仓库
git remote add origin https://github.com/jinjingleayi/Rag_501.git

# 推送到 main 分支
git branch -M main
git push -u origin main
```

**⚠️ 重要**：
- 在 GitHub 上确保仓库设置为 **Public**
- 第一次 push 后，GitHub Actions 会失败（正常，因为还没有配置 Secrets）

---

### 步骤 2️⃣: 运行 Terraform 创建 AWS 基础设施

**目的**：创建所有 AWS 资源（ECR, Secrets Manager, IAM Roles 等）

**前置条件**：
- ✅ GitHub 仓库已存在（步骤1完成）
- ✅ AWS CLI 已配置
- ✅ Terraform 已安装

**操作**：
```bash
cd /Users/jinjingyi/Qishi_AI/Rag_501

# 设置 Terraform 变量
export TF_VAR_manage_apprunner_via_terraform=false
export TF_VAR_github_org_or_user=jinjingleayi
export TF_VAR_github_repo_name=Rag_501
export TF_VAR_openai_api_key="your-openai-api-key-here"

# 初始化 Terraform
terraform init

# 查看将要创建的资源
terraform plan

# 应用配置（创建所有 AWS 资源）
terraform apply
```

**⚠️ 重要**：
- 当提示确认时，输入 `yes`
- **保存所有输出值**（用于步骤3）

**输出值示例**：
```
github_actions_role_arn = "arn:aws:iam::123456789:role/github-actions-deploy-role"
ecr_repository_name = "bee-edu-rag-app"
apprunner_access_role_arn = "arn:aws:iam::123456789:role/bee-edu-apprunner-role"
apprunner_instance_role_arn = "arn:aws:iam::123456789:role/bee-edu-apprunner-instance-role"
```

---

### 步骤 3️⃣: 配置 GitHub Secrets

**目的**：让 GitHub Actions 能够访问 AWS

**前置条件**：
- ✅ Terraform 已完成（步骤2）
- ✅ 已保存所有输出值

**操作**：
1. 访问：https://github.com/jinjingleayi/Rag_501/settings/secrets/actions
2. 点击 **New repository secret**
3. 添加以下 6 个 Secrets：

| Secret 名称 | 值来源 | 示例 |
|------------|--------|------|
| `AWS_REGION` | 固定值 | `us-east-1` |
| `ECR_REPOSITORY` | Terraform output `ecr_repository_name` | `bee-edu-rag-app` |
| `APP_RUNNER_ARN` | Terraform output `apprunner_service_arn` | `arn:aws:apprunner:...`（可能为空） |
| `AWS_IAM_ROLE_TO_ASSUME` | Terraform output `github_actions_role_arn` | `arn:aws:iam::...:role/github-actions-deploy-role` |
| `APP_RUNNER_ACCESS_ROLE_ARN` | Terraform output `apprunner_access_role_arn` | `arn:aws:iam::...:role/bee-edu-apprunner-role` |
| `APP_RUNNER_INSTANCE_ROLE_ARN` | Terraform output `apprunner_instance_role_arn` | `arn:aws:iam::...:role/bee-edu-apprunner-instance-role` |

---

### 步骤 4️⃣: 再次 Push 代码触发部署

**目的**：触发 GitHub Actions 自动部署

**前置条件**：
- ✅ GitHub Secrets 已配置（步骤3）

**操作**：
```bash
# 做一个小的修改（例如更新 README）
echo "# 部署完成" >> README.md

# 提交并推送
git add .
git commit -m "Trigger deployment"
git push
```

**或者**：
- 在 GitHub 上手动触发 Actions：Actions > Deploy to AWS App Runner > Run workflow

---

### 步骤 5️⃣: 获取 App Runner URL 并配置 Cloudflare

**目的**：通过自定义域名访问应用

**前置条件**：
- ✅ 部署成功（步骤4）

**操作 5.1 - 获取 App Runner URL**：
1. 登录 AWS Console
2. 进入 **App Runner** 服务
3. 找到服务 `bee-edu-rag-service`
4. 复制服务 URL（例如：`https://xxxxx.us-east-1.awsapprunner.com`）

**操作 5.2 - 配置 Cloudflare**：
1. 登录 Cloudflare 账户
2. 选择您的域名
3. 进入 **DNS** 设置
4. 添加 **CNAME** 记录：
   - **名称**：`rag`（或您想要的子域名）
   - **目标**：App Runner 的 URL（例如：`xxxxx.us-east-1.awsapprunner.com`）
   - **代理状态**：已代理（橙色云朵）
5. 等待 DNS 传播（通常几分钟）

**最终访问地址**：`https://rag.yourdomain.com`

---

## 🎯 快速检查清单

- [ ] 步骤1：代码已 Push 到 GitHub（Public）
- [ ] 步骤2：Terraform 已运行，所有资源已创建
- [ ] 步骤2：已保存所有 Terraform 输出值
- [ ] 步骤3：已配置 6 个 GitHub Secrets
- [ ] 步骤4：已再次 Push 代码或手动触发 Actions
- [ ] 步骤4：GitHub Actions 部署成功
- [ ] 步骤5：已获取 App Runner URL
- [ ] 步骤5：已配置 Cloudflare CNAME 记录
- [ ] 步骤5：可以通过 Cloudflare URL 访问应用

---

## ⚠️ 常见问题

**Q: 第一次 Push 时 GitHub Actions 失败了，正常吗？**
A: 正常！因为还没有配置 GitHub Secrets。配置 Secrets 后，再次 push 就会成功。

**Q: Terraform 需要多久？**
A: 通常 2-5 分钟，取决于 AWS 资源创建速度。

**Q: GitHub Actions 部署需要多久？**
A: 通常 10-15 分钟（构建镜像 + 部署到 App Runner）。

**Q: Cloudflare DNS 传播需要多久？**
A: 通常几分钟到几小时，取决于 DNS 缓存。

