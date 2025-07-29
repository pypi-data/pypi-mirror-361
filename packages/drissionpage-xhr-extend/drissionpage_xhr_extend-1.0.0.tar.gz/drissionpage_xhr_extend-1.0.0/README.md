# DrissionPage XHR请求封装

这个模块提供了一个便捷的方式来使用DrissionPage的chromium实例执行XHR请求。通过JavaScript的XMLHttpRequest对象进行同步请求，并返回封装的响应对象。

## 功能特性

- ✅ 支持所有HTTP方法 (GET, POST, PUT, DELETE等)
- ✅ 支持表单数据和JSON数据
- ✅ 使用浏览器默认请求头
- ✅ 同步请求执行
- ✅ 完整的错误处理
- ✅ 封装的响应对象
- ✅ 超时控制
- ✅ 面向对象的API设计

## 安装依赖

```bash
pip install DrissionPage
```

## 快速开始

### 基本用法

```python
from DrissionPage import ChromiumPage
from xhr_request import XHRClient

# 创建chromium实例
page = ChromiumPage()

# 创建XHR客户端
client = XHRClient(page)

# 执行GET请求
response = client.get('https://httpbin.org/get')
print(f"状态码: {response.status_code}")
print(f"响应内容: {response.text}")

# 关闭浏览器
page.quit()
```

### POST表单请求

```python
# 表单数据
form_data = {
    'username': 'testuser',
    'password': 'testpass',
    'email': 'test@example.com'
}

response = client.post('https://httpbin.org/post', form_data)
if response.ok:
    print("请求成功!")
    print(response.json)
```

### JSON请求

```python
# JSON数据
json_data = {
    'name': '张三',
    'age': 25,
    'city': '北京'
}

response = client.json_request('POST', 'https://httpbin.org/post', json_data)
print(f"响应: {response.json}")
```

### 使用浏览器默认请求头

```python
# 自动使用浏览器的默认请求头，包括User-Agent、Accept等
response = client.get('https://api.example.com/data')

# 浏览器会自动处理cookies、认证等
response = client.post('https://api.example.com/login', {'user': 'test'})
```

## API文档

### XHRClient类

主要的XHR客户端类，封装了所有请求方法。

```python
class XHRClient:
    def __init__(self, chromium_instance):
        """初始化XHR客户端"""

    def request(self, method: str, url: str, form_data=None, timeout=30000):
        """执行XHR请求"""

    def get(self, url: str, timeout=30000):
        """执行GET请求"""

    def post(self, url: str, form_data=None, timeout=30000):
        """执行POST请求"""

    def json_request(self, method: str, url: str, json_data=None, timeout=30000):
        """执行JSON请求"""
```

**参数说明:**
- `chromium_instance`: DrissionPage的chromium实例
- `method`: HTTP方法 ('GET', 'POST', 'PUT', 'DELETE' 等)
- `url`: 请求的URL
- `form_data`: 表单数据字典 (可选)
- `json_data`: JSON数据字典 (可选)
- `timeout`: 超时时间，单位毫秒 (默认30秒)

**返回:** `XHRResponse` 对象

### XHRResponse对象

响应对象包含以下属性和方法：

```python
class XHRResponse:
    status_code: int        # HTTP状态码
    text: str              # 响应文本
    headers: Dict[str, str] # 响应头
    url: str               # 请求URL
    
    @property
    def json(self) -> Dict[str, Any]:  # 解析为JSON
    
    @property
    def ok(self) -> bool:              # 检查是否成功 (200-299)
```

## 运行测试

```bash
python test_xhr_request.py
```

测试将执行以下操作：
- GET请求测试
- POST表单请求测试
- JSON请求测试
- 自定义请求头测试
- 错误处理测试

## 注意事项

1. **同步请求**: 使用的是同步XHR请求，会阻塞JavaScript执行直到请求完成
2. **浏览器环境**: 需要在有效的浏览器页面环境中执行
3. **CORS限制**: 受到浏览器的同源策略限制
4. **超时设置**: 建议根据实际需求调整超时时间
5. **错误处理**: 请务必使用try-catch处理可能的异常

## 错误处理示例

```python
try:
    client = XHRClient(page)
    response = client.post('https://api.example.com/data', form_data)
    if response.ok:
        data = response.json
        print(f"成功: {data}")
    else:
        print(f"请求失败: {response.status_code}")
except Exception as e:
    print(f"发生错误: {e}")
```

## 高级用法

### 文件上传模拟

虽然XHR不能直接上传文件，但可以模拟表单提交：

```python
# 模拟文件上传表单
form_data = {
    'file_name': 'document.pdf',
    'file_content': 'base64_encoded_content_here',
    'upload_type': 'document'
}

response = client.post('https://api.example.com/upload', form_data)
```

### 会话保持

由于使用的是浏览器环境，cookies会自动保持：

```python
# 登录
login_data = {'username': 'user', 'password': 'pass'}
login_response = client.post('https://site.com/login', login_data)

# 后续请求会自动携带登录cookies
user_data = client.get('https://site.com/profile')
```

## 许可证

MIT License
