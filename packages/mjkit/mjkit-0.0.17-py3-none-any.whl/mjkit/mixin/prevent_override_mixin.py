from abc import abstractmethod, ABC
from typing import Tuple
from mjkit.utiles import get_logger
import logging



class PreventOverrideMixin(ABC):
    """
    특정 메서드의 오버라이드를 금지하기 위한 Mixin입니다.

    - 하위 클래스는 @property로 'forbidden_methods'를 정의해야 합니다.
    - Mixin을 직접 상속한 클래스(Base 등)는 검사 대상에서 제외됩니다.
    """

    # ✅ 클래스 전용 로거
    _prevent_override_logger = get_logger(__name__, logging.INFO)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._prevent_override_logger.debug(f"🔍 '{cls.__name__}'에 대해 PreventOverrideMixin 검사 시작")

        if cls._is_direct_subclass_of_mixin():
            cls._prevent_override_logger.debug(f"⏭️ '{cls.__name__}'은 직접 상속 클래스이므로 검사 생략")
            return

        forbidden = cls._get_forbidden_methods()
        cls._prevent_override_logger.debug(f"🚫 '{cls.__name__}'에서 금지된 메서드 목록: {forbidden}")

        cls._check_override_forbidden_methods(forbidden)
        cls._prevent_override_logger.info(f"✅ '{cls.__name__}' 오버라이드 검증 통과 (검사 메서드: {', '.join(forbidden)})\n")

    @classmethod
    def _is_direct_subclass_of_mixin(cls) -> bool:
        """
        현재 클래스가 PreventOverrideMixin을 직접 상속한 클래스인지 확인합니다.

        Returns:
            bool: True이면 검사 제외 대상입니다 (예: BasePlotter 등)
        """
        is_direct = PreventOverrideMixin in cls.__bases__
        cls._prevent_override_logger.debug(f"🧬 {cls.__name__} → 직접 상속 여부: {is_direct}")
        return is_direct

    @classmethod
    def _get_forbidden_methods(cls) -> Tuple[str, ...]:
        """
        클래스에서 'forbidden_methods' 속성을 안전하게 조회하여 금지된 메서드 이름 목록을 반환합니다.
        """
        attr = cls._get_forbidden_methods_attr()
        methods = cls._resolve_forbidden_methods_value(attr)
        cls._validate_forbidden_methods_type(methods)
        return methods

    @classmethod
    def _get_forbidden_methods_attr(cls):
        """
        'forbidden_methods' 속성을 클래스에서 조회합니다.
        없으면 예외를 발생시킵니다.
        """
        attr = getattr(cls, "forbidden_methods", None)
        if attr is None:
            raise TypeError(f"{cls.__name__}는 forbidden_methods를 정의해야 합니다.")
        return attr

    @classmethod
    def _resolve_forbidden_methods_value(cls, attr):
        """
        'forbidden_methods'가 호출 가능(callable)이면 호출하여 값을 얻고,
        그렇지 않으면 그대로 반환합니다.

        호출 실패 시 예외를 발생시킵니다.
        """
        if callable(attr):
            try:
                return attr()
            except Exception as e:
                raise TypeError(f"forbidden_methods 호출 실패: {e}")
        return attr

    @classmethod
    def _validate_forbidden_methods_type(cls, methods):
        """
        'forbidden_methods' 반환값이 튜플인지 확인합니다.
        튜플이 아니면 예외를 발생시킵니다.
        """
        if not isinstance(methods, tuple):
            raise TypeError(f"forbidden_methods는 tuple이어야 합니다. 반환 타입: {type(methods)} (값: {methods})")

    @classmethod
    def _check_override_forbidden_methods(cls, forbidden: Tuple[str, ...]) -> None:
        """
        금지된 메서드가 실제로 하위 클래스에서 override 되었는지 검사합니다.

        Args:
            forbidden (Tuple[str, ...]): override 금지 메서드 목록

        Raises:
            TypeError: 금지된 메서드가 override된 경우
        """
        for method in forbidden:
            if method in cls.__dict__:
                cls._prevent_override_logger.error(
                    f"❌ {cls.__name__}.{method}()는 override 금지 메서드입니다."
                )
                raise TypeError(f"{cls.__name__}.{method}()는 override할 수 없습니다.")
            else:
                cls._prevent_override_logger.debug(f"🔒 {cls.__name__}.{method}() → OK (override 없음)")

    @classmethod
    @abstractmethod
    def forbidden_methods(cls) -> Tuple[str, ...]:
        """
        오버라이드를 금지할 메서드 이름을 정의합니다.

        Returns:
            Tuple[str, ...]: 금지된 메서드 이름 목록 (예: ('draw',))
        """
        raise NotImplementedError(f"{cls.__class__.__name__} 클래스는 'forbidden_methods' @classmethod 구현해야 합니다.")

if __name__ == "__main__":
    from abc import ABC, abstractmethod


    class AbstractTest(ABC):
        """
        PreventOverrideMixin을 상속받는 추상 클래스 예시입니다.
        """


        def draw(self):
            print("draw")

        @abstractmethod
        def save(self):
            pass

    class PassClass(AbstractTest, PreventOverrideMixin):

        @classmethod
        def forbidden_methods(cls) -> Tuple[str, ...]:
            """
            오버라이드를 금지할 메서드 목록을 정의합니다.
            """
            return ("save")

        def save(self):
            print("save")

    class OverridedClass(PassClass):

        def save(self):
            print("오버라이드")



    p = PassClass()
    o = OverridedClass()

