# CodeBuddy Skills

CodeBuddy Code专用skills库，包含扩展和优化工作流的专业技能模块。

## 📦 可用Skills

### github-workflows-guide
全面的GitHub Actions CI/CD工作流指南，包括工作流设计、性能优化、故障排查和可复用模板。

**功能特性：**
- ✅ GitHub Actions工作流设计和最佳实践
- ✅ 12个生产级工作流模板（Node.js、Python、Docker、部署等）
- ✅ 性能优化和成本控制策略
- ✅ 故障诊断和调试指南
- ✅ 自动化分析工具（analyze_workflows.py）

**使用场景：**
- 创建新的GitHub Actions工作流
- 分析和优化CI/CD流水线
- 故障排查和工作流失败诊断
- 实现新的自动化任务

**快速开始：**
```bash
/plugin marketplace add YyZz-wy/codebuddy-skills
```

## 🚀 安装Skills

### 方法1：通过Plugin命令（推荐）
```bash
/plugin marketplace add YyZz-wy/codebuddy-skills
```

### 方法2：通过GitHub URL
```bash
/plugin marketplace add https://github.com/YyZz-wy/codebuddy-skills
```

## 📁 仓库结构

```
codebuddy-skills/
├── README.md                          # 本文件
├── marketplace.json                   # Marketplace配置
└── skills/
    └── github-workflows-guide/        # GitHub工作流skill
        ├── SKILL.md                   # 主要文档
        ├── references/                # 参考文档
        ├── scripts/                   # 可执行脚本
        └── assets/                    # 模板和资源
```

## 📖 Marketplace配置

仓库包含 `marketplace.json` 配置文件，用于CodeBuddy Code的plugin系统自动识别和安装skills。

## 🔧 开发指南

### 添加新的Skill
1. 在 `skills/` 目录下创建新的skill文件夹
2. 按照CodeBuddy Skill标准结构组织文件
3. 在 `marketplace.json` 中注册新skill
4. 提交PR或更新

### Skill标准结构
```
skill-name/
├── SKILL.md              # 必需：skill元数据和文档
├── scripts/              # 可选：可执行脚本
├── references/           # 可选：参考文档
└── assets/               # 可选：模板和资源
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这些skills！

## 📞 支持
- 🐛 [报告问题](https://github.com/YyZz-wy/codebuddy-skills/issues)
- 💬 [讨论](https://github.com/YyZz-wy/codebuddy-skills/discussions)
