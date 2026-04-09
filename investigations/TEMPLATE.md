# 조사 보고서: [IP주소]

> **사용법:** 이 파일을 복사해 `investigations/cluster[N]/[IP주소].md` 또는 `investigations/unclassified/[IP주소].md`로 저장 후 작성.  
> 필수 항목: ⭐ / 선택 항목: ○

**조사일:** YYYY-MM-DD  
**조사자:**  
**상태:** UNVERIFIED | PARTIAL | DONE  
**클러스터:** Cluster#N | 미분류  
**신뢰도:** HIGH | MEDIUM | LOW | UNVERIFIED  

**first_seen:** YYYY-MM-DD  
**last_seen:** YYYY-MM-DD  
**last_verified:** YYYY-MM-DD  
**ttl_days:** 90  
**lifecycle_state:** ACTIVE | STALE | RETIRED | UNVERIFIED  

> `ttl_days` 기본: KR_RESIDENTIAL 90, VPS_GLOBAL 30, KR_MOBILE 60.  
> `STALE`/`RETIRED` 는 `generate_reports.py` 블록리스트에서 제외. [OPS.md](../OPS.md) 참고.

---

## ⭐ IP 기본 정보

| 항목 | 값 |
|---|---|
| IP | |
| ISP / ASN | |
| Usage Type | Fixed Line ISP \| Mobile ISP \| Data Center/Web Hosting |
| Country | |
| City | |
| IP 범위 (/24) | |
| AbuseIPDB | ✅ 등록됨 / ❌ 미등록 |
| 인프라 유형 | KR_RESIDENTIAL \| KR_MOBILE \| VPS_GLOBAL \| PROXY |

---

## ⭐ 사용된 검색어

- [ ] `"[IP주소]"`
- [ ] `"[IP주소]" 내구제 OR 유심 OR 기프티콘 OR 텔레그램`
- [ ] `site:izanaholdings.com "[IP주소]"`
- [ ] (추가 검색어 기록)

---

## ⭐ 게시판 스팸 활동

| 사이트 | 날짜 | 닉네임 | 내용 요약 | IOC |
|---|---|---|---|---|
| | | | | |

> 직접 게시 확인 없으면 "직접 게시 미확인" 기록.

---

## ⭐ 추출된 IOC

| IOC 유형 | 값 | 출처 URL/사이트 | 발견일 | ioc_registry 등록 |
|---|---|---|---|---|
| 텔레그램 | | | | ✅ / ❌ |
| 도메인 | | | | ✅ / ❌ |
| 닉네임 | | | | ✅ / ❌ |
| 추가 IP | | | | ✅ / ❌ |

---

## ⭐ 클러스터 귀속 근거

**귀속 클러스터:** Cluster#N | 미분류

| 근거 유형 | 내용 |
|---|---|
| 공유 IOC | (다른 IP와 공유된 텔레그램/닉네임/도메인) |
| 동일 서브넷 | (같은 /24 대역 내 확인된 IP) |
| 행위 패턴 유사 | (동일 스팸 유형, 동일 게시 방식 등) |

> 귀속 기준: IOC 2개 이상 공유 OR 동일 /24 서브넷 + IOC 1개 이상 공유

---

## ○ 인프라 인접 IP 확인

| IP | 확인 방법 | 결과 |
|---|---|---|
| (같은 /24 대역 IP) | | 동일 행위자 / 무관 / 미확인 |

---

## ⭐ 다음 피벗 대상

- [ ] (IOC 유형: 값) — 이유
- [ ] (IOC 유형: 값) — 이유

---

## ○ 특이사항

(조사 중 발견한 특이한 점, 주의사항 등)
