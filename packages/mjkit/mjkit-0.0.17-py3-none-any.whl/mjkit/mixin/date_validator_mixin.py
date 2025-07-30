from datetime import datetime
from typing import List
from mjkit.utiles import get_logger
import logging

class DateValidatorMixin:
    def validate_yyyymmdd(self, date_str: str) -> None:
        """
        주어진 문자열이 'YYYYMMDD' 형식인지 검증합니다.

        Raises:
            ValueError: 형식이 맞지 않거나 날짜로 변환 불가능한 경우
        """
        try:
            logger = get_logger(__name__, level=logging.INFO)
            logger.info(f"[✅ 날짜 형식 검증] '{date_str}' 형식 검증 시작")
            datetime.strptime(date_str, "%Y%m%d")
        except ValueError as e:
            raise ValueError(f"[❌ 잘못된 날짜 형식] '{date_str}'는 'YYYYMMDD' 형식이 아닙니다.") from e

    def validate_yyyymmdd_list(self, date_list: List[str]) -> None:
        """
        날짜 문자열 리스트가 모두 'YYYYMMDD' 형식을 따르는지 검증합니다.

        Args:
            date_list (List[str]): 날짜 문자열 리스트

        Raises:
            ValueError: 하나라도 형식에 맞지 않으면 예외 발생
        """
        for date_str in date_list:
            self.validate_yyyymmdd(date_str)
