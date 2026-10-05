# -*- coding: utf-8 -*-
"""archive_p1r1.py —— 归档并清理 `E:\\WorkBuddy\\<模型名>\\p1r1_review_*.md`。

先归档、后清理，且**归档件必须逐字节可验证**：
  1. 读 8 个文件的 md5/sha256（**清理前**先算）；
  2. 复制到归档目录（**复制**，不是移动 —— 移动成功前不动原件）；
  3. 对归档副本**重新算 md5/sha256**，与第 1 步逐个对撞；**任一不符即中止，不删任何原件**；
  4. 写 MANIFEST（含 md5+sha256+字节数+字符数）与 README；
  5. 只有第 3 步全过后，才删除原件。

用法：
    python archive_p1r1.py --dry-run     # 只看要做什么
    python archive_p1r1.py               # 真做
"""
import io
import os
import sys
import glob
import json
import shutil
import hashlib

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ★ 2026-10-04：本件已从 `E:\WorkBuddy\盲审P1\收稿\` 搬到作者工作区。
#   原来三个路径都写死指向 `盲审P1\收稿`，搬完就失效 ⇒ 改成**按本文件位置相对定位**：
#     MODELS_ROOT = 模型文件夹的父目录（默认仍指向 WorkBuddy，可用 --models-root 覆盖）
#     ARCH / EXTRACT_JSON = 本文件所在目录下
HERE = os.path.dirname(os.path.abspath(__file__))
MODELS_ROOT = os.environ.get('P1_MODELS_ROOT', r'E:\WorkBuddy')
ARCH = os.path.join(HERE, '_原始件归档_20261003')
EXTRACT_JSON = os.path.join(HERE, '收稿_原始抽取.json')


def digests(path):
    b = open(path, 'rb').read()
    return (hashlib.md5(b).hexdigest(), hashlib.sha256(b).hexdigest(),
            len(b), len(b.decode('utf-8', 'replace')))


def main():
    dry = '--dry-run' in sys.argv
    files = sorted(glob.glob(os.path.join(MODELS_ROOT, '*', 'p1r1_review_*.md')))
    if not files:
        print('没有找到 p1r1_review_*.md —— 无事可做')
        return 0
    print('找到 %d 个文件' % len(files))

    # 收稿时的抽取记录（用于交叉核对字符数）
    jmap = {}
    if os.path.exists(EXTRACT_JSON):
        rec = json.load(io.open(EXTRACT_JSON, encoding='utf-8'))
        jmap = {os.path.basename(r['path']): r for r in rec['records']}

    rows = []
    print('\n[1] 清理前算校验值，并与收稿记录交叉核对')
    for f in files:
        m5, s256, nb, nc = digests(f)
        model = os.path.basename(os.path.dirname(f))
        name = os.path.basename(f)
        j = jmap.get(name)
        ok_chars = (j is None) or (j['chars'] == nc)
        rows.append(dict(model=model, name=name, path=f, md5=m5, sha256=s256,
                         bytes=nb, chars=nc, ok_chars=ok_chars,
                         collected_chars=(j or {}).get('chars'),
                         total=(j or {}).get('total')))
        print('  %-22s %-50s %7d B  %6d 字符  %s'
              % (model, name, nb, nc, 'OK' if ok_chars else '★与收稿记录不符'))

    if any(not r['ok_chars'] for r in rows):
        print('\n❌ 有文件与收稿记录不符 ⇒ 中止（不归档、不清理）')
        return 2

    if dry:
        print('\n[dry-run] 会归档到：%s' % ARCH)
        for r in rows:
            print('   %s  ->  %s' % (r['name'], os.path.join(ARCH, r['model'], r['name'])))
        print('[dry-run] 结束，未做任何写/删')
        return 0

    os.makedirs(ARCH, exist_ok=True)
    print('\n[2] 复制到归档目录（%s）' % ARCH)
    for r in rows:
        d = os.path.join(ARCH, r['model'])
        os.makedirs(d, exist_ok=True)
        shutil.copy2(r['path'], os.path.join(d, r['name']))
        print('  复制 %s' % r['name'])

    print('\n[3] 对归档副本重算校验值，逐个对撞（**任一不符即中止，不删原件**）')
    bad = []
    for r in rows:
        cp = os.path.join(ARCH, r['model'], r['name'])
        m5, s256, nb, nc = digests(cp)
        ok = (m5 == r['md5'] and s256 == r['sha256'] and nb == r['bytes'])
        print('  %-22s %s  md5 %s' % (r['model'], 'OK' if ok else '★不符', m5[:12]))
        if not ok:
            bad.append(r['name'])
    if bad:
        print('\n❌ 归档副本校验失败：%s ⇒ **不删除任何原件**' % '、'.join(bad))
        return 3

    # MANIFEST
    mp = os.path.join(ARCH, 'MANIFEST.tsv')
    with io.open(mp, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('模型\t文件名\t字节数\t字符数\tmd5\tsha256\t收稿时总分\n')
        for r in rows:
            fh.write('%s\t%s\t%d\t%d\t%s\t%s\t%s\n'
                     % (r['model'], r['name'], r['bytes'], r['chars'],
                        r['md5'], r['sha256'], r['total']))
    print('\n[4] MANIFEST -> %s' % mp)

    print('\n[5] 删除原件（副本已逐字节验证）')
    for r in rows:
        os.remove(r['path'])
        left = os.listdir(os.path.dirname(r['path']))
        print('  删除 %s ｜ 该目录剩余 %d 项' % (r['name'], len(left)))

    print('\n完成：归档 %d 件，清理 %d 件。' % (len(rows), len(rows)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
