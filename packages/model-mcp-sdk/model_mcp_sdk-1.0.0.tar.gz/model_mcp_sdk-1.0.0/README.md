# ModelMcpSDK Python SDK 使用说明文档

## 目录

1. [概述](#概述)
2. [安装与初始化](#安装与初始化)
3. [核心服务](#核心服务)
   - [模型核心服务](#模型核心服务)
   - [后处理服务](#后处理服务)
   - [方案服务](#方案服务)
4. [完整工作流示例](#完整工作流示例)
5. [错误处理](#错误处理)
6. [最佳实践](#最佳实践)
7. [API参考](#api参考)

## 概述

ModelMcpSDK 是一个用于访问 MCP（Model Control Platform）模型的 Python SDK，提供以下核心功能：

- **模型核心服务**：处理 NC 文件格式的转换
- **后处理服务**：获取和处理模型计算结果
- **方案服务**：管理模型方案和执行工作流

## 安装与初始化

### 安装

```bash
pip install model-mcp-sdk
```

### 初始化 SDK

```python
from model_mcp_sdk import ModelMcpSDK

# 配置参数
BASE_URL = "http://gateway.yrihr.com"
APP_KEY = "your_app_key"
APP_SECRET = "your_app_secret"

# 初始化 SDK
sdk = ModelMcpSDK(BASE_URL, APP_KEY, APP_SECRET)
```

## 核心服务

### 模型核心服务

#### 将 NC 文件转换为 JSON 结构

```python
from model_mcp_sdk import ReadNcRequest

# 创建读取 NC 文件的请求
read_nc_request = ReadNcRequest(file_path="/path/to/your/file.nc")

# 调用 NC 转 JSON 方法
nc_info = sdk.model_cores().nc_to_json(read_nc_request)

# 打印结果
print("NC 文件信息:", nc_info)
```

### 后处理服务

#### 获取方案的最新成果模型元素

```python
SCHEME_ID = "your_scheme_id"

# 获取最新成果模型元素
latest_achievements = sdk.postprocess().get_latest_achievements_by_scheme_id(SCHEME_ID)

# 遍历成果模型元素
for achievement in latest_achievements:
    print("成果模型:", achievement.node_name)
    for letter_item in achievement.letter_list:
        print(" - 字母项:", letter_item.letter_name)
```

#### 获取成果完整数据

```python
from model_mcp_sdk import GetIndexRequestVO

# 创建获取指标请求
get_index_request = GetIndexRequestVO(
    instance_id="your_instance_id",
    letter_name="A",
    model_core_id="your_model_core_id",
    scheme_id=SCHEME_ID
)

# 获取成果完整数据
achievements = sdk.postprocess().get_achievements_full_data(get_index_request)

# 处理成果数据
for achievement in achievements:
    print("成果指标:", achievement.index_name, "值:", achievement.value)
```

### 方案服务

#### 获取 NC 模型信息架构

```python
SCHEME_ID = "your_scheme_id"
PARAM_KEY = "your_param_key"

# 获取 NC 模型信息架构
nc_info_schema = sdk.scheme_service().get_nc_info_schema_by_scheme_id(SCHEME_ID, PARAM_KEY)

# 打印结构信息
print("NC 模型架构:", nc_info_schema)
```

#### 写入 NC 文件

```python
from datetime import datetime, timedelta

# 准备数据
rainfall = ["0.1", "0.2", "0.3", "0.4", "0.5"]
begin = datetime.now()
end = begin + timedelta(hours=5)

# 更新模型架构数据
for variable in nc_info_schema.variables_list:
    if variable.name == "PA":  # 降雨量变量
        variable.array_value = rainfall

for attr in nc_info_schema.global_list:
    if attr.name == "BGTM":  # 开始时间
        attr.value = begin.strftime("%Y-%m-%d %H:%M:%S")
    elif attr.name == "EDTM":  # 结束时间
        attr.value = end.strftime("%Y-%m-%d %H:%M:%S")

for dim in nc_info_schema.dimensions_list:
    if dim.name == "TM":  # 时间维度
        dim.value = 5

# 写入 NC 文件
write_result = sdk.scheme_service().write_nc_file_with_nc_info([nc_info_schema])
print("写入结果:", write_result.file_path)
```

#### 执行 Argo 服务工作流

```python
from model_mcp_sdk import ExeArgoServiceReqVO, KeyValueItem

# 创建执行请求
exe_argo_req = ExeArgoServiceReqVO()
exe_argo_req.key = "your_instance_key"
exe_argo_req.call_back_url = "your_callback_url"

# 添加数据
for nc_file in write_result.file_list:
    key_value = KeyValueItem()
    key_value.key = "your_parameter_key"  # 与实际参数对应
    key_value.value = nc_file.file_path
    exe_argo_req.data.append(key_value)

# 执行服务
exec_res = sdk.scheme_service().exec_scheme_service(SCHEME_ID, exe_argo_req)
print("工作流执行结果:", exec_res.instance_id)
```

## 完整工作流示例

```python
def full_workflow_example():
    # 初始化 SDK
    sdk = ModelMcpSDK(BASE_URL, APP_KEY, APP_SECRET)
    
    # 1. 获取 NC 模型架构
    nc_schema = sdk.scheme_service().get_nc_info_schema_by_scheme_id(SCHEME_ID, PARAM_KEY)
    
    # 2. 填充数据
    # ... (填充数据逻辑)
    
    # 3. 写入 NC 文件
    write_result = sdk.scheme_service().write_nc_file_with_nc_info([nc_schema])
    
    # 4. 执行 Argo 服务工作流
    exe_argo_req = prepare_execution_request(write_result)
    exec_res = sdk.scheme_service().exec_scheme_service(SCHEME_ID, exe_argo_req)
    
    # 5. 处理回调 (模拟)
    process_callback(sdk, exec_res)
    
    # 6. 获取后处理数据
    achievements = sdk.postprocess().get_latest_achievements_by_scheme_id(SCHEME_ID)
    process_achievements(sdk, achievements, exec_res)

def prepare_execution_request(write_result):
    # ... (准备执行请求)
    
def process_callback(sdk, exec_res):
    # ... (处理回调逻辑)
    
def process_achievements(sdk, achievements, exec_res):
    # ... (处理成果数据)
```

## 错误处理

SDK 方法可能抛出以下异常：

1. **ConnectionError**：网络连接问题
2. **AuthenticationError**：认证失败
3. **ApiError**：API 返回错误
4. **ValidationError**：参数验证失败

```python
try:
    nc_info = sdk.model_cores().nc_to_json(read_nc_request)
except ConnectionError as e:
    print("网络连接错误:", e)
except AuthenticationError as e:
    print("认证失败:", e)
    # 尝试刷新令牌
    sdk.token().refresh_token()
    # 重试操作
    nc_info = sdk.model_cores().nc_to_json(read_nc_request)
except ApiError as e:
    print("API 错误:", e.response.status_code, e.response.text)
except ValidationError as e:
    print("参数验证失败:", e)
```

## 最佳实践

1. **令牌管理**：
   ```python
   # 手动刷新令牌
   sdk.token().refresh_token()
   
   # 获取当前令牌
   token = sdk.token().get_current_token()
   ```

2. **批量处理**：
   ```python
   # 批量写入多个 NC 文件
   nc_info_list = [nc_info1, nc_info2, nc_info3]
   write_result = sdk.scheme_service().write_nc_file_with_nc_info(nc_info_list)
   ```

3. **异步处理**：
   ```python
   import threading
   
   # 异步执行长时间操作
   def async_nc_to_json():
       try:
           nc_info = sdk.model_cores().nc_to_json(read_nc_request)
           # 处理结果...
       except Exception as e:
           # 错误处理...
   
   thread = threading.Thread(target=async_nc_to_json)
   thread.start()
   ```

4. **数据缓存**：
   ```python
   from cachetools import cached, TTLCache
   
   # 缓存方案数据 (10分钟有效)
   scheme_cache = TTLCache(maxsize=100, ttl=600)
   
   @cached(scheme_cache)
   def get_cached_scheme(scheme_id):
       return sdk.scheme_service().get_nc_info_schema_by_scheme_id(scheme_id, PARAM_KEY)
   ```

## API参考

### ModelMcpSDK

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `model_cores()` | 获取模型核心服务 | `ModelCoresService` |
| `postprocess()` | 获取后处理服务 | `PostprocessService` |
| `scheme_service()` | 获取方案服务 | `SchemeServiceService` |
| `token()` | 获取令牌服务 | `TokenService` |

### ModelCoresService

| 方法 | 描述 | 参数 | 返回类型 |
|------|------|------|----------|
| `nc_to_json(request)` | 将 NC 文件转换为 JSON 结构 | `ReadNcRequest` | `NcInfo` |

### PostprocessService

| 方法 | 描述 | 参数 | 返回类型 |
|------|------|------|----------|
| `get_latest_achievements_by_scheme_id(scheme_id)` | 获取最新成果模型元素 | `scheme_id: str` | `List[ShowSchemeModelElementVO]` |
| `get_achievements_full_data(request)` | 获取成果完整数据 | `GetIndexRequestVO` | `List[BaseAchievements]` |
| `get_achievements_details(request)` | 获取成果详情 | `GetAchivementDetailRequestVO` | `List[Dict]` |

### SchemeServiceService

| 方法 | 描述 | 参数 | 返回类型 |
|------|------|------|----------|
| `get_nc_info_schema_by_scheme_id(scheme_id, key)` | 获取 NC 模型信息架构 | `scheme_id: str`, `key: str` | `NcInfo` |
| `write_nc_file_with_nc_info(nc_info_list)` | 写入 NC 文件 | `List[NcInfo]` | `WriteNcFileRspVO` |
| `exec_scheme_service(scheme_id, request)` | 执行方案服务 | `scheme_id: str`, `ExeArgoServiceReqVO` | `ExeArgoServiceWorkflowResVO` |

### TokenService

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `get_headers()` | 获取认证头信息 | `Dict[str, str]` |
| `refresh_token()` | 刷新认证令牌 | `None` |
| `get_current_token()` | 获取当前令牌 | `str` |

---

本使用说明文档提供了 ModelMcpSDK 的基本用法和核心功能。更多详细信息和高级用法，请参考 SDK 的源代码和 API 文档。