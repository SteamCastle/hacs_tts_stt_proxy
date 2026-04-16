# HACS TTS/STT Proxy

一个 Home Assistant 自定义集成，为 TTS（文本转语音）和 STT（语音转文本）服务提供故障自动转移和优先级轮询功能。

## 功能特性

- 🔄 **自动故障转移** — 当某个 TTS/STT 服务失败时，自动切换到下一个可用服务
- 📊 **健康检查** — 每天定时检查所有服务的健康状态，自动恢复已修复的服务
- ⚖️ **优先级轮询** — 按配置的优先级顺序调用服务，支持自定义排序
- ⚙️ **UI 配置** — 通过 Home Assistant 图形化界面配置服务池和参数
- 💾 **状态持久化** — 服务状态和配置自动保存到 Home Assistant 存储

## 虚拟实体

集成创建两个虚拟实体供其他组件调用：

| 实体 | 类型 | 说明 |
|------|------|------|
| `tts.proxy_tts` | TTS | 代理 TTS 服务，自动选择可用的后端 |
| `stt.proxy_stt` | STT | 代理 STT 服务，自动选择可用的后端 |

## 安装

### HACS 安装（推荐）

1. 打开 Home Assistant 的 **HACS** 面板
2. 点击 **"集成"** → 右上角 **"+"** 按钮
3. 选择 **"从仓库添加"**
4. 搜索 `tts_stt_proxy` 或选择本仓库
5. 点击 **"安装"**
6. 在 Home Assistant 中搜索 `Proxy TTS+STT` 并完成配置

### 手动安装

1. 下载本仓库的 `custom_components/tts_stt_proxy` 目录
2. 复制到 Home Assistant 配置目录下的 `custom_components/` 文件夹
3. 重启 Home Assistant
4. 在 **"集成"** 页面中添加 `Proxy TTS+STT`

## 配置

### 首次配置

1. 在 Home Assistant 中进入 **"设置" → "设备与服务"**
2. 点击 **"添加集成"**，选择 **"Proxy TTS+STT"**
3. 按向导步骤完成配置：

   **步骤 1 — 选择 TTS 服务**
   - 从已安装的 TTS 实体中多选要加入池的服务
   - 选择顺序即为优先级顺序

   **步骤 2 — 选择 STT 服务**
   - 从已安装的 STT 实体中多选要加入池的服务
   - 选择顺序即为优先级顺序

   **步骤 3 — 配置参数**
   - 健康检查时间（默认 `02:00`）
   - 失败阈值（默认 `3` 次）
   - 成功阈值（默认 `1` 次）
   - 日志级别（`debug`/`info`/`warning`/`error`）
   - 调用超时（默认 `30` 秒）

### 修改配置

已安装的集成可通过 **"配置"** 按钮修改参数，或在 **"选项"** 中调整：
- 健康检查时间
- 失败/成功阈值
- 日志级别
- 调用超时

注意：添加/删除 TTS 或 STT 服务需要重新添加集成。

## 工作原理

### TTS 调用流程

```
调用 tts.proxy_tts.speak(...)
    ↓
按优先级选择第一个健康的 TTS 服务
    ↓
调用该服务的 speak API（超时 30s）
    ↓
成功 → 重置失败计数 → 返回音频
失败 → 失败计数+1，达到阈值则禁用该服务 → 尝试下一个服务
```

### STT 调用流程

```
调用 stt.proxy_stt.process_audio(...)
    ↓
按优先级选择第一个健康的 STT 服务
    ↓
调用该服务的 process_audio API（超时 30s）
    ↓
成功 → 重置失败计数 → 返回文本
失败 → 失败计数+1，达到阈值则禁用该服务 → 尝试下一个服务
```

### 健康检查流程

每天在配置的时间（默认凌晨 2:00）自动运行：
1. 遍历所有 TTS 和 STT 服务
2. 每个服务最多尝试 3 次
3. 任一成功则恢复启用状态
4. 3 次全部失败则记录失败，达到阈值后禁用

## 配置文件

集成使用 Home Assistant 的存储机制，数据保存在：
```
.storage/tts_stt_proxy/<entry_id>.json
```

```json
{
  "tts_services": [
    {
      "entity_id": "tts.edge_tts",
      "priority": 1,
      "enabled": true,
      "fail_count": 0
    }
  ],
  "stt_services": [
    {
      "entity_id": "stt.whisper_stt",
      "priority": 1,
      "enabled": true,
      "fail_count": 0
    }
  ],
  "health_check_time": "02:00",
  "failure_threshold": 3,
  "success_threshold": 1,
  "log_level": "info",
  "call_timeout": 30
}
```

## 服务

集成注册一个服务用于手动触发健康检查：

### `tts_stt_proxy.trigger_health_check`

手动触发 TTS/STT 服务的健康检查。

| 字段 | 类型 | 说明 |
|------|------|------|
| `service_type` | string | 可选，`"tts"` 或 `"stt"`，不填则检查所有 |
| `entity_id` | string | 可选，指定检查某个实体，不填则检查该类型所有 |

**示例 — 检查所有服务：**
```yaml
service: tts_stt_proxy.trigger_health_check
```

**示例 — 仅检查 TTS 服务：**
```yaml
service: tts_stt_proxy.trigger_health_check
data:
  service_type: tts
```

**示例 — 检查指定实体：**
```yaml
service: tts_stt_proxy.trigger_health_check
data:
  entity_id: tts.edge_tts
```

## 使用示例

### 在自动化中使用

```yaml
automation:
  - alias: "播报欢迎语"
    trigger:
      - platform: state
        entity_id: input_boolean.guest_arrived
    action:
      - service: tts.tts_proxy_speak
        target:
          entity_id: tts.proxy_tts
        data:
          message: "欢迎回家！"
          language: "zh"
```

### 在脚本中使用

```yaml
script:
  announce_weather:
    sequence:
      - service: tts.tts_proxy_speak
        target:
          entity_id: tts.proxy_tts
        data:
          message: "今天天气晴朗，温度 25 度"
```

## 日志

集成日志使用 `tts_stt_proxy` 命名空间，可在 Home Assistant 日志中查看。

| 场景 | 级别 |
|------|------|
| 集成初始化/配置 | info |
| 服务状态变更（启用/禁用） | warning |
| 健康检查开始/结束 | info |
| 单个服务健康检查详情 | debug |
| TTS/STT 调用失败（会重试） | debug |
| 所有服务都不可用 | warning |

可通过配置调整日志级别为 `debug` 以获取更多详情。

## 故障排查

### 没有可用服务

检查是否已在配置中选择了至少一个 TTS/STT 实体。确保这些实体本身在 Home Assistant 中正常工作。

### 健康检查未执行

确认 Home Assistant 正在运行，且集成已正确加载。健康检查任务在集成加载时启动。

### 服务频繁切换

可能是网络不稳定或后端服务响应慢。尝试：
- 增加 `failure_threshold`（如 `5`）
- 增加 `call_timeout`（如 `60`）
- 检查后端服务的实际可用性

## 开发

### 项目结构

```
custom_components/tts_stt_proxy/
├── __init__.py          # 集成入口点
├── manifest.json        # 集成元数据
├── const.py             # 常量定义
├── coordinator.py       # 核心协调器（服务池、健康检查、持久化）
├── tts.py               # TTS 平台设置
├── stt.py               # STT 平台设置
├── tts_entity.py        # TTS 代理实体实现
├── stt_entity.py        # STT 代理实体实现
├── services.py          # 自定义服务注册
└── config_flow.py       # UI 配置流程
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_tts_entity.py
pytest tests/test_stt_entity.py
pytest tests/test_coordinator.py
pytest tests/test_config_flow.py
pytest tests/test_platform.py
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

- 基于 [Home Assistant 自定义集成开发文档](https://developers.home-assistant.io/docs/creating_component_index)
- 设计文档见 `docs/superpowers/specs/`
