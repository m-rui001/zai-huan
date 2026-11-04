#!/bin/bash
for f in "$@"; do
  echo "=== $(basename "$f")"
  echo "  不是A是B: $(grep -o -E '不是[^，。；！？]{1,20}[，。][是为][^，。；！？]' "$f" | grep -v -E '不是[^，。；！？]{1,10}(的|了)?[，。]$' | wc -l)"
  echo "  AI词: $(grep -o -E '仿佛|宛如|不禁|值得注意|换句话说|事实上|与此同时|更关键|说白了|本质上|这意味着|这说明|真正的' "$f" | wc -l)"
  echo "  句式/词表命中: $(python -X utf8 "$(dirname "$0")/audit.py" "$f" 2>/dev/null | grep -c '^  [0-9]')"
  python -X utf8 - "$f" <<'PY'
import re,sys
s=open(sys.argv[1],encoding='utf-8').read()
# 剔除代码块、任务卡行、公文块
body=re.sub(r'```.*?```','',s,flags=re.S)
body=re.sub(r'^【.*?】$','',body,flags=re.M)
body=re.sub(r'^#.*$','',body,flags=re.M)
cn=re.compile(r'[一二三四五六七八九十百千万半]{1,4}(?:块|毛|分|元|天|小时|分钟|秒|个月|年|框|条|对|次|人|岁)')
n=len(cn.findall(body))+len(re.findall(r'\d+',body))
d=n/len(body)*1000
flag='  <<超12' if d>12 else ''
print(f'  叙述数字密度: {d:.1f} 每千字{flag}')
print(f'  叙述字数: {len(body)}')
PY
done
