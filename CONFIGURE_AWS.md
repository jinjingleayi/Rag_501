# 配置 AWS CLI（使用 IAM 用户）

⚠️ **重要**：不要使用 root 用户创建 access key！AWS 强烈不推荐这样做。

## 步骤 1: 创建 IAM 用户

### 1.1 进入 IAM 控制台

1. 登录 AWS Console: https://console.aws.amazon.com
2. 在搜索栏输入 "IAM"
3. 点击进入 IAM 服务

### 1.2 创建新用户

1. 左侧菜单点击 **Users**
2. 点击 **Create user**
3. 输入用户名（例如：`terraform-admin`）
4. 勾选 **Provide user access to the AWS Management Console**（可选）
5. 点击 **Next**

### 1.3 设置权限

1. 选择 **Attach policies directly**
2. 搜索并勾选 **AdministratorAccess**（用于 Terraform 部署）
3. 点击 **Next**
4. 点击 **Create user**

## 步骤 2: 为 IAM 用户创建 Access Key

### 2.1 进入用户详情

1. 点击刚创建的用户名（例如：`terraform-admin`）

### 2.2 创建访问密钥

1. 点击 **Security credentials** 标签
2. 滚动到 **Access keys** 部分
3. 点击 **Create access key**
4. 选择 **Command Line Interface (CLI)**
5. 勾选确认框
6. 点击 **Next**
7. 添加描述（可选）：`Terraform deployment`
8. 点击 **Create access key**

### 2.3 保存凭证

**重要**：立即复制或下载：
- **Access Key ID**
- **Secret Access Key**（只显示一次！）

## 步骤 3: 配置 AWS CLI

运行以下命令：

```bash
aws configure
```

然后输入：

1. **AWS Access Key ID**: 粘贴你的 Access Key ID
2. **AWS Secret Access Key**: 粘贴你的 Secret Access Key
3. **Default region name**: `us-east-1`
4. **Default output format**: `json`（直接回车）

## 步骤 4: 验证配置

```bash
aws sts get-caller-identity
```

如果显示你的 IAM 用户信息，说明配置成功！

## 为什么不用 root 用户？

- ✅ **安全风险**：root 用户权限太大，一旦泄露后果严重
- ✅ **最佳实践**：AWS 建议永远不要为 root 用户创建 access key
- ✅ **权限管理**：IAM 用户可以精确控制权限
- ✅ **可追踪性**：更容易审计和管理

## 完成！

现在可以安全地使用 Terraform 了。

