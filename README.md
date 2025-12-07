# 2089026-_TFTP

# 파이썬을 이용한 TFTP 클라이언트 구현 기말 과제 (mytftp.py)

## 1. 개요
본 프로그램은 파이썬과 소켓 API를 사용하여 TFTP (Trivial File Transfer Protocol) 클라이언트를 구현한 기말 과제입니다. [cite_start]TFTP 서버(tftpd-hpa)와 통신하여 파일 전송 기능을 수행합니다[cite: 1].

## 2. 구현 기능
[cite_start]클라이언트는 과제 요구사항에 따라 다음 기능을 구현했습니다[cite: 2, 3].

* **파일 전송:** 파일 다운로드 (`get`) 및 업로드 (`put`) 기능 지원.
* [cite_start]**전송 모드:** 'octet' 모드만 지원[cite: 2].
* [cite_start]**호스트 지정:** IP 주소 또는 도메인 네임 (예: `genie.pcu.ac.kr`) 지원[cite: 2].
* **포트 설정:** `-p port` 옵션을 통한 포트 지정 기능 지원 (기본 포트 69).
* **오류 및 신뢰성:**
    * RRQ, WRQ에 대한 서버 응답이 없을 경우 **타임아웃 처리** 구현.
    * [cite_start]서버 오류 메시지 (`File not found`, `File already exists`) 처리 구현[cite: 3].

## 3. 실행 방법 (Usage)
[cite_start]클라이언트는 명령줄 인수를 통해 실행됩니다.

**기본 형식:**
```bash
$ python mytftp.py host [-p port] [get|put] filename
