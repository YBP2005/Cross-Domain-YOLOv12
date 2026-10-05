# -*- coding: utf-8 -*-
"""90_fetch_via_jump.py —— **经跳板机取外网**的统一入口（只读，不落任何文件）。

为什么要它
----------
本机**没有外网**（见交接件 §3.2），一切检索必须经跳板机。
2026-10-03 那一轮 F/G/H 检索失败的根因是"通道退化"（arXiv API 全程 429、OpenAlex 额度耗尽），
而不是"这三条主张没有先例" ⇒ 要重跑，就得先把**通道本身**做稳、做成可重复调用的一件工具。

★ 凭据纪律（铁律 #9）
--------------------
口令**只从环境变量 `JUMP_PW` 读**，**不落盘、不打印、不进任何产物**。
本文件里**没有**任何口令、也没有任何机器名被写死（主机/端口/用户从环境变量取，缺省值只是方便）。

用法
----
    JUMP_PW=... python scripts/90_fetch_via_jump.py crossref "<query>" [rows]
    JUMP_PW=... python scripts/90_fetch_via_jump.py arxiv "<query>" [max_results]
    JUMP_PW=... python scripts/90_fetch_via_jump.py datacite "<query>" [rows]
    JUMP_PW=... python scripts/90_fetch_via_jump.py openalex "<query>" [rows]
    JUMP_PW=... python scripts/90_fetch_via_jump.py url "<https://...>"          # 任意页面/接口
    JUMP_PW=... python scripts/90_fetch_via_jump.py probe                        # 只测通道

输出：**纯文本**，每行一个候选（作者 / 年 / 题名 / DOI 或 URL / 一句摘要片段）。
设计依据：经验 #32（外网检索的工具行为与取证）——**必须做阴性对照**，见 `probe` 子命令里的
"确定不存在的词"对照；**取到 0 字节 = 取数失败，不是零命中**。
"""
import os
import re
import sys
import json
import html
import shlex

HOST = os.environ.get('JUMP_HOST', '117.50.181.2')
PORT = int(os.environ.get('JUMP_PORT', '23'))
USER = os.environ.get('JUMP_USER', 'root')
PW = os.environ.get('JUMP_PW')

UA = 'Mozilla/5.0 (compatible; research-lit-check/1.0)'


def _conn():
    import paramiko
    if not PW:
        sys.stderr.write('ERROR: 环境变量 JUMP_PW 未设置（口令只走环境变量，绝不落盘）\n')
        sys.exit(3)
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=PORT, username=USER, password=PW,
              timeout=25, banner_timeout=30, auth_timeout=30)
    return c


def run(c, cmd, timeout=90):
    _, so, se = c.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace')
    err = se.read().decode('utf-8', 'replace')
    return out, err


def fetch(c, url, timeout=60):
    """经跳板机取一个 URL 的**正文**；返回 (http_code, body)。"""
    q = shlex.quote(url)
    cmd = ("curl -sS -L --max-time %d -A %s -w '\\n__HTTP__%%{http_code}' %s"
           % (timeout, shlex.quote(UA), q))
    out, err = run(c, cmd, timeout=timeout + 30)
    code = ''
    m = re.search(r'__HTTP__(\d+)\s*$', out)
    if m:
        code = m.group(1)
        out = out[:m.start()]
    return code, out, err


def strip_tags(s):
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def out_crossref(body, rows):
    try:
        items = json.loads(body)['message']['items']
    except Exception as e:
        print('  [crossref 解析失败] %s' % e)
        return
    for it in items[:rows]:
        au = '; '.join((a.get('family', '') + ', ' + a.get('given', '')).strip(', ')
                       for a in it.get('author', [])[:6])
        yr = (it.get('issued', {}).get('date-parts') or [['?']])[0][0]
        ven = (it.get('container-title') or [''])
        ven = ven[0] if ven else ''
        print('- %s | %s | %s | %s | %s' % (
            yr, (it.get('title') or [''])[0][:180], ven[:70], au[:160], it.get('DOI', '')))


def out_datacite(body, rows):
    try:
        items = json.loads(body)['data']
    except Exception as e:
        print('  [datacite 解析失败] %s' % e)
        return
    for it in items[:rows]:
        a = it.get('attributes', {})
        ti = (a.get('titles') or [{}])[0].get('title', '')
        au = '; '.join(x.get('name', '') for x in (a.get('creators') or [])[:6])
        print('- %s | %s | %s | %s | %s' % (
            a.get('publicationYear', '?'), ti[:180], (a.get('publisher') or '')[:60],
            au[:160], a.get('doi', '')))


def out_arxiv(body, rows):
    entries = re.findall(r'<entry>(.*?)</entry>', body, re.S)
    if not entries:
        # ★ 2026-10-04：把"三态"直接打在输出里 —— 子代理报告里最容易出的一类误判，
        #   就是把**限流失败**或**短语过窄导致的零命中**记成"未找到先例"。
        #   实测分界（阴性对照 `zzqxwvuytnonexistentterm` = 728 B，真命中 >1.4 KB）：
        #     · ~700–900 B   ⇒ **零命中**（检索式过窄，请换措辞）
        #     · < 200 B / 非 200 ⇒ **取数失败**（限流/网络），**必须重试，不得记为未找到**
        _n = len(body)
        _guess = '零命中（检索式过窄？换措辞）' if _n > 400 else '取数失败（必须重试，不得记为未找到）'
        print('  [arxiv 无 entry] 字节=%d ⇒ 判读：%s' % (_n, _guess))
        return
    # ★★ 2026-10-04 第三态：**伪命中**。子代理 H 实测：arXiv API 对
    #   `abs:"多词短语"` / `all:"…"` 这类**带引号**的查询，会返回 200 + 14–23 KB 的
    #   **"最近提交"清单**（与检索式完全无关的粒子物理/交通流论文）⇒ 若只看"字节数大"，
    #   就会把伪命中当成真命中。⇒ **在 arXiv 上只信"不带引号的多词合取式"**；
    #   带引号的短语式查询不应当作证据（见 `deliver/检索复跑_主张H_20261004.md` §1.1）。
    for e in entries[:rows]:
        ti = re.search(r'<title>(.*?)</title>', e, re.S)
        idd = re.search(r'<id>(.*?)</id>', e, re.S)
        pub = re.search(r'<published>(\d{4})', e)
        au = re.findall(r'<name>(.*?)</name>', e, re.S)
        su = re.search(r'<summary>(.*?)</summary>', e, re.S)
        print('- %s | %s | %s | %s' % (
            pub.group(1) if pub else '?',
            strip_tags(ti.group(1))[:180] if ti else '?',
            '; '.join(a.strip() for a in au[:5])[:140],
            (idd.group(1).strip() if idd else '')))
        if su:
            print('    abs: %s' % strip_tags(su.group(1))[:280])


def out_openalex(body, rows):
    try:
        items = json.loads(body).get('results', [])
    except Exception as e:
        print('  [openalex 解析失败] %s' % e)
        return
    for it in items[:rows]:
        au = '; '.join((a.get('author') or {}).get('display_name', '')
                       for a in (it.get('authorships') or [])[:6])
        print('- %s | %s | %s | %s | %s' % (
            it.get('publication_year', '?'), (it.get('title') or '')[:180],
            ((it.get('primary_location') or {}).get('source') or {}).get('display_name', '')[:60],
            au[:150], it.get('doi') or it.get('id', '')))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    mode = sys.argv[1]
    # ★★ 2026-10-04：`batch` —— **串行 + 节流**地跑一批检索式。
    #   起因（实测，值得记）：三只子代理**并发**打 arXiv export API 时，其中一只**全程 429 / 1 字节**，
    #   而我在同一台跳板机上连打三次都是 **200**。⇒ 这是**同一出口 IP 的速率限制**，
    #   **不是"通道退化"、更不是"零命中"**。判据三件套：HTTP 码 + 字节数 + 阴性对照；
    #   `429` 的正确处置是**退避重试**，不是记成"未找到先例"。
    #   用法：`python scripts/90_fetch_via_jump.py batch arxiv <q1> <q2> ... [--sleep=6]`
    if mode == 'batch':
        import time
        from urllib.parse import quote as _q
        sub = sys.argv[2]
        sleep_s, qs = 6.0, []
        for a in sys.argv[3:]:
            if a.startswith('--sleep='):
                sleep_s = float(a.split('=', 1)[1])
            else:
                qs.append(a)
        c = _conn()
        try:
            for i, q in enumerate(qs):
                if i:
                    time.sleep(sleep_s)
                if sub == 'arxiv':
                    url = ('http://export.arxiv.org/api/query?search_query=%s&max_results=8&sortBy=relevance'
                           % _q('all:"%s"' % q))
                    for attempt in (1, 2, 3):
                        code, body, err = fetch(c, url)
                        if code == '200' and len(body) > 1200:
                            break
                        time.sleep(20 * attempt)
                    print('# [%d/%d] arxiv HTTP=%s bytes=%d q=%s' % (i + 1, len(qs), code, len(body), q))
                    out_arxiv(body, 8)
                elif sub == 'crossref':
                    url = 'https://api.crossref.org/works?rows=8&query.bibliographic=%s' % _q(q)
                    code, body, err = fetch(c, url)
                    print('# [%d/%d] crossref HTTP=%s bytes=%d q=%s' % (i + 1, len(qs), code, len(body), q))
                    out_crossref(body, 8)
                else:
                    print('batch 只支持 arxiv / crossref')
                    return 2
        finally:
            c.close()
        return 0
    c = _conn()
    try:
        if mode == 'probe':
            targets = [
                ('crossref', 'https://api.crossref.org/works?rows=1&query.bibliographic=machine+learning'),
                ('datacite', 'https://api.datacite.org/dois?page%5Bsize%5D=1&query=dataset'),
                ('arxiv-abs', 'https://arxiv.org/abs/2304.09446'),
                ('arxiv-api', 'http://export.arxiv.org/api/query?search_query=all:%22domain%20adaptation%22&max_results=1'),
                ('openalex', 'https://api.openalex.org/works?per-page=1&search=domain+adaptation'),
                # ★ 阴性对照：确定不存在的词 —— 用来区分"零命中"与"取数失败"（经验 #32）
                ('NEG-crosref', 'https://api.crossref.org/works?rows=3&query.bibliographic=zzqxwvuytnonexistentterm'),
                ('NEG-arxiv', 'http://export.arxiv.org/api/query?search_query=all:zzqxwvuytnonexistentterm&max_results=3'),
            ]
            for name, url in targets:
                code, body, err = fetch(c, url)
                print('%-13s HTTP=%-4s bytes=%-7d %s' % (name, code or '???', len(body),
                                                         ('ERR:' + err.strip()[:80]) if err.strip() else ''))
            return 0

        if mode == 'url':
            code, body, err = fetch(c, sys.argv[2])
            print('HTTP=%s bytes=%d' % (code, len(body)))
            print(body if len(body) < 20000 else body[:20000] + '\n...[截断]')
            return 0

        q = sys.argv[2]
        rows = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        from urllib.parse import quote
        if mode == 'crossref':
            url = ('https://api.crossref.org/works?rows=%d&query.bibliographic=%s'
                   % (rows, quote(q)))
            code, body, err = fetch(c, url)
            print('# crossref HTTP=%s bytes=%d q=%s' % (code, len(body), q))
            out_crossref(body, rows)
        elif mode == 'datacite':
            # ⚠ `page[size]` 的方括号必须**百分号编码**，否则 curl 报 `bad range in URL`（已踩）
            url = 'https://api.datacite.org/dois?page%%5Bsize%%5D=%d&query=%s' % (rows, quote(q))
            code, body, err = fetch(c, url)
            print('# datacite HTTP=%s bytes=%d q=%s' % (code, len(body), q))
            out_datacite(body, rows)
        elif mode == 'arxiv':
            url = ('http://export.arxiv.org/api/query?search_query=%s&max_results=%d&sortBy=relevance'
                   % (quote('all:"%s"' % q), rows))
            code, body, err = fetch(c, url)
            print('# arxiv HTTP=%s bytes=%d q=%s' % (code, len(body), q))
            out_arxiv(body, rows)
        elif mode == 'openalex':
            url = 'https://api.openalex.org/works?per-page=%d&search=%s' % (rows, quote(q))
            code, body, err = fetch(c, url)
            print('# openalex HTTP=%s bytes=%d q=%s' % (code, len(body), q))
            out_openalex(body, rows)
        else:
            print('unknown mode: %s' % mode)
            return 2
    finally:
        c.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
