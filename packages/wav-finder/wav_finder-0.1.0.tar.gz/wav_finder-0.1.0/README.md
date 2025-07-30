# WAV Finder

一个简单的Python工具，用于从指定地址（URL或本地路径）中查找WAV文件。

## 功能特性

- 支持从HTTP/HTTPS URL查找WAV文件
- 支持从本地文件系统路径查找WAV文件
- 递归搜索子目录
- 支持多种WAV文件扩展名（.wav, .WAV）
- 提供命令行接口和Python API

## 安装

```bash
pip install wav-finder
```

## 使用方法

### 命令行使用

```bash
# 从URL查找WAV文件
wav-finder https://example.com/audio-files/

# 从本地路径查找WAV文件
wav-finder /path/to/audio/directory

# 显示帮助信息
wav-finder --help
```

### Python API使用

```python
from wav_finder import WavFinder

# 创建WAV查找器实例
finder = WavFinder()

# 从URL查找WAV文件
wav_files = finder.find_wav_files("https://example.com/audio-files/")
print(wav_files)

# 从本地路径查找WAV文件
wav_files = finder.find_wav_files("/path/to/audio/directory")
print(wav_files)
```

## 输出格式

工具会返回一个包含WAV文件路径的列表：

```python
[
    "https://example.com/audio-files/song1.wav",
    "https://example.com/audio-files/song2.wav",
    "/path/to/audio/file3.wav"
]
```

## 依赖

- Python 3.7+
- requests
- beautifulsoup4
- urllib3

## 许可证

MIT License 