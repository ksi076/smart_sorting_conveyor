import cv2
import RPi.GPIO as GPIO
import time

# 서보모터 제어를 위한 핀 번호 설정
servo1_pin = 17  # GPIO 17 (서보모터 1 연결)
servo2_pin = 18  # GPIO 18 (서보모터 2 연결)

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)

# PWM 객체 생성 (50Hz 주파수, 서보모터용)
servo1 = GPIO.PWM(servo1_pin, 50)
servo2 = GPIO.PWM(servo2_pin, 50)

# 서보모터 초기 위치 설정
servo1.start(0)  # 서보 1의 PWM 신호 시작
servo2.start(0)  # 서보 2의 PWM 신호 시작

# 각도에 따른 서보모터 제어 함수
def set_servo_angle(servo, angle):
    duty = 2 + (angle / 18)  # 각도를 PWM 신호로 변환
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)  # 서보모터가 움직일 시간을 줌
    servo.ChangeDutyCycle(0)  # 서보모터를 멈춤

# 카메라 설정
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 360)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 270)

RE_width = 720
RE_height = 540

# 중복 데이터 리스트
ex_data = []
do = None
si = None
reset_QR = 0

try:
    while cv2.waitKey(41) < 0:
        ret, frame = capture.read()
        if not ret:
            break

        GRAY_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        RE_frame = cv2.resize(GRAY_frame, (RE_width, RE_height), interpolation=cv2.INTER_LINEAR)
        cv2.imshow("VideoFrame", RE_frame)

        qr = cv2.QRCodeDetector()
        data, box, straight_qrcode = qr.detectAndDecode(GRAY_frame)

        if data not in ex_data:
            print(data)
            ex_data.append(data)
            qr_num = "%s" % data

            if qr_num[0:2] == "00":  # 광역자치단체
                do = "서울특별시"
            elif qr_num[0:2] == "03":
                do = "인천광역시"
            elif qr_num[0:2] == "08":
                do = "경기도"

            if do == "서울특별시":  # 서울특별시 기초자치단체
                if qr_num[2:4] == "00":
                    si = "종로구"
                elif qr_num[2:4] == "01":
                    si = "중구"
                elif qr_num[2:4] == "02":
                    si = "용산구"
            elif do == "인천광역시":  # 인천광역시 기초자치단체
                if qr_num[2:4] == "00":
                    si = "중구"
                elif qr_num[2:4] == "01":
                    si = "동구"
                elif qr_num[2:4] == "02":
                    si = "미추홀구"
            elif do == "경기도":  # 경기도 기초자치단체
                if qr_num[2:4] == "01":
                    si = "수원시"
                elif qr_num[2:4] == "04":
                    si = "광명시"
                elif qr_num[2:4] == "13":
                    si = "시흥시"

            if do is not None and si is not None:
                print(do + " " + si)

                # 서보모터 제어
                if do == "경기도":
                    set_servo_angle(servo1, 90)  # 1번 서보모터를 90도로 회전
                elif do == "서울특별시":
                    set_servo_angle(servo2, 90)  # 2번 서보모터를 90도로 회전

                reset_QR = 0
                do = None
                si = None

        reset_QR += 1
        if reset_QR == 96:
            ex_data = []

finally:
    servo1.stop()
    servo2.stop()
    GPIO.cleanup()  # GPIO 설정 정리
    capture.release()
    cv2.destroyAllWindows()