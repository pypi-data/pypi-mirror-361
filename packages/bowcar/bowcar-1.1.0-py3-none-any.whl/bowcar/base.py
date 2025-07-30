from typing import Union

class BowCarBase:
    """
    모든 BowCar 모드의 기반이 되는 추상 베이스 클래스입니다.
    이 클래스는 직접 객체로 만들지 않으며, LiveBowCar와 GenerateBowCar가 상속받아
    각자의 방식으로 메소드를 구현하는 '설계도' 역할을 합니다.
    """

    # --- LED 제어 메소드 ---
    def red_on(self):
        """빨간색 LED를 켭니다."""
        raise NotImplementedError

    def red_off(self):
        """빨간색 LED를 끕니다."""
        raise NotImplementedError

    def blue_on(self):
        """파란색 LED를 켭니다."""
        raise NotImplementedError

    def blue_off(self):
        """파란색 LED를 끕니다."""
        raise NotImplementedError

    def all_light_on(self):
        """모든 LED를 켭니다."""
        raise NotImplementedError

    def all_light_off(self):
        """모든 LED를 끕니다."""
        raise NotImplementedError

    # --- 부저 제어 메소드 ---
    def buzzer_on(self, scale: str = "C0", octave: int = 4, note: int = 4):
        """지정한 음계와 옥타브로 버저를 울립니다."""
        raise NotImplementedError

    def buzzer_off(self):
        """버저를 끕니다."""
        raise NotImplementedError

    # --- 설정 메소드 ---
    def set_duration(self, time: int = 2000):
        """버저 소리의 기본 지속 시간을 설정합니다. (밀리초 단위)"""
        raise NotImplementedError

    def set_speed(self, type: str = 'a', speed: int = 100):
        """모터의 속도를 설정합니다. (0-255)"""
        raise NotImplementedError

    def set_direction(self, type: str = 'a', dir: str = 'f'):
        """모터의 방향을 설정합니다. ('f': 전진, 'b': 후진)"""
        raise NotImplementedError

    # --- 센서 값 비교 메소드 ---
    def is_light(self, type: str = 'u', thresehold: int = 500) -> Union[bool, str]:
        """조도 센서 값이 임계값보다 위(u) 또는 아래(d)인지 확인합니다."""
        raise NotImplementedError

    def is_push(self, type: str = 'u') -> Union[bool,str]:
        """버튼(u, d, l, r)이 눌렸는지 확인합니다."""
        raise NotImplementedError

    def is_sound(self, type: str = 'u', thresehold: int = 500) -> Union[bool,str]:
        """소리 센서 값이 임계값보다 위(u) 또는 아래(d)인지 확인합니다."""
        raise NotImplementedError

    def is_line(self, dir: str = 'l', type: str = 'u', thresehold: int = 500) -> Union[bool,str]:
        """IR 센서(l, r) 값이 임계값보다 위(u) 또는 아래(d)인지 확인합니다."""
        raise NotImplementedError

    def distance(self, type: str = 'u', thresehold: int = 10) -> Union[bool,str]:
        """초음파 센서의 거리가 임계값보다 위(u) 또는 아래(d)인지 확인합니다."""
        raise NotImplementedError

    # --- 센서 값 직접 가져오기 메소드 ---
    def get_light(self) -> Union[int,str]:
        """조도 센서의 현재 값을 가져옵니다."""
        raise NotImplementedError

    def get_button(self, type: str = 'u') -> Union[int,str]:
        """버튼(u, d, l, r)의 현재 상태 값을 가져옵니다."""
        raise NotImplementedError

    def get_sound(self) -> Union[int,str]:
        """소리 센서의 현재 값을 가져옵니다."""
        raise NotImplementedError

    def get_line(self, dir: str = 'l') -> Union[int,str]:
        """IR 센서(l, r)의 현재 값을 가져옵니다."""
        raise NotImplementedError

    def get_distance(self) -> Union[float,str]:
        """초음파 센서로 측정한 현재 거리를 cm 단위로 가져옵니다."""
        raise NotImplementedError

    # --- 시간 제어 메소드 ---
    def delay(self, ms: int):
        """지정된 시간(밀리초)만큼 프로그램을 지연시킵니다."""
        raise NotImplementedError