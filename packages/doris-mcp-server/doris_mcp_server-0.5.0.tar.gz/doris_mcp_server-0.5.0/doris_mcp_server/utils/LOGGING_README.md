# Doris MCP Server 增强日志系统

## 概述

本项目已升级至增强的日志系统，具备以下特性：

- ✅ **按日志级别分文件存储** - 每个日志级别独立存储到专门的文件中
- ✅ **完整时间戳记录** - 所有日志均包含精确到毫秒的时间戳和行号信息
- ✅ **自动日志轮转** - 支持文件大小限制和备份数量管理
- ✅ **统一日志导入** - 全局一次导入，避免重复导入的代码冗余
- ✅ **审计日志分离** - 独立的审计日志记录系统
- ✅ **系统信息记录** - 自动记录系统环境信息用于调试

## 日志文件结构

```
logs/
├── doris_mcp_server_all.log        # 所有级别的综合日志
├── doris_mcp_server_debug.log      # DEBUG 级别日志
├── doris_mcp_server_info.log       # INFO 级别日志
├── doris_mcp_server_warning.log    # WARNING 级别日志
├── doris_mcp_server_error.log      # ERROR 级别日志
├── doris_mcp_server_critical.log   # CRITICAL 级别日志
└── doris_mcp_server_audit.log      # 审计日志
```

## 日志格式

```
2025-07-10 13:20:14.145 [    INFO] module_name:line_number - log message
```

- **时间戳**: 精确到毫秒的完整时间戳
- **日志级别**: 格式化的日志级别（8字符对齐）
- **模块名称**: 记录日志的模块路径
- **行号**: 记录日志的具体代码行号
- **日志消息**: 实际的日志内容

## 使用方法

### 基本用法

```python
from doris_mcp_server.utils.logger import get_logger

# 获取logger实例
logger = get_logger(__name__)

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("一般信息") 
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 高级配置

```python
from doris_mcp_server.utils.logger import setup_logging

# 自定义配置
setup_logging(
    level="DEBUG",           # 日志级别
    log_dir="custom_logs",   # 自定义日志目录
    enable_console=True,     # 启用控制台输出
    enable_file=True,        # 启用文件输出
    enable_audit=True,       # 启用审计日志
    max_file_size=20*1024*1024,  # 单文件最大20MB
    backup_count=10          # 保留10个备份文件
)
```

### 审计日志

```python
from doris_mcp_server.utils.logger import get_audit_logger

audit_logger = get_audit_logger()
audit_logger.info("用户登录: user_id=123, ip=192.168.1.100")
```

### 系统信息记录

```python
from doris_mcp_server.utils.logger import log_system_info

# 记录系统环境信息，用于调试
log_system_info()
```

## 环境变量配置

```bash
# .env 文件配置
LOG_LEVEL=INFO                              # 日志级别
LOG_FILE_PATH=logs/custom.log               # 自定义日志文件路径
ENABLE_AUDIT=true                           # 启用审计日志
AUDIT_FILE_PATH=logs/audit.log              # 审计日志文件路径
```

## 文件轮转配置

- **默认单文件大小限制**: 10MB
- **默认备份文件数量**: 5个
- **轮转策略**: 当文件达到大小限制时自动轮转
- **备份命名**: `filename.log.1`, `filename.log.2`, 等

## 性能优化

### 全局导入优化

新系统在每个模块顶部统一导入logger，避免了在类构造函数中重复导入：

```python
# ✅ 推荐方式（已实现）
from .logger import get_logger

class MyClass:
    def __init__(self):
        self.logger = get_logger(__name__)
```

```python
# ❌ 避免方式（已修复）
class MyClass:
    def __init__(self):
        from .logger import get_logger  # 避免在方法内重复导入
        self.logger = get_logger(__name__)
```

### 日志级别控制

通过合理设置日志级别来控制日志输出量：

- **生产环境**: 建议使用 `INFO` 或 `WARNING`
- **开发环境**: 可以使用 `DEBUG` 
- **故障排查**: 临时调整为 `DEBUG`

## 故障排查

### 常见问题

1. **日志文件未生成**
   - 检查 `logs` 目录权限
   - 确认日志系统已正确初始化

2. **日志内容为空**
   - 检查日志级别设置
   - 确认日志级别高于配置的最低级别

3. **文件过大**
   - 调整 `max_file_size` 参数
   - 增加 `backup_count` 数量

### 日志级别说明

- **DEBUG**: 详细的调试信息，仅在开发阶段使用
- **INFO**: 一般信息，记录程序正常运行状态
- **WARNING**: 警告信息，程序仍可继续运行但需要注意
- **ERROR**: 错误信息，程序遇到错误但仍可继续运行
- **CRITICAL**: 严重错误，程序可能无法继续运行

## 升级说明

### 从旧系统迁移

原有的日志代码无需修改，系统向下兼容：

```python
# 旧代码仍然有效
import logging
logger = logging.getLogger(__name__)
logger.info("这样的代码仍然可以工作")

# 但推荐升级为新方式
from doris_mcp_server.utils.logger import get_logger
logger = get_logger(__name__)
logger.info("新方式提供更好的功能")
```

### 配置系统集成

新日志系统已与配置系统完全集成，通过 `ConfigManager.setup_logging()` 自动初始化：

```python
from doris_mcp_server.utils.config import DorisConfig, ConfigManager

config = DorisConfig.from_env()
config_manager = ConfigManager(config)
config_manager.setup_logging()  # 自动配置日志系统
```

## 最佳实践

1. **模块级别logger**: 每个模块使用 `get_logger(__name__)` 获取专属logger
2. **合理的日志级别**: 根据信息重要性选择合适的日志级别
3. **结构化日志**: 在重要操作中记录关键参数和结果
4. **性能考虑**: 避免在高频调用的函数中使用DEBUG级别日志
5. **安全考虑**: 不要在日志中记录敏感信息（密码、token等）

## 示例代码

```python
from doris_mcp_server.utils.logger import get_logger

class DatabaseManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        
    async def connect(self, host, port):
        self.logger.info(f"连接数据库: {host}:{port}")
        try:
            # 连接逻辑
            self.logger.info("数据库连接成功")
            return True
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
            return False
            
    async def execute_query(self, sql):
        self.logger.debug(f"执行SQL: {sql}")
        start_time = time.time()
        try:
            # 执行查询
            result = await self._execute(sql)
            execution_time = time.time() - start_time
            self.logger.info(f"查询执行成功，耗时: {execution_time:.3f}s")
            return result
        except Exception as e:
            self.logger.error(f"查询执行失败: {e}")
            raise
``` 