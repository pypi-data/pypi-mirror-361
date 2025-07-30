class DataclassPrettyStrMixin:
    """
    dataclass에 상속하여 __str__ 메서드를 자동으로 구현해주는 믹스인 클래스입니다.

    이 믹스인을 상속받은 dataclass는 인스턴스 출력 시
    필드명과 값을 보기 쉽게 예쁘게 포맷팅하여 문자열로 반환합니다.

    특징:
    - dataclass 필드명과 해당 값들을 모두 출력
    - 마지막 필드 앞의 구분자를 ├에서 └로 변경하여 가독성 향상
    - dataclass가 아닌 클래스에 적용하면 AttributeError 발생 가능

    사용 예:
        @dataclass
        class MyData(DataclassPrettyStrMixin):
            a: int
            b: str

        print(MyData(1, "test"))
    """

    def __str__(self) -> str:
        """
        dataclass 필드와 값을 예쁘게 포맷팅하여 반환합니다.

        Returns:
            str: 클래스명과 필드들을 계층 구조처럼 보기 쉽게 나열한 문자열
        """
        # dataclass 필드명 목록을 순회하며 "  ├ 필드명: 값" 형태 문자열 생성
        fields = [f"  ├ {field}: {getattr(self, field)}" for field in self.__dataclass_fields__]

        # 필드가 하나 이상이면 마지막 필드 구분자를 └로 변경하여 마감 표시
        if fields:
            fields[-1] = fields[-1].replace("├", "└")

        # 클래스명과 함께 완성된 문자열 반환
        return f"[{self.__class__.__name__}]\n" + "\n".join(fields)

if __name__ == "__main__":
    from dataclasses import dataclass

    @dataclass
    class ExampleData(DataclassPrettyStrMixin):
        name: str
        value: int
        description: str

    example = ExampleData(name="Test", value=42, description="This is a test instance.")
    print(example)