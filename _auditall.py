# -*- coding: utf-8 -*-
"""Full-manuscript audit. Writes _auditall_out.md (UTF-8), prints ASCII status."""
import io, re, statistics, glob

VOLS = [
    ('一', ['40_卷一_人类反馈_正文.md'], 58367),
    ('二', ['41_卷二_以斯拉书_正文.md'], 28005),
    ('三', sorted(glob.glob('42*.md')), 64012),
    ('四', ['43_卷四_冻存_正文.md'], 62397),
    ('五', ['44_卷五_剂量_正文.md'], 48408),
    ('六', ['67_卷六_十一秒_正文.md'], 26446),
    ('七', ['45_卷七_嗯_正文.md'], 60069),
    ('八', ['46_卷八_晨昏线_正文.md'], 230389),
    ('九', ['48_卷九_记录之外_正文.md'], 204915),
    ('十', ['50_卷十_针脚_正文.md'], 161416),
]

hz = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
BAN = '——|仿佛|宛如|不禁|犹如|值得注意|换句话说|事实上|与此同时|更关键|说白了|本质上|这意味着|这说明|终极|完美|史诗|杰作|最锋利|觉醒|麻木|异化'
NOTIS = r'不是.{1,14}，是'
TRAD = r'[個這時說會來與後裡麼樣內]'


def measure(files):
    t = '\n'.join(io.open(f, encoding='utf-8').read() for f in files)
    h = hz(t)
    secs = re.findall(r'(?m)^## .*$', t)
    lens = [hz(s) for s in re.split(r'(?m)^## ', t)[1:]] or [h]
    body = re.sub(r'(?m)^#.*$', '', t)
    sents = [s for s in re.split(r'(?<=[。！？])', body) if hz(s)]
    sl = [hz(s) for s in sents]
    parts = re.split(r'(```.*?```)', t, flags=re.S)
    prose = ''.join(p for p in parts if not p.startswith('```'))
    prose = re.sub(r'(?m)^#.*$', '', prose)
    pl = [hz(s) for s in re.split(r'(?<=[。！？])', prose) if hz(s)]
    ad = [abs(pl[i] - pl[i - 1]) for i in range(1, len(pl))]
    dlg = sum(hz(m) for m in re.findall(r'"[^"]*"|“[^”]*”', t))
    brk = sum(hz(m) for m in re.findall(r'「[^」]*」', t))
    return dict(
        hanzi=h, secs=len(secs), median=statistics.median(lens), mx=max(lens),
        sent=round(sum(sl) / len(sl), 1), le20=round(sum(1 for x in sl if x <= 20) / len(sl) * 100, 1),
        ge60=round(sum(1 for x in sl if x >= 60) / len(sl) * 100, 1),
        ge80=sum(1 for x in sl if x >= 80),
        adj=round(sum(1 for x in ad if x <= 3) / len(ad) * 100, 1) if ad else 0.0,
        dlg=round(dlg / h * 100, 1), brk=round(brk / h * 100, 1),
        digits=len(re.findall(r'[0-9]', t)),
        perwan=round(len(re.findall(r'[0-9]', t)) / h * 10000),
        ban=len(re.findall(BAN, t)), notis=len(re.findall(NOTIS, t)),
        trad=len(set(re.findall(TRAD, t))), curly=len(re.findall(r'[「」“”]', t)),
        glue=len(re.findall(r'```[^\n]', t)),
    )


rows, total, bad = [], 0, []
for name, files, expect in VOLS:
    m = measure(files)
    total += m['hanzi']
    if m['hanzi'] != expect:
        bad.append(f'卷{name} hanzi {m["hanzi"]} != {expect}')
    rows.append((name, m))

lines = ['# 全书实测（_auditall.py 生成）', '',
         '| 卷 | 字数 | 节 | 中位 | 最长 | 句均 | ≤20% | ≥60% | ≥80 | 邻差≤3 | 引号内% | 「」% | 数字/万 | 禁用 | 解说句 | 繁体 | 围栏 |',
         '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for name, m in rows:
    lines.append(f"| {name} | {m['hanzi']:,} | {m['secs']} | {m['median']:g} | {m['mx']:,} | {m['sent']} | {m['le20']}% | {m['ge60']}% | {m['ge80']} | {m['adj']}% | {m['dlg']}% | {m['brk']}% | {m['perwan']} | {m['ban']} | {m['notis']} | {m['trad']} | {m['glue']} |")
lines += ['', f'合计 {total:,} 字。']
lines += [
    '',
    '读表口径：',
    '- **引号内%** 是 “…”／"…" 里的汉字占比，**不是对白占比**。「」另列。卷九第一章至第四章用引号，第五章起改「名字：」逐字稿，引号消失，2.4% 只覆盖四章；该卷说话占 73.9%，见 `00` 注 *。',
    '- 卷七的 2.9% 是术语引用（“自检”“失效”等），无对白；卷十前十八章用“”，十九章（第 X 日章）起用「」，两套相加 40.2%；卷六的 10.9% 全为「」，界面标签、结论句与人物短句混用。',
    '- **禁用**一栏的 22 处已逐处归类：卷四 13（对白截断 11、表格空缺 2）、卷九 5（逐字稿里被打断的话）、卷十 3（对白截断、唱词收尾、拟声）、卷一 1（招工单上的「口头史诗」）；破折号只出现在被截断的话和表格空缺里，叙述里零处。其余禁用词全书零。',
    '- 中位统一为两中值平均；偶数节取上中位的旧记法见 `00` 表下的「复尺」条。',
]

# cross-checks
lines.append('')
lines.append('核对：')
lines.append(f'- 全书字数 {total:,}（`30` 记 944,424）：{"一致" if total == 944424 else "不一致"}')
for name, m in rows:
    pass
lines.append(f'- 十卷字数与 `30` 逐卷：{"全部一致" if not bad else "；".join(bad)}')

io.open('_auditall_out.md', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('total', total, 'expect 944424', 'OK' if total == 944424 else 'MISMATCH')
print('per-volume', 'OK' if not bad else 'MISMATCH')
for b in bad:
    print('  ', b.encode('ascii', 'replace').decode())
print('rows', len(rows))
