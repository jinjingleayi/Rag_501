# 快速开始指南

## ⚠️ 前置检查

在执行部署前，请确保：

1. ✅ **Terraform 已安装** - 已确认 ✓
2. ❓ **AWS CLI 已安装并配置** - 需要检查
3. ✅ **GitHub 仓库已创建** - https://github.com/jinjingleayi/Rag_501
4. ✅ **OpenAI API Key** - 已设置

---

## 🚀 执行步骤

### 步骤 1: 安装并配置 AWS CLI（如果还没有）

```bash
# macOS 安装 AWS CLI
brew install awscli

# 配置 AWS 凭证
aws configure
```

**需要输入**：
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`
- Default output format: `json`

**如何获取 AWS 凭证**：
1. 登录 AWS Console
2. 进入 IAM > Users > 您的用户名
3. 创建 Access Key
4. 下载并保存凭证

---

### 步骤 2: Push 代码到 GitHub

```bash
cd /Users/jinjingyi/Qishi_AI/Rag_501

# 添加远程仓库（如果还没有）
git remote add origin https://github.com/jinjingleayi/Rag_501.git

# 推送到 main 分支
git branch -M main
git push -u origin main
```

**⚠️ 重要**：
- 在 GitHub 上确保仓库设置为 **Public**
- 第一次 push 后，GitHub Actions 会失败（正常！）

---

### 步骤 3: 运行 Terraform

```bash
cd /Users/jinjingyi/Qishi_AI/Rag_501

# 设置 Terraform 变量
export TF_VAR_manage_apprunner_via_terraform=false
export TF_VAR_github_org_or_user=jinjingleayi
export TF_VAR_github_repo_name=Rag_501
export TF_VAR_openai_api_key="your-openai-api-key-here"

# 初始化 Terraform
terraform init

# 应用配置
terraform apply
```

**⚠️ 重要**：
- 保存所有 Terraform 输出值（用于下一步）

---

### 步骤 4: 配置 GitHub Secrets

访问：https://github.com/jinjingleayi/Rag_501/settings/secrets/actions

添加 6 个 Secrets（使用 Terraform 输出值）

---

### 步骤 5: 再次 Push 触发部署

```bash
git add .
git commit -m "Trigger deployment"
git push
```

---

### 步骤 6: 配置 Cloudflare

1. 获取 App Runner URL（AWS Console）
2. 在 Cloudflare 添加 CNAME 记录

---

## 📝 详细步骤

参考 `STEP_BY_STEP.md` 获取更详细的说明。

