---
name: network-analysis
description: "分析 PCAP、协议会话、异常请求或连接故障"
---

# Network Analysis

## Activation conditions
User request contains: 抓包、MITM、中间人、burp、wireshark、tcpdump、ARP、spoof、sniff、CDN、直链、下载加速

## SOP

1. **Protocol analysis**: identify the transport-layer protocol (HTTP/HTTPS/TCP/UDP/ARP) → extract key fields
2. **Capture strategy**: pick a tool (Wireshark/tcpdump/burp) → decide the capture point (gateway/local host/man-in-the-middle)
3. **Packet decoding**: decode layer by layer → reassemble the HTTP stream → extract the payload
4. **Attack-surface identification**: analyze auth token/Cookie/session → identify replay/hijack/tamper points
5. **Result output**: structured report → key-packet pcap summary → attack recommendations

## Download-acceleration sub-flow
- **Baidu Netdisk**: in-process memory grab of BDUSS → method=download API → 302 CDN direct link → multi-connection parallel (4-8)
- **Generic CDN download**: analyze the URL signature parameters → HEAD probe → Range multi-segment parallel

## Tool stack
- Packets: Wireshark, tcpdump, tshark
- MITM: mitmproxy, burp suite, bettercap
- Network scanning: nmap, masscan
- Cookie extraction: ReadProcessMemory + regex scan

<!-- skill-trace:9c863c199e7ac52cc6d177052de33d84 -->
