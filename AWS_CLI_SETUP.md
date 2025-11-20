# AWS CLI 快速配置

## 为什么需要 AWS CLI？

Terraform 需要 AWS 凭证来创建资源。AWS CLI 是用来配置这些凭证的工具。

## 快速安装和配置

### 1. 安装 AWS CLI

```bash
brew install awscli
```

### 2. 创建 IAM 用户并获取凭证

⚠️ **不要使用 root 用户！** 应该创建 IAM 用户：

1. 登录 AWS Console，搜索 "IAM"
2. 点击 **Users** → **Create user**
3. 输入用户名（如 `terraform-admin`）
4. 选择 **Attach policies directly** → 勾选 **AdministratorAccess**
5. 创建用户后，进入用户详情 → **Security credentials**
6. 点击 **Create access key** → 选择 **CLI**
7. 保存：
   - **Access Key ID**
   - **Secret Access Key**（只显示一次！）

### 3. 配置 AWS CLI

```bash
aws configure
```

**输入以下信息**：
- **AWS Access Key ID**: 粘贴你的 Access Key ID
- **AWS Secret Access Key**: 粘贴你的 Secret Access Key
- **Default region name**: `us-east-1`
- **Default output format**: `json`（直接回车）

### 4. 验证配置

```bash
aws sts get-caller-identity
```

如果显示你的 AWS 账户信息，说明配置成功！

## 完成！

现在可以运行 Terraform 了。

