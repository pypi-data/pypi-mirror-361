# Claude AI 助手记忆 - Anki 插件开发

本文档为 Claude AI 提供专业的 Anki 插件开发指导和项目上下文信息。

### 开发优先级

1. **产品设计卓越**: 优化用户体验和插件设计
2. **代码质量**: 通过 TDD、类型化和现代模式保持高标准
3. **Anki 生态系统兼容性**: 遵循 Anki 宿主环境约定
4. **性能**: 使用后台操作和高效数据处理
5. **可维护性**: 编写干净、文档良好、可测试的代码

记住: 这是一个针对 25.06+ 的现代 Anki 插件，采用当前最佳实践和工具。始终优先考虑最新的 Anki 模式而非遗留方法。

## 参考信源优先级

1. **本地源代码**: 检查 `.venv` 下 `anki` 和 `aqt` 源代码
2. **项目文档**: 项目根目录下 `ANKI.md` 中的 API 详解和最佳实践
3. **禁止网络搜索**: 网络内容往往过时，不要参考

## 设计原则

1. **现代 Anki 25.06+**: 针对最新 Anki 版本使用现代 API
2. **类型安全**: 使用现代 Python 3.10+ 注解的完整 mypy 覆盖
3. **仅支持 Qt6**: 通过 aqt.qt 兼容层，无 Qt5 遗留代码，简化架构
4. **基于操作**: 使用 CollectionOp/QueryOp 而非遗留线程
5. **网络-数据库分离**: 严格分离网络请求和数据库操作
6. **测试驱动开发**: 先写测试，后实现功能
7. **类型安全钩子**: 使用 gui_hooks 而非遗留 anki.hooks
8. **src-layout**: 最佳实践项目结构

### 弃用模式 

- **禁止** 使用直接 PyQt6 导入 - 始终使用 `from aqt.qt import *`
- **禁止** 使用遗留 `anki.hooks` - 使用 `gui_hooks` 代替
- **禁止** 使用手动线程 - 使用 `CollectionOp`/`QueryOp`
- **禁止** 在单个函数中混合网络和数据库操作
- **禁止** 使用不返回 `OpChanges` 的旧集合方法
- **禁止** 使用 Qt5 模式 - 此项目仅支持 Qt6
- **禁止** 使用旧式类型提示 (`List`, `Dict`, `Optional`)
- **禁止** 手动复制 UI 文件 - 使用 `aadt ui` 命令
- **禁止** 使用 QRC 文件 - 使用直接文件路径
- **禁止** 使用 pip - 始终使用 uv 命令

## 🎯 项目概述

**目标版本**: Anki 25.06b7+ (buildhash: ad34b76f)  
**开发语言**: Python 3.13+  
**架构**: 现代 Qt6 专用 Anki 插件  
**开发模式**: 测试驱动开发 (TDD)  

## 项目结构

```
your-addon/
├── src/your_module/            # 主 Python 包 (src-layout)
│   ├── __init__.py             # 插件入口点和主要功能
│   ├── resources/              # UI 资源 (从 ui/resources/ 复制)
│   └── ui/                     # 编译的 UI 文件 (.py 从 .ui 转换)
├── ui/                         # UI 源文件
│   ├── designer/               # Qt Designer .ui 文件
│   └── resources/              # UI 资源 (图标、样式等)
├── tests/                      # 测试文件 (TDD 方法)
├── addon.json                  # 插件配置
├── pyproject.toml              # 项目配置和依赖
├── .python-version             # Python 版本规范
├── README.md                   # 插件说明
├── ANKI.md                     # ANKI 核心库详解
└── CLAUDE.md                   # 本文件
```

## 依赖管理

本项目使用单一 `dev` 组包含所有开发依赖：

```bash
# 安装/更新所有开发依赖
uv sync --group dev

# 包含:
# - anki>=25.6                  # Anki 核心库
# - aqt>=25.6                   # Anki 专属 PyQt6 库
# - aadt>=1.1.0                 # 开发工具库
# - mypy>=1.16.1                # 静态类型检查
# - ruff>=0.12.1                # 快速代码检查和格式化
# - pytest>=8.0.0               # 测试框架
```
