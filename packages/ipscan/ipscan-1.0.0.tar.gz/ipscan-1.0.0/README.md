# ipscan

快速IP掃描工具 - 多線程 Ping 和 ARP 掃描

## 安裝

```bash
pip install ipscan
```

## 使用方法

### Ping 掃描

```python
from ipscan import ping_range, PingScanner

# 掃描IP範圍
online_hosts = ping_range("192.168.1.1", "192.168.1.254")
print(f"在線主機: {online_hosts}")

# 使用類接口
scanner = PingScanner(timeout=1.0)
results = scanner.scan_range("10.0.0.1", "10.0.0.100")
```

### ARP 掃描

```python
from ipscan import arp_range, ArpScanner

# 掃描IP範圍並獲取MAC地址
host_info = arp_range("192.168.1.1", "192.168.1.254")
for ip, mac in host_info.items():
    print(f"{ip} -> {mac}")

# 使用類接口
scanner = ArpScanner()
results = scanner.scan_range("10.0.0.1", "10.0.0.100")
```

### 命令行工具

```bash
# Ping 掃描
fping

# ARP 掃描
farp
```

## 特點

- 多線程掃描，速度極快(使用ping scan 65535個裝置約30~60秒 ,使用arp scan 約15~30秒)
- 支援 Ping 和 ARP 掃描
- 顯示進度條
- 簡潔的 API 設計

## 系統需求

- Python 3.7+
- Windows 系統（ARP 掃描需要） 