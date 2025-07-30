class KwargsValidationMixin:
    """
    필수 키워드 인자가 kwargs에 존재하고 None이 아닌지 검증하는 기능을 제공하는 Mixin 클래스입니다.

    이 Mixin은 여러 클래스에서 kwargs 검증 로직을 재사용할 수 있도록 도와줍니다.

    Methods:
        - validate_required_kwargs(kwargs, required_keys): 필수 키들이 kwargs에 모두 포함되어 있는지 검증

    Example:
        class MyManager(KwargsValidationMixin):
            def run(self, **kwargs):
                self.validate_required_kwargs(kwargs, ["ticker", "date"])
                print("모든 필수 인자 확인 완료")

        manager = MyManager()
        manager.run(ticker="005930", date="20250702")  # ✅ 정상
        manager.run(ticker="005930")  # ❌ ValueError 발생
    """

    def validate_required_kwargs(self, kwargs: dict, required_keys: list[str]) -> None:
        """
        kwargs 딕셔너리 내에 required_keys 리스트에 명시된 키들이 모두 존재하고 None이 아닌지 검사합니다.
        누락된 키가 있다면 ValueError를 발생시킵니다.

        Args:
            kwargs (dict): 키워드 인자 딕셔너리
            required_keys (list[str]): 필수로 존재해야 하는 키 목록

        Raises:
            ValueError: 누락된 키가 있을 경우 발생

        Usage:
            >>> self.validate_required_kwargs({"ticker": "005930", "date": "20250702"}, ["ticker", "date"])
            # 정상 처리

            >>> self.validate_required_kwargs({"ticker": "005930"}, ["ticker", "date"])
            Traceback (most recent call last):
                ...
            ValueError: 다음 필수 인자가 누락되었습니다: ['date']
        """
        missing = [k for k in required_keys if k not in kwargs or kwargs[k] is None]
        if missing:
            raise ValueError(f"다음 필수 인자가 누락되었습니다: {missing}")
