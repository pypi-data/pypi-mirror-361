import httpx
import orjson
from typing import Any, Dict, Optional


class ELIVDomain:
    """
    ELIVDomain 클래스는 ELIV DNS API와 상호 작용하기 위한 클라이언트 역할을 합니다.

    이 클래스는 TLD
    정보 쿼리, 도메인 가용성 확인, 도메인 등록,
    도메인 설정 업데이트, 도메인 세부 정보 검색 등 도메인을 관리하는 기능을 제공합니다.

    :ivar key: 테넌시 아이디:키값
    :type key: str
    """
    def __init__(self, key: str):
        self.VERSION = "v1"
        self.BASE_URL = "https://domain.api.eliv-dns.kr"
        self.HEADERS = {
            "Authorization": key,
            "User-Agent": "ELIV-Domain-API-Python-Client/1.0.0",
        }

    @staticmethod
    def _return(
        result: bool, message: str, code: str, data: Optional[Any] = None
    ) -> Dict[str, Any]:
        return {
            "Result": result,
            "Message": message,
            "Code": code,
            "Data": data if data is not None else [],
        }

    def _fetch(
        self, method: str, path: str, data: Optional[dict] = None
    ) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{self.VERSION}{path}"
        try:
            if method.upper() == "GET":
                resp = httpx.get(url, headers=self.HEADERS, params=data)
            else:
                resp = httpx.request(
                    method.upper(), url, headers=self.HEADERS, json=data
                )
        except httpx.RequestError as e:
            return self._return(False, f"요청 중 오류 발생: {e}", "REQUEST_ERROR")

        try:
            response = orjson.loads(resp.content)
        except orjson.JSONDecodeError as e:
            return self._return(False, f"JSON 디코딩 오류: {e}", "JSON_ERROR")

        if not resp.is_success:
            msg = response.get("MSG", f"HTTP 오류: {resp.status_code}")
            code = response.get("CODE", f"HTTP_ERROR_{resp.status_code}")
            return self._return(False, msg, code)

        if response.get("STATUS") != "OK":
            return self._return(
                False,
                response.get("MSG", "오류"),
                response.get("CODE", "API_ERROR"),
                response.get("DATA", []),
            )
        return self._return(
            True,
            response.get("MSG", "성공"),
            response.get("CODE", "OK"),
            response.get("DATA", []),
        )

    def get_tld_info(self, tld: str) -> Dict[str, Any]:
        """
        TLD 정보 조회
      
        도메인의 TLD(Top Level Domain) 정보를 조회합니다
        TLD의 정책 정보를 확인할 수 있습니다

        :param tld: 조회할 TLD
        :return: TLD 정보 조회 결과
        """
        return self._fetch("GET", f"/Domain/TLD/{tld}")

    def check_domain_availability(self, domain_name: str) -> Dict[str, Any]:
        """
        도메인 등록가능 여부 확인

        :param domain_name: 확인할 도메인 이름
        :return: 도메인 등록 가능 여부 결과
        """
        result = self._fetch("GET", "/Domain/Check", {"DomainName": domain_name})
        if not result["Result"]:
            return result
        data = result["Data"]
        return self._return(
            result["Result"],
            result["Message"],
            result["Code"],
            {"Reason": data.get("Reason"), "Available": data.get("Available")},
        )

    def register_domain(
        self, domain_name: str, contacts: dict, nameservers: list, period: int = 1
    ) -> Dict[str, Any]:
        """
        도메인 등록

        :param domain_name: 등록할 도메인 이름
        :param contacts: 연락처 정보
        :param nameservers: 네임서버 목록
        :param period: 등록 기간 (년 단위)
        :return: 도메인 등록 결과
        """
        return self._fetch(
            "POST",
            "/Domain/Registration",
            {
                "DomainName": domain_name,
                "Contacts": contacts,
                "Nameservers": nameservers,
                "Period": period,
            },
        )

    def register_domain_with_validation(
        self,
        domain_name: str,
        tld: str,
        contacts: dict,
        nameservers: list,
        period: int = 1,
    ) -> Dict[str, Any]:
        """
        도메인 등록 (검증)

        :param domain_name: 등록할 도메인 이름
        :param tld: 도메인 확장자
        :param contacts: 연락처 정보
        :param nameservers: 네임서버 목록
        :param period: 등록 기간 (년 단위)
        :return: 도메인 등록 결과
        """
        tld_info = self.get_tld_info(tld)
        if not tld_info["Result"]:
            return tld_info
        rules = tld_info["Data"].get("Rules", {})
        if period < rules.get("Registration", {}).get("Min", 1):
            return self._return(
                False,
                f"등록 기간은 {rules['Registration']['Min']}년 이상이어야 합니다",
                "INVALID_PERIOD",
            )
        if period > rules.get("Registration", {}).get("Max", 10):
            return self._return(
                False,
                f"등록 기간은 {rules['Registration']['Max']}년 이하여야 합니다",
                "INVALID_PERIOD",
            )
        for ctype in rules.get("ContactTypes", []):
            if ctype not in contacts:
                return self._return(
                    False,
                    f"{tld_info['Data'].get('TLD', tld)} 도메인은 {ctype} 연락처 타입이 필수에요",
                    "MISSING_CONTACT_TYPE",
                )
            get_contact = self.get_contact_by_uuid(contacts[ctype])
            if not get_contact["Result"]:
                return get_contact
        ns_count = len(nameservers)
        if ns_count < rules.get("Nameservers", {}).get("Min", 2):
            return self._return(
                False,
                f"네임서버는 최소 {rules['Nameservers']['Min']}개 이상 필요합니다",
                "INVALID_NAMESERVER_COUNT",
            )
        if ns_count > rules.get("Nameservers", {}).get("Max", 10):
            return self._return(
                False,
                f"네임서버는 최대 {rules['Nameservers']['Max']}개까지 설정 가능합니다",
                "INVALID_NAMESERVER_COUNT",
            )
        return self.register_domain(domain_name, contacts, nameservers, period)

    #
    def get_tenant_info(self) -> Dict[str, Any]:
        """
        테넌시 정보 조회

        :return:
        """
        return self._fetch("GET", "/Tenancy")

    #
    def get_domain_whois(self, domain_name: str) -> Dict[str, Any]:
        """
        도메인 WHOIS 정보 조회

        :param domain_name:
        :return:
        """
        return self._fetch("GET", f"/Domain/{domain_name}/Whois")

    #
    def get_domain_info(self, domain_name: str) -> Dict[str, Any]:
        """
        도메인 정보 조회

        :param domain_name:
        :return:
        """
        return self._fetch("GET", f"/Domain/{domain_name}")

    #
    def renewal_domain(self, domain_name: str, period: int = 1) -> Dict[str, Any]:
        """
        도메인 연장

        :param domain_name:
        :param period:
        :return:
        """
        return self._fetch("POST", f"/Domain/{domain_name}/Renewal", {"Period": period})

    #
    def get_domain_renewal_record(self, domain_name: str) -> Dict[str, Any]:
        """
        도메인 연장기록 조회

        :param domain_name:
        :return:
        """
        return self._fetch("GET", f"/Domain/{domain_name}/Renewal")

    #
    def change_domain_nameservers(
        self, domain_name: str, nameservers: list
    ) -> Dict[str, Any]:
        """
        도메인 네임서버 변경

        :param domain_name:
        :param nameservers:
        :return:
        """
        return self._fetch(
            "POST", f"/Domain/{domain_name}/Nameservers", {"Nameservers": nameservers}
        )

    #
    def delete_domain(self, domain_name: str) -> Dict[str, Any]:
        """
        도메인 삭제

        :param domain_name:
        :return:
        """
        return self._fetch("DELETE", f"/Domain/{domain_name}")

    #
    def change_domain_contacts(
        self, domain_name: str, contacts: dict
    ) -> Dict[str, Any]:
        """
        도메인 연락처 정보 변경

        :param domain_name:
        :param contacts:
        :return:
        """
        return self._fetch(
            "POST", f"/Domain/{domain_name}/Contacts", {"Contacts": contacts}
        )

    #
    def krnic_domain_privacy(self, domain_name: str, privacy: bool) -> Dict[str, Any]:
        """
        도메인 후이즈 정보 비공개 (KRNIC 전용)

        :param domain_name:
        :param privacy:
        :return:
        """
        return self._fetch(
            "PUT", f"/Domain/{domain_name}/KRNICPrivacy", {"KRNICPrivacy": privacy}
        )

    #
    def domain_transfer_lock(self, domain_name: str, lock: bool) -> Dict[str, Any]:
        """
        도메인 기관이전 잠금

        :param domain_name:
        :param lock:
        :return:
        """
        return self._fetch(
            "PUT", f"/Domain/{domain_name}/TransferLock", {"TransferLock": lock}
        )

    #
    def change_domain_auth_code(self, domain_name: str) -> Dict[str, Any]:
        """
        도메인 인증코드 변경

        :param domain_name:
        :return:
        """
        return self._fetch("PUT", f"/Domain/{domain_name}/AuthCode")

    #
    def domain_transfer_list(self) -> Dict[str, Any]:
        """
        도메인 기관이전 목록 조회

        :return:
        """
        return self._fetch("GET", "/Domain/Transfer")

    # 도메인 예약 (KRNIC만 지원)
    def domain_reservation(self, domain_name: str) -> Dict[str, Any]:
        return self._fetch("POST", "/Domain/Reservation", {"DomainName": domain_name})

    # 도메인 인증코드 검증
    def krnic_domain_transfer_code_verification(
        self, domain_name: str, auth_code: str
    ) -> Dict[str, Any]:
        return self._fetch(
            "POST",
            "/Domain/Transfer/AuthCode",
            {"DomainName": domain_name, "AuthCode": auth_code},
        )

    # 도메인 기관이전 신청
    def krnic_domain_transfer(
        self, domain_name: str, auth_code: str, contacts: dict
    ) -> Dict[str, Any]:
        return self._fetch(
            "POST",
            "/Domain/Transfer",
            {"DomainName": domain_name, "AuthCode": auth_code, "Contacts": contacts},
        )

    # 도메인 Glue Record 조회
    def get_domain_glue_record(self, domain_name: str) -> Dict[str, Any]:
        return self._fetch("GET", f"/Domain/{domain_name}/GlueRecord")

    # 도메인 Glue Record 추가
    def add_domain_glue_record(
        self, domain_name: str, hostname: str, ip: str
    ) -> Dict[str, Any]:
        return self._fetch(
            "POST",
            f"/Domain/{domain_name}/GlueRecord",
            {"Hostname": hostname, "IPAddress": ip},
        )

    # 도메인 Glue Record 삭제
    def delete_domain_glue_record(
        self, domain_name: str, glue_record_uuid: str
    ) -> Dict[str, Any]:
        return self._fetch(
            "DELETE", f"/Domain/{domain_name}/GlueRecord/{glue_record_uuid}"
        )

    # 도메인 DNSSEC 설정
    def set_domain_dnssec(
        self, domain_name: str, ds_record: list, dnskey: list
    ) -> Dict[str, Any]:
        return self._fetch(
            "POST",
            f"/Domain/{domain_name}/DNSSEC",
            {"DS_Record": ds_record, "DNSKEY": dnskey},
        )

    # 도메인 DNSSEC 정보 조회
    def get_domain_dnssec(self, domain_name: str) -> Dict[str, Any]:
        return self._fetch("GET", f"/Domain/{domain_name}/DNSSEC")

    # 도메인 포워딩 설정
    def set_domain_forwarding(
        self, domain_name: str, subdomain: Optional[str] = None
    ) -> Dict[str, Any]:
        return self._fetch(
            "POST",
            "/MagicDNS/Forward/Domain",
            {"DomainName": domain_name, "Subdomain": subdomain},
        )

    # 도메인 포워딩 삭제
    def delete_domain_forwarding(
        self, domain_name: str, forward_uuid: str
    ) -> Dict[str, Any]:
        return self._fetch(
            "DELETE", f"/MagicDNS/Forward/Domain/{domain_name}/{forward_uuid}"
        )

    # 도메인 포워딩 목록 조회
    def get_domain_forwarding_list(self, domain_name: str) -> Dict[str, Any]:
        return self._fetch("GET", f"/MagicDNS/Forward/Domain/{domain_name}")

    # 연락처 생성
    def create_contact(self, data: dict) -> Dict[str, Any]:
        return self._fetch("POST", "/Contact/Create", data)

    # 연락처 UUID 조회
    def get_contact_by_uuid(self, contact_uuid: str) -> Dict[str, Any]:
        return self._fetch("GET", f"/Contact/{contact_uuid}")
