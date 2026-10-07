---
name: build-release
description: "构建可运行制品并验证内容、依赖与交付哈希"
---

# Build Release / Build & Release

> Source: cursor-team-kit fix-ci + review-and-ship + Local Workspace build.py practice

## Trigger routing
Keywords: 打包、build、exe、pyinstaller、编译为、构建、release、发布、CI/CD

## SOP: build and release process

### Phase 1: pre-release checks (3 min)
1. `git status` to confirm the working tree is clean
2. `git log -1` to confirm the version number to be released
3. Run the existing test suite `python _selftest.py`
4. Check whether the version.json version number is incremented

### Phase 2: build (10 min)
1. **Python**: `python build.py` or `build.bat`
2. **Node**: `npm run build` or `npx vite build`
3. Verify artifact integrity:
   - Reasonable file size (>100KB, non-empty)
   - Record the hash checksum
   - Quick smoke-test startup validation

### Phase 3: CI failure diagnosis (if it fails)
1. Parse the build log → locate the first error
2. Compare against the last successful build's log (if any)
3. Environment-diff check: Python/Node version, dependency versions, system libraries
4. Incremental fix: change only one variable at a time, rebuild and verify
5. Repeat ≤3 times; if it still fails → full environment rebuild

### Phase 4: release
1. Git commit + push (including version.json)
2. Create a Git Tag (vX.Y.Z)
3. Upload artifacts to the release repository (Gitee Release / GitHub Release)
4. Verify the download URL returns HTTP 200
5. Update the changelog

## Fix-CI quick reference

| Symptom | Common cause | Fix |
|------|---------|------|
| ModuleNotFoundError | Dependency not installed or version mismatch | pip install -r requirements.txt --upgrade |
| ImportError: DLL load failed | Cython/Pyd platform mismatch | Check Python bitness (32/64) |
| Permission denied | File held by a process | Kill the old process |
| MemoryError | Out of memory | Limit parallelism |
| Signing failed | Certificate expired | Check signing configuration |

## Forbidden actions
- Do not skip post-build verification
- Do not commit untested code
- Do not force push to main/master

<!-- skill-trace:a47288e5b54f47fef37bceaa89521cb3 -->
