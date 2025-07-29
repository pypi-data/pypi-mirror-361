# GitCode CLI

基于OpenMind SDK的GitCode平台模型文件上传下载CLI工具

## 简介

GitCode CLI 是一个命令行工具，用于与GitCode平台交互，支持模型和数据集的上传、下载等操作。工具基于OpenMind Hub SDK开发，并配置为连接GitCode API端点。

## 功能特性

- 🔐 用户认证和登录管理
- 📁 支持模型和数据集仓库创建
- ⬆️ 文件和目录批量上传
- ⬇️ 仓库内容下载
- 🎨 彩色终端输出
- 📊 上传下载进度显示
- 🔧 配置文件管理

## 安装

### 从源码安装

```bash
git clone https://gitcode.com/gitcode-ai/gitcode_cli.git
cd gitcode
pip install -e .
```

### 使用pip安装（如果已发布）

```bash
pip install gitcode
```

## 使用方法

### 1. 登录

首先需要登录到GitCode平台：

```bash
gitcode login
```

系统会提示输入访问令牌（从GitCode平台获取）。




### 2. 上传文件

#### 上传模型

```bash
gitcode upload ./your-model-dir --repo-id your-username/your-model-name
```

#### 上传数据集

```bash
gitcode upload ./your-dataset-dir --repo-id your-username/your-dataset-name
```

#### 上传单个文件

```bash
gitcode upload ./model.bin --repo-id your-username/your-model-name
```

### 3. 下载文件

#### 下载到当前目录

```bash
gitcode download your-username/your-model-name
```

#### 下载到指定目录

```bash
gitcode download your-username/your-model-name -d ./models/
```

### 4. 其他命令

#### 查看当前登录用户

```bash
gitcode whoami
```


#### 退出登录

```bash
gitcode logout
```

#### 显示配置信息

```bash
gitcode config-show
```

## 配置文件

配置文件保存在 `~/.gitcode/config.json`，包含用户认证信息和其他设置。

## API端点配置

工具已预配置为连接GitCode平台API端点：
- **API端点**：`https://api.gitcode.com`
- **环境变量**：`OPENMIND_HUB_ENDPOINT=https://api.gitcode.com`

此配置在程序启动时自动设置，用户无需手动配置。

## 错误处理

- 如果遇到网络错误，工具会自动重试
- 上传大文件时会显示进度条
- 所有操作都有详细的错误信息提示

## 支持的文件类型

- 支持所有文件类型的上传和下载
- 自动处理目录结构
- 支持大文件传输

## 开发

### 项目结构

```
gitcode/
├── __init__.py          # 包初始化
├── __main__.py          # 主入口
├── cli.py               # CLI命令定义
├── api.py               # OpenMind API客户端
├── config.py            # 配置管理
├── utils.py             # 工具函数
├── requirements.txt     # 依赖包
├── setup.py             # 包安装配置
└── README.md           # 说明文档
```

### 本地开发

```bash
# 克隆项目
git clone https://gitcode.com/gitcode-ai/gitcode_cli.git
cd gitcode

# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .

# 运行测试
python -m pytest tests/
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系我们

- 邮箱：support@gitcode.com
- 项目地址：https://gitcode.com/gitcode-ai/gitcode_cli
- 问题报告：https://gitcode.com/gitcode-ai/gitcode_cli/issues 