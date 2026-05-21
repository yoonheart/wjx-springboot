# 问卷星自动刷题系统带可视化界面

基于 Spring Boot + Python(Selenium) 的问卷星自动填写工具

## 功能

- **问卷解析** — 输入问卷星链接，自动解析所有题型（单选、多选、填空、量表、矩阵、排序等）
- **概率配置** — 为每个选项独立配置分布概率，支持「一键随机概率」
- **配额管理** — 单链接 上限200 份



## 项目结构

```
src/main/java/top/yoonheart/
├── WjxSpringbootApplication.java    # 启动入口
├── config/
│   ├── PythonExecutor.java          # Python 脚本调用引擎
│   └── WebConfig.java               # 静态资源配置
├── controller/
│   ├── HiController.java            # 页面路由
│   ├── AnalysisController.java      # 问卷解析 API
│   └── BrushController.java         # 刷题 API
└── po/
    └── Result.java                  # 统一响应模型

src/main/resources/
├── application.yml
├── scripts/
│   ├── scan.py                      # 问卷解析脚本
│   └── wjx2.py                      # 自动刷题脚本
└── static/
    └── js/                          # 前端 JS 模块
```

## 环境要求

- **JDK 17+**
- **Maven 3.6+**
- **Python 3.x** 并安装依赖：

```bash
pip install selenium beautifulsoup4 numpy requests
```

- **Microsoft Edge 浏览器** + edge浏览器版本对应的 [Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)

> Edge WebDriver 默认路径放在 `D:\python\msedgedriver.exe`，可在 `scan.py` 和 `wjx2.py` 中修改。



## 使用流程

1. 打开首页，粘贴问卷星链接，点击「解析问卷」
2. 在解析结果页为每道题的每个选项配置概率（或使用「一键随机概率」）
3. 点击「开刷」

## 代理 IP 配置

代理 IP 功能启用，需要自行配置 `wjx2.py` 中的 IP 获取 API：

```python
# wjx2.py 第 30 行
api = "api填写处"   # 替换为你的代理 IP 提取 API
```

> 使用的是**三分钟短效 IP**，api填写处是一串申请的链接，可以去浏览器找代理ip，推荐青果网络ip（并非广告)



## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/YoonHeart/wjx-springboot.git
cd wjx-springboot

# 2. 安装 Python 依赖
pip install selenium beautifulsoup4 numpy requests

# 3. 确保 Edge WebDriver 已安装并配置好路径

# 4.确保wjx2.py中的api已替换为你自己申请的三分钟短效ip链接

# 5. 启动 Spring Boot
mvn spring-boot:run

# 6. 浏览器访问 http://localhost:8080
```

