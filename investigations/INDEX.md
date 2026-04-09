# 조사 인덱스 (Investigation Index)

> 모든 시드 IP의 조사 상태를 한 곳에서 관리한다.  
> 새 조사 파일 생성 시 이 인덱스도 반드시 업데이트한다.  
> **last_seen / last_verified:** 악성 활동 마지막 관측일·조사자 재확인일 (상세는 각 조사 보고서 lifecycle 필드).

**마지막 업데이트:** 2026-04-09

> **진행률 집계는 [`reports/summary.md`](../reports/summary.md)를 참조하세요.** `python scripts/generate_reports.py`로 자동 갱신됩니다.

---

## 서비스A IP 목록


| IP | 상태 | 클러스터 | 인프라 | last_seen | last_verified | 조사 파일 |
| --- | --- | --- | --- | --- | --- | --- |
| 221.143.197.135 | DONE | Cluster#1 | KR_RESIDENTIAL | 2026-03-14 | 2026-04-07 | [보고서](cluster1/221.143.197.135.md) |
| 221.143.197.136 | DONE | Cluster#1 | KR_RESIDENTIAL | 2026-03-14 | 2026-04-07 | [보고서](cluster1/221.143.197.136.md) |
| 221.143.197.13 | PARTIAL | Cluster#1 추정 | KR_RESIDENTIAL (SK Broadband, 대구) | - | 2026-04-09 (board 35p+36–59p) | [보고서](cluster1/221.143.197.13.md) |
| 218.236.231.231 | PARTIAL | - | - | - | - | [보고서](unclassified/218.236.231.231.md) |
| 218.236.231.232 | PARTIAL | - | - | - | - | [보고서](unclassified/218.236.231.232.md) |
| 218.236.231.235 | PARTIAL | - | - | - | - | [보고서](unclassified/218.236.231.235.md) |
| 121.170.203.142 | PARTIAL | - | - | - | - | [보고서](unclassified/121.170.203.142.md) |
| 125.141.26.12 | PARTIAL | - | - | - | - | [보고서](unclassified/125.141.26.12.md) |


## 기프티콘 IP 목록


| IP | 상태 | 클러스터 | 인프라 | last_seen | last_verified | 조사 파일 |
| --- | --- | --- | --- | --- | --- | --- |
| 221.143.197.135 | DONE | Cluster#1 | KR_RESIDENTIAL | 2026-03-14 | 2026-04-07 | [보고서](cluster1/221.143.197.135.md) |
| 39.118.92.147 | PARTIAL | - | KR_MOBILE 추정 | - | - | [보고서](unclassified/39.118.92.147.md) |
| 122.99.176.197 | PARTIAL | - | - | - | - | [보고서](unclassified/122.99.176.197.md) |
| 218.238.34.55 | PARTIAL | - | - | - | - | [보고서](unclassified/218.238.34.55.md) |
| 223.26.145.161 | PARTIAL | - | - | - | - | [보고서](unclassified/223.26.145.161.md) |
| 103.11.26.217 | PARTIAL | - | - | - | - | [보고서](unclassified/103.11.26.217.md) |
| 218.36.50.230 | PARTIAL | - | - | - | - | [보고서](unclassified/218.36.50.230.md) |
| 182.224.243.237 | PARTIAL | - | - | - | - | [보고서](unclassified/182.224.243.237.md) |
| 203.216.180.165 | PARTIAL | - | - | - | - | [보고서](unclassified/203.216.180.165.md) |
| 211.254.20.124 | PARTIAL | - | - | - | - | [보고서](unclassified/211.254.20.124.md) |
| 182.208.225.70 | PARTIAL | - | - | - | - | [보고서](unclassified/182.208.225.70.md) |
| 211.36.152.160 | PARTIAL | - | - | - | - | [보고서](unclassified/211.36.152.160.md) |
| 223.26.145.166 | PARTIAL | - | - | - | - | [보고서](unclassified/223.26.145.166.md) |
| 211.254.98.200 | PARTIAL | - | - | - | - | [보고서](unclassified/211.254.98.200.md) |
| 218.36.87.94 | PARTIAL | - | - | - | - | [보고서](unclassified/218.36.87.94.md) |
| 223.26.161.163 | PARTIAL | - | - | - | - | [보고서](unclassified/223.26.161.163.md) |
| 223.165.203.142 | PARTIAL | - | - | - | - | [보고서](unclassified/223.165.203.142.md) |
| 218.36.99.252 | PARTIAL | - | - | - | - | [보고서](unclassified/218.36.99.252.md) |
| 211.241.215.41 | PARTIAL | - | - | - | - | [보고서](unclassified/211.241.215.41.md) |
| 223.26.178.120 | PARTIAL | - | - | - | - | [보고서](unclassified/223.26.178.120.md) |
| 118.235.74.151 | PARTIAL | - | - | - | - | [보고서](unclassified/118.235.74.151.md) |
| 211.201.169.74 | PARTIAL | - | - | - | - | [보고서](unclassified/211.201.169.74.md) |
| 125.132.9.135 | PARTIAL | - | - | - | - | [보고서](unclassified/125.132.9.135.md) |
| 218.36.50.67 | PARTIAL | - | - | - | - | [보고서](unclassified/218.36.50.67.md) |
| 61.96.100.169 | PARTIAL | - | - | - | - | [보고서](unclassified/61.96.100.169.md) |


## 서비스C IP 목록 (Vultr VPS 대역)


| IP | 상태 | 클러스터 | 인프라 | last_seen | last_verified | 조사 파일 |
| --- | --- | --- | --- | --- | --- | --- |
| 141.164.36.87 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.36.87.md) |
| 141.164.37.225 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.37.225.md) |
| 141.164.39.46 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.39.46.md) |
| 141.164.40.188 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.40.188.md) |
| 141.164.48.3 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.48.3.md) |
| 141.164.49.178 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.49.178.md) |
| 141.164.49.218 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.49.218.md) |
| 141.164.52.110 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.52.110.md) |
| 141.164.52.34 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.52.34.md) |
| 141.164.53.101 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.53.101.md) |
| 141.164.56.216 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.56.216.md) |
| 141.164.60.85 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.60.85.md) |
| 141.164.61.113 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/141.164.61.113.md) |
| 158.247.194.42 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.194.42.md) |
| 158.247.195.36 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.195.36.md) |
| 158.247.198.28 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.198.28.md) |
| 158.247.200.9 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.200.9.md) |
| 158.247.202.252 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.202.252.md) |
| 158.247.210.130 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.210.130.md) |
| 158.247.220.75 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.220.75.md) |
| 158.247.224.35 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.224.35.md) |
| 158.247.225.151 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.225.151.md) |
| 158.247.225.193 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.225.193.md) |
| 158.247.233.19 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.233.19.md) |
| 158.247.233.59 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.233.59.md) |
| 158.247.236.138 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.236.138.md) |
| 158.247.238.216 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.238.216.md) |
| 158.247.239.223 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/158.247.239.223.md) |
| 64.176.224.115 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/64.176.224.115.md) |
| 64.176.228.120 | PARTIAL | Cluster#2 후보 | VPS_GLOBAL (Vultr) | - | - | [보고서](unclassified/64.176.228.120.md) |
| 211.255.155.246 | PARTIAL | - | 미확인 | - | - | [보고서](unclassified/211.255.155.246.md) |


---

## 피벗으로 추가 확보한 IP

> 아래 IP는 seed 진행률에 포함하지 않음. izanaholdings 직접 본문에서 확인된 추가 residential IP만 기록.

| IP | 상태 | 클러스터 | 인프라 | last_seen | last_verified | 조사 파일 |
| --- | --- | --- | --- | --- | --- | --- |
| 220.123.216.40 | DONE | Cluster#1 | KR_RESIDENTIAL | 2026-04-07 | 2026-04-07 | [보고서](cluster1/220.123.216.40.md) |
| 218.49.179.79 | DONE | Cluster#1 | KR_RESIDENTIAL | 2026-04-07 | 2026-04-07 | [보고서](cluster1/218.49.179.79.md) |
| 125.132.9.140 | DONE | Cluster#1 | KR_RESIDENTIAL | 2026-04-07 | 2026-04-07 | [보고서](cluster1/125.132.9.140.md) |
| 125.132.9.136 | DONE | Cluster#1 | KR_RESIDENTIAL | 2026-04-07 | 2026-04-07 | [보고서](cluster1/125.132.9.136.md) |
| 14.51.2.179 | DONE | Cluster#1 | KR_RESIDENTIAL | 2026-04-07 | 2026-04-07 | [보고서](cluster1/14.51.2.179.md) |
| 121.159.134.27 | PARTIAL | Cluster#1 추정 | KR_RESIDENTIAL (추정) | - | - | [보고서](cluster1/121.159.134.27.md) |

---

## 클러스터별 파일 위치


| 클러스터      | 폴더              | 설명                                    |
| --------- | --------------- | ------------------------------------- |
| Cluster#1 | `cluster1/`     | 뽀로로/곰돌이/라부부 통신 네트워크 (seed + 직접 피벗 IP) |
| Cluster#2 | `cluster2/`     | @YY77882 불법 의약품 자동화 인프라 (Vultr VPS)     |
| 미분류       | `unclassified/` | 기프티콘 KR_RESIDENTIAL 등 클러스터 미배정 IP       |
