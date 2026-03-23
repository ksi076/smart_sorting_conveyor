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

### 2️⃣ 서보모터 제어 로직

```python
def set_servo_angle(servo, angle):
    duty = 2 + (angle / 18)  # 각도를 PWM 신호로 변환 (서보모터는 각도를 직접받는게 아닌 PWM 듀비티를 받음)
    servo.ChangeDutyCycle(duty)                     #0도 -> 2, 90도 -> 7, 180도 -> 12
    time.sleep(0.5)  # 서보모터가 움직일 시간을 줌
    servo.ChangeDutyCycle(0)  # 서보모터를 멈춤
```
---

### 3️⃣ 카메라 설정 및 영상 입력

```python
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 360)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 270)
```
---

### 4️⃣ QR 인식 처리

```python
 qr = cv2.QRCodeDetector()  # openCV의 QR코드 검출기 객체 생성 (QR코드를 찾아주고, 안의 문자열도 읽어줌)
        data, box, straight_qrcode = qr.detectAndDecode(GRAY_frame) # data: QR안의 문자열, box: QR의 위치좌표, straight_qrcode : 보정된 QR이미지
```

---

### 5️⃣ 지역 판별 로직(데이터처리)

```python
  f qr_num[0:2] == "00":  # 광역자치단체 
                do = "서울특별시"     #(QR문자열 앞의 두자리가 00 이면)
            elif qr_num[0:2] == "03": 
                do = "인천광역시"     #(QR문자열 앞의 두자리가 03 이면)  
            elif qr_num[0:2] == "08":
                do = "경기도"        #(QR문자열 앞의 두자리가 08 이면) 
```
---

### 6️⃣ 서보모터 동작(분류 실행)

```python
  if do == "경기도":
                    set_servo_angle(servo1, 90)  # 1번 서보모터를 90도로 회
                    time.sleep(5)
                    set_servo_angle(servo1, 0)   # 5초 대기후 원점복귀
                    
                elif do == "서울특별시":
                    set_servo_angle(servo2, 90)  # 2번 서보모터를 90도로 회전
                    time.sleep(5)
                    set_servo_angle(servo2, 0)   # 5초 대기후 원점복귀
```

### 7️⃣ 중복 방지 & 예외 처리

```python
   reset_QR += 1   # 반복문이 한번 돌때마다 카운터 1증가
        if reset_QR == 96:  # 96이 되었을때 중복방지 리스트 초기화 (41ms마다 한번이기 때문에 약 4초마다 초기화)
            ex_data = []
```
---


