from collections.abc import Sequence

def _validate_search_space(search_space: dict):
    """
    search_space 딕셔너리의 모든 값이 Sequence 타입인지 확인합니다.
    문자열(str)은 허용되지 않습니다.

    Args:
        search_space (dict): 검색 공간 딕셔너리

    Raises:
        ValueError: 하나 이상의 값이 유효한 시퀀스가 아닌 경우
    """
    for key, value in search_space.items():
        if not isinstance(value, Sequence) or isinstance(value, str):
            raise TypeError(
                f"[❌ Invalid search_space] '{key}'의 값은 Sequence (list, tuple 등) 여야 합니다. "
                f"현재 타입: {type(value).__name__}, 값: {value}"
            )

    print("[✅ Valid search_space] 모든 값이 유효한 시퀀스입니다.")


def get_search_space_len(search_space: dict) -> int:
    """
    주어진 검색 공간의 길이를 계산합니다.

    Args:
        search_space (dict): 검색 공간을 나타내는 딕셔너리

    Returns:
        int: 검색 공간의 길이
    """
    # 각 키의 가능한 값 개수 출력 및 전체 조합 계산

    _validate_search_space(search_space)
    param_lengths = {k: len(v) for k, v in search_space.items()}
    total_combinations = 1
    for k, length in param_lengths.items():
        print(f"{k:25s}: {length:>3}개")
        total_combinations *= length

    print(f"\n✅ 총 조합 수: {total_combinations:,}")

    return total_combinations


if __name__ == "__main__":
    # 예시 검색 공간
    search_space = {
        "holding_period": list(range(2, 300)),
        "buy_threshold": [0.01, 0.02, 0.03],
        "sell_threshold": [0.01, 0.02],
        "stop_loss": [0.05, 0.1],
    }

    # 검색 공간 길이 계산
    total_combinations = get_search_space_len(search_space)
    print(f"총 조합 수: {total_combinations}")