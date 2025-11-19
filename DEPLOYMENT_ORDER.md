# 部署顺序说明

## 为什么需要按顺序执行？

### 关键依赖关系：

1. **Terraform 需要知道 GitHub 仓库信息**（用于配置 OIDC）
2. **GitHub Actions 需要 AWS 资源**（ECR, IAM Roles 等）
3. **GitHub Secrets 需要 Terraform 的输出值**
4. **Cloudflare 需要 App Runner URL**

## 正确的执行顺序

### ✅ 步骤 1: 先 Push 代码到 GitHub（设置为 Public）

**为什么先做这个？**
- Terraform 的 OIDC 配置需要知道仓库存在
- 即使第一次 push 时 GitHub Actions 会失败（因为还没有 Secrets），也没关系
- 我们需要仓库存在，Terraform 才能正确配置权限

**操作：**
1. 确保仓库设置为 **Public**
2. Push 所有代码文件

### ✅ 步骤 2: 运行 Terraform 创建 AWS 基础设施

**为什么第二步？**
- 需要 GitHub 仓库已存在（步骤1完成）
- 创建所有 AWS 资源：ECR, Secrets Manager, IAM Roles, OIDC Provider
- 获取输出值用于配置 GitHub Secrets

**操作：**
- 运行 `terraform apply`
- 保存所有输出值

### ✅ 步骤 3: 配置 GitHub Secrets

**为什么第三步？**
- 需要 Terraform 的输出值（步骤2完成）
- GitHub Actions 需要这些 Secrets 才能访问 AWS

**操作：**
- 在 GitHub 仓库中添加 6 个 Secrets
- 使用 Terraform 的输出值

### ✅ 步骤 4: 再次 Push 代码（触发部署）

**为什么第四步？**
- 现在所有配置都完成了
- Push 代码会触发 GitHub Actions
- 这次应该会成功部署

**操作：**
- 可以做一个小的修改并 push
- 或者手动触发 GitHub Actions

### ✅ 步骤 5: 配置 Cloudflare

**为什么最后？**
- 需要 App Runner 的 URL（步骤4完成后才能获取）
- 配置 CNAME 记录指向 App Runner

## 总结

```
1. Push 代码到 GitHub (Public) 
   ↓
2. 运行 Terraform (创建 AWS 资源)
   ↓
3. 配置 GitHub Secrets (使用 Terraform 输出)
   ↓
4. Push 代码触发部署 (GitHub Actions)
   ↓
5. 配置 Cloudflare (使用 App Runner URL)
```

## 注意事项

⚠️ **第一次 Push 时 GitHub Actions 会失败** - 这是正常的！
- 因为还没有配置 GitHub Secrets
- 配置 Secrets 后，再次 push 就会成功

⚠️ **仓库必须是 Public**
- OIDC 配置可能需要 Public 仓库（根据作业要求）
- 或者至少需要正确配置权限

