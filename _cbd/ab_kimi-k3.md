<|open|>tools<|sep|><|open|>call tool="Write" index="1"<|sep|><|open|>argument key="file_path" type="string"<|sep|>C:\Users\hp\.codebuddy\projects\e-Novel2\memory\user_writing_style.md<|close|>argument<|sep|><|open|>argument key="content" type="string"<|sep|>---
name: 用户的中文小说写作偏好
description: 用户在 e:\Novel2 写中文长篇小说，要求改写时不用说话人标注（说/问/答），靠句子本身和动作区分说话人；短句为主，不写心理，不总结意义，禁用「不是……是……」句式
type: feedback
---

改写中文小说对话时：不用「说／问／答」等说话人标注，靠句子内容和手部动作区分说话人；短句为主；不写心理活动；不替读者总结意义；禁用「不是……是……」句式；保持每句的信息与先后次序不变；只输出候选正文，前后不加说明或点评。

**Why:** 用户在逐句打磨长篇小说对话，由第三方逐句比对候选版本，任何多余输出都会干扰比对。

**How to apply:** 凡在 e:\Novel2 项目中处理小说文本改写任务时遵循以上约束；信息次序以原文行号顺序为准。
<|close|>argument<|sep|><|close|>call<|sep|><|close|>tools<|sep|><|close|>message<|sep|>
