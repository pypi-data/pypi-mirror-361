# 自动化小红书MCP服务器

这是一个基于MCP的小红书内容创作和管理工具，可以帮助你自动化小红书内容平台的操作，包括搜索笔记、发布笔记、评论等功能。

## 功能特点

- 🔍 搜索小红书笔记内容
- 📝 发布图文/视频笔记
- 💬 自动评论笔记
- 🏠 获取首页推荐内容
- 🔐 支持账号登录与验证

## 快速开始

### 1. 环境要求
 * node.js
 * python 3.12
 * uv (pip install uv)

### 2. 安装依赖
```sh
git clone https://github.com/fancyboi999/xhs-auto-mcp.git

cd xhs-auto-mcp
uv venv
source .venv/bin/activate
uv pip install -e .
```

### 3. 获取小红书的cookie
[打开网页端小红书](https://www.xiaohongshu.com/explore)
登录后，获取内容平台的cookie，将cookie配置到MCP服务的 XHS_COOKIE 环境变量中
![获取cookie教程](docs/get_cookies.png)

### 4. 配置MCP服务

有两种方式可以配置和启动MCP服务，环境变量JSON_PATH 是用于存储创作平台token与cookie，因此请填写绝对路径：

#### 方式一：使用stdio协议（直接连接）

在Claude配置中添加以下内容：

```json
{
    "mcpServers": {
        "xhs-auto-mcp": {
            "command": "uvx",
            "args": ["xhs-auto-mcp", "--transport", "stdio"],
            "env": {
                "XHS_COOKIE": "xxxx",
                "JSON_PATH": "your_token_save_path"
            }
        }
    }
}
```

#### 方式二：使用HTTP协议

1. 启动HTTP服务：

```sh
env XHS_COOKIE=xxxx JSON_PATH=your_token_save_path uvx xhs-auto-mcp --transport http --port 8080
```

2. 在Claude配置中添加以下内容：

```json
{
    "mcpServers": {
        "xhs-auto-mcp": {
            "type": "http",
            "url": "http://localhost:8080/mcp"
        }
    }
}
```

## 工具使用说明

本项目提供了多种工具来操作小红书平台：

![可用工具](docs/available_tools.png)

### 内容平台工具
- **检查cookie有效性**: 验证当前cookie是否有效
- **获取首页推荐笔记**: 获取小红书首页推荐内容
- **搜索笔记**: 根据关键词搜索笔记
- **获取笔记内容**: 获取指定笔记的详细内容
- **获取笔记评论**: 获取指定笔记的评论
- **发表评论**: 对指定笔记发表评论

### 创作平台工具
- **登录**: 通过手机号和验证码登录小红书创作平台
- **发布图文笔记**: 创建并发布包含图片的笔记
- **发布视频笔记**: 创建并发布包含视频的笔记

## 示例视频

查看演示视频了解如何使用本工具：[演示视频](docs/demo.mp4)

## 免责声明
本项目仅用于学习交流，禁止用于其他用途，任何涉及商业盈利目的均不得使用，否则风险自负。
