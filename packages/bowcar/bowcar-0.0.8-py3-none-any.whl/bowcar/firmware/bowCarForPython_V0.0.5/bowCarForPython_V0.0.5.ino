const int RED_LED_PIN = 10;
const int BLUE_LED_PIN = 11;
const int BUZZER_PIN = 3;
int scale = 0;
int duration = 2000;

const int notes[6][12] = {
  // 1옥타브: C1 ~ B1
  { 33, 35, 37, 39, 41, 44, 46, 49, 52, 55, 58, 62 },
  // 2옥타브: C2 ~ B2
  { 65, 69, 73, 78, 82, 87, 93, 98, 104, 110, 117, 123 },
  // 3옥타브: C3 ~ B3
  { 131, 139, 147, 156, 165, 175, 185, 196, 208, 220, 233, 247 },
  // 4옥타브: C4 ~ B4
  { 262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494 },
  // 5옥타브: C5 ~ B5
  { 523, 554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988 },
  // 6옥타브: C6 ~ B6
  { 1047, 1109, 1175, 1245, 1319, 1397, 1480, 1568, 1661, 1760, 1865, 1976 }
};

void setup() {
  // 시리얼 통신을 9600 속도로 시작합니다.
  Serial.begin(9600); 
  // 아두이노 보드에 내장된 LED를 출력으로 설정합니다.
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(BLUE_LED_PIN, OUTPUT);
}

void loop() {
  // 파이썬으로부터 수신한 데이터가 있는지 확인합니다.
  if (Serial.available() > 0) {
    // 줄바꿈 문자를 만날 때까지 문자열 전체를 읽어옴
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    // 첫글자가 l 인 경우 light를 제어  
    // 두번째 글자가 a인 경우 전부 제어
    if (command[0] == 'l'){
      if(command[1] == 'a'){
        if(command[2] == 'n'){
          digitalWrite(RED_LED_PIN, HIGH);
          digitalWrite(BLUE_LED_PIN, HIGH);
        }else{
          digitalWrite(RED_LED_PIN, LOW);
          digitalWrite(BLUE_LED_PIN, LOW);
        }
      }else if(command[1] == 'r'){
        if(command[2] == 'n'){
          digitalWrite(RED_LED_PIN, HIGH);
        }else{
          digitalWrite(RED_LED_PIN, LOW);
        }
      }else if(command[1] == 'b'){
        if(command[2] == 'n'){
          digitalWrite(BLUE_LED_PIN, HIGH);
        }else{
          digitalWrite(BLUE_LED_PIN, LOW);
        }
      }
    }else if(command[0] == 'b'){
      //첫 글자가 b 인 경우 speaker를 제어
      //두번째 글자가 옥타브(1~6)
      //세번째 글자가 계이름, 네번째 글자가 샵여부('c0 c# d0 d# e0 f0 f# g0 g# a0 a# b0') #도 전부 표현
      switch(command[2]){
        case 'C':
          if(command[3] == '0') scale = 0;
          else scale = 1;
          break;
        case 'D':
          if(command[3] == '0') scale = 2;
          else scale = 3;
          break;
        case 'E':
          scale = 4;
          break;
        case 'F':
          if(command[3] == '0') scale = 5;
          else scale = 6;
          break;
        case 'G':
          if(command[3] == '0') scale = 7;
          else scale = 8;
          break;
        case 'A':
          if(command[3] == '0') scale = 9;
          else scale = 10;
          break;
        case 'B':
          scale = 11;
          break;
        default:
          scale = -1;
          break;
      }
      if(scale == -1){
        noTone(BUZZER_PIN);
      }else{
        tone(BUZZER_PIN, notes[command[1]-'1'][scale], duration/(command[4]-'0')*0.95);
        delay(duration/(command[4]-'0'));
      }
    }else if(command[0] == 's'){
      duration = (command[1]-'0')*10000 + (command[2]-'0')*1000 + (command[3]-'0')*100 + (command[4]-'0')*10 + command[5]-'0';
    }
  }
}