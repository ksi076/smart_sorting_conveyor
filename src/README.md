## 🧠 기능 세분화

---

### 1️⃣ 초기 설정 (GPIO 및 서보모터 초기화)

```python
import cv2                  # openCV 라이브러리
import RPi.GPIO as GPIO     # GPIO제어 라이브러리
import time                 # 서보모터가 실제로 움직일 시간을 주기위해 사용

# 서보모터 제어를 위한 핀 번호 설정
servo1_pin = 17  # GPIO 17 (서보모터 1 연결)
servo2_pin = 18  # GPIO 18 (서보모터 2 연결)

# GPIO 설정
GPIO.setmode(GPIO.BCM)              #물리핀번호가 아닌 BCM방식으로 사용
GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)    # 서보모터 핀을 출력모드로 설정(라즈베리가 신호를 보내줘야함)

# PWM 객체 생성 (50Hz 주파수, 서보모터용)
servo1 = GPIO.PWM(servo1_pin, 50)
servo2 = GPIO.PWM(servo2_pin, 50)

# 서보모터 초기 위치 설정
servo1.start(0)  # 서보 1의 PWM 신호 시작
servo2.start(0)  # 서보 2의 PWM 신호 시작  
```
---

### 2️⃣ 입력 처리

- **카메라 프레임 입력:**
  ○ read_frame 함수로 실시간 영상 획득  

- **전처리:**
  ○ resize_frame으로 YOLO 입력 크기 조정  

---

### 3️⃣ 객체 및 위반 감지

- **객체 탐지:**
  ○ predict 함수로 YOLO 추론 수행  
  ○ 사람(person), 차량(car, bus, truck) 인식  

- **무단 횡단 감지:**
  ○ check_jaywalk 함수로 제한 구역 내 사람 확인  

- **불법 주정차 감지:**
  ○ check_illegal_parking 함수로 일정 시간 정지 차량 판단  

- **불법 유턴 감지:**
  ○ check_illegal_uturn 함수로 이동 방향 변화 분석  

---

### 4️⃣ 결과 처리

- **화면 출력:**
  ○ draw_box 함수로 bbox 및 라벨 표시  

- **이미지 저장:**
  ○ save_image 함수로 이벤트 이미지 저장  

- **DB 저장:**
  ○ save_db 함수로 로그 기록  
    ■ 시간 (detected_at)  
    ■ 이벤트 종류 (event_type)  
    ■ 이미지 경로 (image_path)  

---

### 5️⃣ 예외 처리 및 추가 기능

- **무시 영역 설정:**
  ○ ignore_zone 함수로 특정 영역 사람 감지 제외  

- **중복 방지:**
  ○ duplicate_limit으로 일정 시간 내 중복 카운트 방지  

- **비상 모드:**
  ○ emergency_mode 실행 시 15초 유지  
  ○ 'J' 키 입력 시 해제  

- **오류 처리:**
  ○ 카메라 오류 및 파일 저장 오류 대응  

