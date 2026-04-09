# 관련 레포지토리 및 데이터 흐름

PointPivot과 함께 쓰는 방어 인텔 레포, 그리고 증거·승격 규칙을 정리한다.

## 역할 구분


| 레포                                                              | 초점                                                    | 소스 오브 트루스                            | 주요 산출물                                                                             |
| --------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------ | ---------------------------------------------------------------------------------- |
| **PointPivot** (이 저장소)                                          | 국내 ATO·포인트·기프티콘 **행위망**, 게시판 스팸, residential/VPS seed | `data/*.md`, `investigations/`       | 조사 보고서, `reports/summary.md`, 클러스터 정의                                        |
| **[anonymous-vps](https://github.com/windshock/anonymous-vps)** | 익명·크립토 친화 **호스팅/VPS** 인벤토리, 사건 IOC, 보수적 CIDR 승격       | `data/*.yml`, `data/incidents/*.yml` | `generated/detection/incident-iocs.csv`, `high-risk-cidrs.csv`, Sigma/Logpresso 쿼리 |


두 레포 모두 **방어·탐지·사냥** 목적이며, “전체 VPS = 악성” 같은 단순화는 하지 않는다.

## 데이터 흐름 (요약)

1. **서비스C seed (Vultr 등)** 는 PointPivot에서 OSINT로 행위 맥락을 붙인다.
2. 동일 IP/대역이 **반복 관측**되고 공개 근거가 쌓이면, anonymous-vps의 [정책](https://github.com/windshock/anonymous-vps)에 맞춰 `data/incidents/`에 **IOC `/32`** 로 기여할 수 있다.
3. **역방향:** anonymous-vps의 `provider-ranges.csv` 등으로 PointPivot seed의 **인프라 유형·공급자** 풍부화를 할 수 있다 (자동화는 별도 스크립트로 확장 가능).

## 승격(기여) 시 체크리스트 (anonymous-vps 쪽)

anonymous-vps README의 **Conservative Promotion Rules**를 따른다:

- 단일 사건·단일 리포트만으로 **대역(/24) 승격하지 않는다**.
- **단일 IOC는 `/32` 유지**가 기본.
- PointPivot 조사서에 **직접 게시·행위 근거 URL/날짜**가 있어야 한다 (스니펫만으로는 부족).
- 운영 차단 영향이 크면 **provider 전체 차단이 아닌** incident IOC·high-risk CIDR 정책을 따른다.

## PointPivot 내부 환류

- Seed → `investigate_ip.py` / 브라우저 조사 → IOC → `investigate_ioc.py` → `data/pivot_queue.md` → 재조사 → `campaigns.md` / `INDEX.md` 갱신.  
상세는 [METHODOLOGY.md](METHODOLOGY.md) § 2, [OPS.md](OPS.md).

