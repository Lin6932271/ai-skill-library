---
name: reverse-engineering
description: "逆向工程通用入口"
---

# 逆向工程通用入口

## 目标类型智能路由

根据用户描述自动选择深度模块：

| 用户关键词 | 目标类型 | 推荐模块 |
|-----------|---------|---------|
| exe/dll/PE/壳/脱壳/x64dbg/IDA/Safengine/VMProtect/Themida | **Windows 二进制** | `echo windows-binary-deep` |
| APK/Android/Frida/Xposed/jadx/dex2jar/JNI | **Android 移动端** | `echo mobile-reverse` + `echo android-reverse` |
| IPA/iOS/ObjC/Swift/Mach-O/dylib/越狱 | **iOS 移动端** | `echo mobile-reverse` |
| 抓包/协议/Protobuf/gRPC/WebSocket/mitmproxy/Wireshark | **协议逆向** | `echo protocol-reverse` |
| Unity/IL2CPP/UE4/游戏/Cheat Engine | **游戏逆向** | `echo mobile-reverse` (Unity) 或 `echo windows-binary-deep` (PC游戏) |
| Frida Hook/内存 Hook/运行时修改 | **动态分析** | `echo quickref-frida` |
| AES/RSA/加密/解密/哈希 | **密码学分析** | `echo quickref-crypto` |
| IDA Pro/Ghidra/二进制分析 | **静态分析工具** | `echo ida-reverse` 或 `echo ghidra-reverse` |

**执行逻辑**：
1. 识别目标类型（根据上表）
2. 调用对应深度模块（`echo MODULE_ID`）
3. 如需跨域（如Android Native），连续调用多个模块

## 四大逆向领域概览

### 1. Windows 二进制逆向

**典型目标**：exe/dll/sys/ocx  
**核心技能**：脱壳、反混淆、反调试绕过、IAT修复  
**工具链**：
- 静态：IDA Pro、Ghidra、x64dbg、DIE、CFF Explorer
- 动态：x64dbg + ScyllaHide、OllyDbg、WinDbg
- 脱壳：Scylla、UPX、通用脱壳机

**常见壳识别**：
- UPX: 特征节名 `.UPX0/.UPX1`，入口点 PUSHAD
- Safengine: `.sfe` 段，大量花指令
- VMProtect: 无导入表，入口直接VM指令
- Themida: 多层虚拟化，代码熵值 > 7.5
- ASPack: `.aspack` 段
- Armadillo: `.arms` 段

**快速上手**：对于带壳程序，直接调用 `echo windows-binary-deep` 获取30条铁律和标准脱壳SOP。

### 2. 移动端逆向

**Android**：
- 静态：jadx、apktool、dex2jar、baksmali
- 动态：Frida、Xposed、Magisk、VirtualXposed
- 脱壳：FART、BlackDex、DexHunter、FRIDA-DEXDump
- 特殊：Il2CppDumper（Unity）、unidbg（原生模拟）

**iOS**：
- 静态：Hopper、IDA Pro、class-dump、jtool2
- 动态：Frida、Cycript、LLDB、Debugserver
- 越狱检测绕过：Shadow、FlyJB、Liberty Lite
- 砸壳：frida-ios-dump、CrackerXI+、Clutch

**混合架构**：现代 App 常见 Java/Kotlin + JNI Native 双层，需要同时分析 DEX 和 SO。

### 3. 协议逆向

**分析流程**：
1. 流量捕获（mitmproxy/Wireshark/Charles）
2. 协议识别（文本/二进制/混合）
3. 消息边界确定（定长/分隔符/长度字段）
4. 字段解析（Protobuf/gRPC/JSON/XML/自定义）
5. 状态机重建（握手/会话/心跳）

**常见协议栈**：
- HTTP/HTTPS: 明文 JSON 或加密 body
- WebSocket: 文本/二进制帧
- Protobuf: 字段编号 + wire type
- gRPC: HTTP/2 + Protobuf
- MQTT: IoT 常用，主题订阅
- 自定义 TCP/UDP: 需要手工解析

**工具速查**：`echo protocol-reverse` 获取详细命令和盲解技巧。

### 4. 游戏安全逆向

**PC 游戏**：
- 内存修改：Cheat Engine、ArtMoney
- DLL注入：LoadLibrary、SetWindowsHookEx
- 反作弊对抗：BE/EAC/VAC 检测绕过（需 Kernel Driver）

**手游**：
- Unity IL2CPP: Il2CppDumper + Frida Hook
- UE4: UE4SS、Polaris、FModel
- Cocos2d-x: JSB Hook
- 内存修改：GameGuardian（Android Root）

## 通用分析流程（5步法）

### Step 1: 信息收集
```bash
# Windows PE
diec target.exe  # 查壳
strings target.exe | grep -i "license\|key\|verify"  # 提取字符串
pe-parser target.exe  # 解析PE结构

# Android APK
aapt dump badging app.apk  # 包信息
jadx -d output app.apk  # 反编译
apktool d app.apk  # 资源解包

# iOS IPA
unzip app.ipa
otool -L Payload/App.app/App  # 依赖库
class-dump Payload/App.app/App  # ObjC头文件
```

### Step 2: 静态分析
- IDA Pro: F5 反编译查看伪代码
- Ghidra: 自动类型恢复
- 搜索关键字符串交叉引用
- 识别加密算法常量（查 `echo quickref-crypto`）

### Step 3: 动态调试
- 下断点在关键函数（CreateFileW/RegOpenKeyExW/网络API）
- 观察参数和返回值
- 修改返回值测试（license check 强制返回 true）
- 记录调用栈

### Step 4: Hook 和修改
- Frida Hook 修改运行时行为（查 `echo quickref-frida`）
- x64dbg Patch 二进制（JMP/NOP 验证跳转）
- Xposed 持久化 Hook（Android）

### Step 5: 验证和文档
- 测试修改后的程序是否正常运行
- 记录关键地址、偏移、算法
- 输出 Patch/Hook 脚本

## 加密算法快速识别

### 常量特征搜索（IDA/x64dbg 中）
| 算法 | 搜索十六进制 | 说明 |
|------|-------------|------|
| AES | 63 7C 77 7B F2 6B | S-box 前6字节 |
| MD5 | 67 45 23 01 EF CD AB 89 | 初始化向量 |
| SHA-1 | 67 45 23 01 EF CD AB 89 98 BA DC FE | IV 完整 |
| SHA-256 | 6A 09 E6 67 BB 67 AE 85 | IV 前8字节 |
| RSA | 00 01 00 01 | 公钥指数 65537 |
| Base64 | "ABCDEFGHIJKLMNOP..." | 编码表字符串 |

识别到算法后，调用 `echo quickref-crypto` 获取加密/解密一行代码。

## 工具命令速查

### IDA Pro
```
空格        切换文本/图形视图
F5          反编译当前函数
X           交叉引用（找谁调用了这个函数）
N           重命名函数/变量
Y           修改函数签名
G           跳转到地址
Ctrl+S      搜索字节序列
Alt+T       搜索文本
Shift+F12   字符串窗口
```

### x64dbg
```
F2          下断点
F7          步入
F8          步过
F9          运行
Ctrl+G      跳转到地址
Ctrl+B      二进制搜索
Ctrl+F      搜索命令
右键 → Binary → Edit  修改字节
Plugins → Scylla      脱壳/修复IAT
```

### Frida
```bash
# 附加进程
frida -U -n com.example.app -l script.js

# 启动并注入
frida -U -f com.example.app -l script.js --no-pause

# 列出所有进程
frida-ps -U

# Spawn 模式（Hook 启动过程）
frida -U -f com.example.app --no-pause -l script.js
```

完整 Frida Hook 模板：`echo quickref-frida`

### jadx
```bash
# 反编译 APK
jadx -d output app.apk

# 只反编译代码（跳过资源）
jadx --no-res -d output app.apk

# 导出 Gradle 项目
jadx --export-gradle -d output app.apk
```

### apktool
```bash
# 解包
apktool d app.apk -o output

# 重打包
apktool b output -o app_modified.apk

# 对齐和签名
zipalign -v 4 app_modified.apk app_aligned.apk
apksigner sign --ks my.keystore app_aligned.apk
```

## 输出标准

完成逆向任务后必须提供：

1. **目标信息**
   - 文件名、SHA256 哈希
   - 平台（Windows/Android/iOS）
   - 壳类型（如有）

2. **分析结果**
   - 关键函数地址/偏移
   - 算法识别（AES/RSA/自定义）
   - 字符串/资源发现

3. **可执行产物**（至少一种）
   - Patch 后的文件
   - Frida Hook 脚本
   - IDA/Ghidra 项目文件
   - 解密脚本

4. **验证证据**
   - 修改前后对比截图
   - 关键内存/寄存器值
   - 成功绕过的验证点

5. **复现步骤**
   - 完整命令序列
   - 环境要求（工具版本、依赖）
   - 已知限制

## 下一步：调用深度模块

根据目标类型，执行对应的 `echo MODULE_ID` 命令加载深度分析流程。

## 使用前核对

目标与操作范围以用户当前请求为准；核对方法前置条件、工具和附件，按实际执行层级记录结果。正文不表示示例代码已经在本机执行或验证。
