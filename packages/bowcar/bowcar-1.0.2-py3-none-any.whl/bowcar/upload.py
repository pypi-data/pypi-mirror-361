import serial.tools.list_ports
import os
import subprocess
from typing import Optional, Type
from .base import BowCarBase

# 이 클래스에서 사용할 아두이노 보드, 폴더, 파일 이름 정보
FQBN = "arduino:avr:uno"
FOLDER_NAME = "arduino_bowcar"
FILE_NAME = "arduino_bowcar.ino"

# 음계 매핑(옥타브 별)
tones = [
  [ 33, 35, 37, 39, 41, 44, 46, 49, 52, 55, 58, 62 ],
  # 2옥타브: C2 ~ B2
  [ 65, 69, 73, 78, 82, 87, 93, 98, 104, 110, 117, 123 ],
  # 3옥타브: C3 ~ B3
  [ 131, 139, 147, 156, 165, 175, 185, 196, 208, 220, 233, 247 ],
  # 4옥타브: C4 ~ B4
  [ 262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494 ],
  # 5옥타브: C5 ~ B5
  [ 523, 554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988 ],
  # 6옥타브: C6 ~ B6
  [ 1047, 1109, 1175, 1245, 1319, 1397, 1480, 1568, 1661, 1760, 1865, 1976 ]
]

# 음계 매핑 딕셔너리
SCALE_MAPPING = {
    "C0": 0, "C#": 1, "D0": 2, "D#": 3, "E0": 4, "F0": 5, "F#": 6,
    "G0": 7, "G#": 8, "A0": 9, "A#": 10, "B0": 11
}

class UploadBowCar(BowCarBase):
    """
    파이썬 코드를 아두이노 C++ 코드로 생성하고 업로드하는 클래스입니다.
    """
    def __init__(self):
        self.declarations:set[str] = set() # 전역 선언 (라이브러리, 변수 등)
        self.setup_code:str = ""      # setup() 블록에 들어갈 코드
        self.loop_code:str = ""       # loop() 블록에 들어갈 코드
        self._indent_level:int = 1    # 코드 구조를 위한 들여쓰기 수준
        print("코드 생성 모드로 시작합니다.")

    def _get_indent(self):
        """현재 들여쓰기 수준에 맞는 공백을 반환합니다."""
        return "  " * self._indent_level

    # --- 범용 컨텍스트 매니저 ---
    class _BlockManager:
        def __init__(self, car_instance: 'UploadBowCar', open_clause:str):
            self.car = car_instance
            self.open_clause = open_clause

        def __enter__(self):
            self.car.loop_code += f"{self.car._get_indent()}{self.open_clause} {{\n"
            self.car._indent_level += 1

        def __exit__(self, exc_type: Optional[Type[BaseException]],
                    exc_val:Optional[BaseException],
                    exc_tb:object):
            self.car._indent_level -= 1
            self.car.loop_code += f"{self.car._get_indent()}}}\n"

    # --- 사용자 호출 메소드 (BowCarBase 구현) ---

    def _add_pin_mode(self, pin_name:str, mode:str):
        """pinMode 코드를 setup_code에 추가합니다 (중복 방지)."""
        pin_mode_line = f"  pinMode({pin_name}, {mode});\n"
        if pin_mode_line not in self.setup_code:
            self.setup_code += pin_mode_line
    
    def _add_value(self, type:str, name:str, initial_val=None): #type:ignore
        """
        전역 번수 선언을 중복 없이 추가합니다.
        예: _add_value("int", "sensorValue", 0) -> "int sensorValue = 0;"
        """
        command = f"{type} {name}"
        if initial_val is not None:
            command += f" = {initial_val}"
        command += ";"

        self.declarations.add(command)
    
    def red_on(self):
        self._add_pin_mode("RED_LED_PIN", "OUTPUT")
        self.loop_code += f"{self._get_indent()}digitalWrite(RED_LED_PIN, HIGH);\n"

    def red_off(self):
        self._add_pin_mode("RED_LED_PIN", "OUTPUT")
        self.loop_code += f"{self._get_indent()}digitalWrite(RED_LED_PIN, LOW);\n"

    def blue_on(self):
        self._add_pin_mode("BLUE_LED_PIN", "OUTPUT")
        self.loop_code += f"{self._get_indent()}digitalWrite(BLUE_LED_PIN, HIGH);\n"

    def blue_off(self):
        self._add_pin_mode("BLUE_LED_PIN", "OUTPUT")
        self.loop_code += f"{self._get_indent()}digitalWrite(BLUE_LED_PIN, LOW);\n"
        
    def all_light_on(self):
        self.red_on()
        self.blue_on()

    def all_light_off(self):
        self.red_off()
        self.blue_off()

    def buzzer_on(self, scale: str = "C0", octave: int = 4, note = 0): #type:ignore
        if not 1 <= octave <= 6:
            print(f"오류: 옥타브는 1에서 6 사이여야 합니다. (입력값: {octave})")
            return
        if scale not in SCALE_MAPPING:
            print(f"오류: 음계는 C0~B0 식으로 설정해야 합니다. (입력값: {scale})")
            return
        
        self._add_pin_mode("BUZZER_PIN", "OUTPUT")
        frequency = tones[octave - 1][SCALE_MAPPING[scale]]
        command = f"tone(BUZZER_PIN, {frequency}"
        if note > 0:
            command += f", (float)duration/{note}*0.95"
        command += ");"

        self.loop_code += f"{self._get_indent()}{command}\n"

    def buzzer_off(self):
        self.loop_code += f"{self._get_indent()}noTone(BUZZER_PIN);\n"

    def set_duration(self, time:int=2000):
        self.loop_code += f"duration = {time};\n"

        
    def set_speed(self, type: str = 'a', speed): #type: ignore
        
        if type in ('l', 'a'):
            self._add_pin_mode("LM_PWM_PIN", "OUTPUT")
            self.loop_code += f"{self._get_indent()}analogWrite(LM_PWM_PIN, {speed});\n"
        if type in ('r', 'a'):
            self._add_pin_mode("RM_PWM_PIN", "OUTPUT")
            self.loop_code += f"{self._get_indent()}analogWrite(RM_PWM_PIN, {speed});\n"

    def set_direction(self, type: str = 'a', dir: str = 'f'):
        direction_code = '0' if dir == 'f' else '1'
        if type in ('l', 'a'):
            self._add_pin_mode("LM_DIR_PIN", "OUTPUT")
            self.loop_code += f"{self._get_indent()}digitalWrite(LM_DIR_PIN, {direction_code});\n"
        if type in ('r', 'a'):
            self._add_pin_mode("RM_DIR_PIN", "OUTPUT")
            self.loop_code += f"{self._get_indent()}digitalWrite(RM_DIR_PIN, {direction_code});\n"

    # --- 센서 값/조건을 C++ 코드로 반환하는 메소드 ---
    def get_light(self) -> str:
        self._add_pin_mode("LS_PIN", "INPUT")
        return "analogRead(LS_PIN)"

    def get_distance(self) -> str:
        # 실제 초음파 거리 계산 함수를 아두이노 코드에 추가해야 함
        self._add_pin_mode("TRIG_PIN","OUTPUT")
        self._add_pin_mode("ECHO_PIN","INPUT")
        
        Dist_Code = '''
long Distance() {
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long dura = pulseIn(ECHO_PIN, HIGH);
    long dist = dura / 29 / 2;
    return dist;
}
'''

        self.declarations.add(Dist_Code)
        return "Distance()"

    def is_push(self, type: str = 'u') -> str:
        pin_map = {'u': "UB_PIN", 'd': "DB_PIN", 'l': "LB_PIN", 'r': "RB_PIN"}
        return f"(digitalRead({pin_map.get(type, 'UB_PIN')}) == LOW)" # 풀업 저항 기준

    # --- 제어문 빌더 ---
    def bfor(self, condition: str):
        return self._BlockManager(self, f"for ({condition})")

    def bif(self, condition: str):
        cpp_condition = self._translate_condition(condition)
        return self._BlockManager(self, f"if ({cpp_condition})")

    def belif(self, condition: str):
        cpp_condition = self._translate_condition(condition)
        return self._BlockManager(self, f"else if ({cpp_condition})")

    def belse(self):
        return self._BlockManager(self, "else")
    
    def bwhile(self, condition: str = ""): #type: ignore
        cpp_condition = self._translate_condition(condition)
        return self._BlockManager(self, f"while ({cpp_condition})")

    def _translate_condition(self, condition: str) -> str:
        """파이썬 조건문 문자열을 C++ 형식으로 변환하는 헬퍼 메소드"""
        py_to_cpp_ops = {
            "and": "&&",
            "or": "||",
            "not": "!",
            # True/False도 C++에 맞게 소문자로 변경
            "True": "true", 
            "False": "false"
        }
        # 1. 공백을 기준으로 단어를 분리합니다.
        words = condition.split(' ')
        
        # 2. 각 단어를 확인하며 C++ 연산자로 치환합니다.
        cpp_words = [py_to_cpp_ops.get(word, word) for word in words]
        
        # 3. 다시 하나의 문자열로 합칩니다.
        return ' '.join(cpp_words)

    def delay(self, ms): # type: ignore
        self.loop_code += f"{self._get_indent()}delay({ms});\n"

    def bbreak(self): # 브레이크 설정
        self.loop_code += f"{self._get_indent()}break;\n"

    def set_value(self, type:str = 'int', name:str = 'x', val = None): #type: ignore
        self._add_value(type, name) #type:ignore
        if isinstance(val, str):
            self.loop_code += f"{name} = '{val}';\n"
        else:    
            self.loop_code += f"{name} = {val};\n"

    # --- 코드 생성 및 업로드 ---
    def get_full_code(self):
        """모든 코드 버퍼를 합쳐 완전한 .ino 코드를 생성합니다."""
        # 여기에 필요한 전역 변수, 핀 번호 등을 추가
        initial_definitions = "// Auto-generated by BowCar\n#include <Arduino.h>\n\n"
        pin_definitions = '''
// Arduino pin numbers for BowCar
// 바우카를 위한 아두이노 핀 번호

// LED control pins
const int RED_LED_PIN =10;
const int BLUE_LED_PIN =11;

// Ultrasonic sensor pins
const int TRIG_PIN =13;
const int ECHO_PIN =12;

// IR sensor pins
const int IRL_PIN =A6;
const int IRR_PIN =A7;

// Sound sensor pin
const int SS_PIN =A3;

// Buzzer pin
const int BUZZER_PIN =3;

// Light Sensor
const int LS_PIN = A2;

// Motor control pins
const int LM_DIR_PIN =2;
const int LM_PWM_PIN =5;

const int RM_DIR_PIN =4;
const int RM_PWM_PIN =6;

// Button pin
const int UB_PIN =A0;
const int DB_PIN =A1;
const int LB_PIN =7;
const int RB_PIN =8;

int duration = 2000;
'''
        
        full_code = (
            initial_definitions +
            pin_definitions +
            "\n".join(self.declarations) + "\n\n"
            "void setup() {\n"
            "  Serial.begin(9600);\n"
            + self.setup_code +
            "}\n\n"
            "void loop() {\n"
            + self.loop_code +
            "}\n"
        )
        return full_code

    def _find_arduino_port(self):
        """아두이노 포트를 찾아 반환하고, 없으면 None을 반환합니다."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description or 'CH340' in port.description:
                print(f"아두이노 발견: {port.device}")
                return port.device
        print('아두이노를 찾을 수 없습니다!')
        return None

    def upload_code(self):
        """생성된 코드를 .ino 파일로 만들고 아두이노에 업로드합니다."""
        myPort = self._find_arduino_port()
        if not myPort:
            print("업로드를 중지합니다.")
            return

        full_code = self.get_full_code()

        try:
            os.makedirs(FOLDER_NAME, exist_ok=True)
            full_path = os.path.join(FOLDER_NAME, FILE_NAME)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(full_code)
            print(f"'{full_path}' 파일 생성 완료!")
            
            
            # arduino-cli를 사용한 컴파일 및 업로드
            compile_command: list[str] = [
                'arduino-cli', 'compile',
                '--fqbn', 'arduino:avr:uno',  # 보드 유형을 지정합니다. (예: Arduino Uno)
                full_path, '--clean'
            ]
            upload_command: list[str] = [
                'arduino-cli', 'upload', 
                '--port', str(myPort),
                '--fqbn', 'arduino:avr:uno',  # 보드 유형을 지정합니다. (예: Arduino Uno)
                full_path
            ]
            print("코드 컴파일 및 업로드 시작...")
            # ... (subprocess 호출 로직) ...
            try:
                result = subprocess.run(  # arduino-cli 명령어 실행
                    compile_command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                print(result.stdout.decode('utf-8'))  # 업로드 성공 메시지 출력
                result = subprocess.run(
                    upload_command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                print("코드 업로드 성공! Code upload successful!")
                print(result.stdout.decode('utf-8'))  # 업로드 성공 메시지 출력
            except subprocess.CalledProcessError as e:
                print(f"업로드 실패: {e}")
            
        except Exception as e:
            print(f"코드 생성 또는 업로드 중 오류 발생: {e}")