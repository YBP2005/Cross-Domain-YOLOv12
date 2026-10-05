# -*- coding: utf-8 -*-
r"""_cloud_creds.py -- G1 两台云端机的登录凭据（**仅供本机脚本读**）。

★★ 纪律（本会话一贯，别破）：**凭据不许进任何放行件、不许进 MANIFEST、不许进盲审包。**
   本文件位于 `analysis/work/analysis_M3/scripts/`（**工作脚本目录**），
   它**不在**任何放行/盲审包的清单里；`复现仓库/build/` 是随包目录，故**不放那里**。
   若要做放行件，必须先确认本文件未被任何打包脚本纳入。

   用户已在会话中提供凭据；此处仅为让**监视子代理**能长期独立工作而落盘。
   用毕可删（`g1_monitor.py` 是唯一读取者）。
"""

A_PW = 'vW3M9J2V5f78O4H6'   # A 机 cpod-1u20pv1vhj4v (port 24581)
B_PW = '26jA953OMo708IEX'   # B 机 cpod-1uearmsfxbj2 (port 25046)
