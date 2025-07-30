# 自动化小红书MCP服务器




## 快速开始

### 1. 环境
 * node
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
[打开web小红书](https://www.xiaohongshu.com/explore)
登录后，获取cookie，将cookie配置到第4步的 XHS_COOKIE 环境变量中
![cookie](https://raw.githubusercontent.com/jobsonlook/xhs-mcp/master/docs/cookie.png)

### 4. 配置mcp server

```json
{
    "mcpServers": {
        "xhs-auto-mcp": {
            "command": "uvx",
            "args":["xhs-auto-mcp", "--transport", "stdio"]
            "env": {
                "XHS_COOKIE": "xxxx",
                "JSON_PATH": "your_token_save_path"
            }
        }
    }
}
```

## 免责声明
本项目仅用于学习交流，禁止用于其他用途，任何涉及商业盈利目的均不得使用，否则风险自负。
