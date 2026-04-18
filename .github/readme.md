# Proxy TTS+STT

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![HA Version](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

一个 Home Assistant 自定义集成，为 TTS（文本转语音）和 STT（语音转文本）服务提供故障自动转移和优先级轮询功能。

## 功能特性

- 🔄 **自动故障转移** — 当某个 TTS/STT 服务失败时，自动切换到下一个可用服务
- 📊 **健康检查** — 每天定时检查所有服务的健康状态，自动恢复已修复的服务
- ⚖️ **优先级轮询** — 按配置的优先级顺序调用服务，支持自定义排序
- ⚙️ **UI 配置** — 通过 Home Assistant 图形化界面配置服务池和参数
- 💾 **状态持久化** — 服务状态和配置自动保存到 Home Assistant 存储

## 安装

### HACS 安装（推荐）

1. 打开 Home Assistant 的 **HACS** 面板
2. 点击 **"集成"** → 右上角 **"+"** 按钮
3. 选择 **"从仓库添加"**
4. 搜索 `tts_stt_proxy` 或粘贴本仓库地址
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
3. 按向导步骤完成配置
