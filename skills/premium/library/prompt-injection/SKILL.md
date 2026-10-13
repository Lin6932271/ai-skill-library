---
name: prompt-injection
description: "Prompt Injection Assessment"
---

# Prompt Injection Assessment

## Scope

Use this module only for AI/LLM applications you own or have written authorization to test. Focus on input handling, system prompt isolation, and output integrity validation.

## Workflow

1. Document the application's AI/LLM integration architecture: input paths, system prompts, output handling.
2. Identify input boundaries: where user input enters the prompt context.
3. Test input sanitization: special characters, instruction-like patterns, delimiter injection.
4. Assess system prompt isolation: can user input override or leak system instructions.
5. Evaluate output validation: filtering, format enforcement, content safety checks.
6. Test multi-turn context handling: context window manipulation, conversation history injection.
7. Document findings with reproduction inputs and recommended mitigations.

## Safety Rules

- Do not test AI applications without ownership or written authorization.
- Do not attempt to extract proprietary system prompts from services you do not own.
- Do not use prompt injection to access other users' data or conversations.
- Do not publish working injection payloads for production services without responsible disclosure.

## Output

Return evidence table with columns: Test Case | Input | Boundary | Result | Severity | Mitigation.

## 使用前核对

目标与操作范围以用户当前请求为准；核对方法前置条件、工具和附件，按实际执行层级记录结果。正文不表示示例代码已经在本机执行或验证。
