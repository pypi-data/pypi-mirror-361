import re
from typing import List

def validate_yyyymm_format(dates: List[str]) -> None:
    """
    날짜 리스트가 "YYYYMM" 형식인지, 연도/월이 유효한지 검사합니다.

    Parameters
    ----------
    dates : List[str]
        검사할 날짜 문자열 리스트. 예: ["201001", "202312"]

    Raises
    ------
    ValueError
        형식이 잘못되었거나 유효하지 않은 월이 포함된 경우 발생합니다.
    """
    pattern = re.compile(r"^\d{6}$")

    for date_str in dates:
        if not pattern.match(date_str):
            raise ValueError(f"날짜 형식이 잘못되었습니다: {date_str} (올바른 형식: 'YYYYMM')")

        month = int(date_str[4:6])

        if not (1 <= month <= 12):
            raise ValueError(f"월이 유효하지 않습니다: {date_str} (월: {month})")


if __name__ == "__main__":
    # 테스트용 코드
    try:
        validate_yyyymm_format(["202301", "202312", "202313"])  # 마지막 날짜는 잘못된 월
    except ValueError as e:
        print(e)  # "월이 유효하지 않습니다: 202313 (월: 13)"

    try:
        validate_yyyymm_format(["202301", "2023-12"])  # 잘못된 형식
    except ValueError as e:
        print(e)  # "날짜 형식이 잘못되었습니다: 2023-12 (올바른 형식: 'YYYYMM')"

    validate_yyyymm_format(["202301", "202312"])  # 올바른 형식
    print("모든 날짜가 유효합니다.")