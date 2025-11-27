# AI API 平台免费获取指南

## DeepSeek（推荐，国内友好）
- 官网：https://platform.deepseek.com/
- 注册后赠送免费额度（500万tokens）
- API Key 获取：控制台 → API Keys → 创建新密钥
- .env 配置：
```
AI_API_KEY=sk-xxxxx
AI_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-chat
```

## 通义千问（阿里云）
- 官网：https://dashscope.aliyun.com/
- 新用户赠送免费tokens
- .env 配置：
```
AI_API_KEY=sk-xxxxx
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=qwen-turbo
```

## 智谱AI（清华）
- 官网：https://open.bigmodel.cn/
- 注册赠送免费额度
- .env 配置：
```
AI_API_KEY=xxxxx.xxxxx
AI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
AI_MODEL=glm-4-flash
```

## Moonshot（月之暗面）
- 官网：https://platform.moonshot.cn/
- 新用户赠送免费tokens
- .env 配置：
```
AI_API_KEY=sk-xxxxx
AI_BASE_URL=https://api.moonshot.cn/v1
AI_MODEL=moonshot-v1-8k
```

## OpenAI（需国际信用卡）
- 官网：https://platform.openai.com/
- 新用户赠送 $5 免费额度（有效期3个月）
- .env 配置：
```
AI_API_KEY=sk-xxxxx
AI_BASE_URL=https://api.openai.com
AI_MODEL=gpt-3.5-turbo
```

## 使用建议
1. 优先选择 DeepSeek（国内访问快，免费额度充足）
2. 所有平台均兼容 OpenAI API 格式，脚本已适配
3. 在 .env 中配置 `AI_API_KEY`、`AI_BASE_URL`、`AI_MODEL` 即可切换
4. 若不配置 `AI_BASE_URL`，默认使用 DeepSeek
