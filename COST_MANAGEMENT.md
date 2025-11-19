# 费用管理指南

## OpenAI API 费用说明

### 当前设置
- 已添加 $5 信用额度
- 需要控制使用以避免超支

### 费用估算

**Embeddings（向量化）**：
- 模型：`text-embedding-ada-002`
- 价格：$0.0001 / 1K tokens
- 数据摄取（一次性）：约 $0.001-0.01（取决于数据量）

**GPT 查询（每次问答）**：
- 模型：`gpt-3.5-turbo`（默认）或 `gpt-4`
- 价格：
  - GPT-3.5-turbo: ~$0.002 / 1K tokens（输入+输出）
  - GPT-4: ~$0.03-0.06 / 1K tokens（更贵）
- 每次问答：约 $0.01-0.05（取决于问题长度）

### 使用限制建议

1. **在 OpenAI 平台设置硬限制**：
   - 访问：https://platform.openai.com/account/billing/limits
   - 设置每月或每日支出限制（例如：$4.50，留 $0.50 缓冲）

2. **监控使用情况**：
   - 访问：https://platform.openai.com/usage
   - 定期检查使用量和费用

3. **代码层面优化**：
   - 使用 GPT-3.5-turbo 而不是 GPT-4（更便宜）
   - 限制每次查询的 token 数量
   - 缓存常见问题的答案

### 预计使用量

**$5 可以支持**：
- 约 100-500 次问答（取决于问题复杂度）
- 或 50-100 次复杂问答

### 当前应用配置

在 `app.py` 中，我们使用的是：
- **Embeddings**: `text-embedding-ada-002`（最便宜的）
- **LLM**: `OpenAI()`（默认 GPT-3.5-turbo，较便宜）

### 如何设置 OpenAI 使用限制

1. 登录 OpenAI Platform: https://platform.openai.com
2. 进入 **Settings** > **Billing** > **Limits**
3. 设置：
   - **Hard limit**: $4.50（留缓冲）
   - **Soft limit**: $4.00（警告阈值）
4. 保存设置

### 监控命令

```bash
# 检查当前使用情况（需要 OpenAI CLI）
openai api usage
```

### 费用优化建议

1. **本地测试时**：
   - 只测试必要的功能
   - 避免重复运行 ingest.py（向量索引已创建，不需要重复）

2. **生产环境**：
   - 考虑使用更便宜的模型
   - 实现查询缓存
   - 限制用户查询频率

3. **开发阶段**：
   - 使用较小的测试数据集
   - 本地测试时使用 mock 数据（可选）

### 紧急停止

如果发现费用异常：
1. 立即在 OpenAI 平台设置硬限制为 $0
2. 暂停应用服务
3. 检查日志找出异常使用原因

### 参考链接

- OpenAI 定价：https://openai.com/pricing
- 使用限制设置：https://platform.openai.com/account/billing/limits
- 使用情况监控：https://platform.openai.com/usage

