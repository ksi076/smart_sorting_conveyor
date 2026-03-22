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

# 각도에 따른 서보모터 제어 함수  (원하는 각도로 움직이는 함수)
def set_servo_angle(servo, angle):
    duty = 2 + (angle / 18)  # 각도를 PWM 신호로 변환 (서보모터는 각도를 직접받는게 아닌 PWM 듀비티를 받음)
    servo.ChangeDutyCycle(duty)                     #0도 -> 2, 90도 -> 7, 180도 -> 12
    time.sleep(0.5)  # 서보모터가 움직일 시간을 줌
    servo.ChangeDutyCycle(0)  # 서보모터를 멈춤

# 카메라 설정 (로지텍 웹캠 C920)
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 360)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 270)

# 카메라 입력은 360 x 270으로 받고 출력은 720 x 540으로 키워서 보여줌
RE_width = 720   
RE_height = 540

# 중복 데이터 리스트 (이게 없으면 같은 QR코드가 카메라 앞에 계속 보이는 동안 매 프레임마다 인식됨)
ex_data = [] 
do = None      # ex) 서울특별시,인천광역시,경기도
si = None      # ex) 종로구, 중구, 수원시
reset_QR = 0        # 중복방지 리스트를 언제 초기화할지 세기위한 변수

try:
    while cv2.waitKey(41) < 0:   # 약 41ms마다 한번 반복, 1초에 24번정도의 루프 발생
        ret, frame = capture.read()   # ret : 읽기성공여부, frame: 실제 영상 이미지(현재카메라가 보고있는 이미지)
        if not ret:
            break

        GRAY_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # QR코드는 흑벡으로도 충분하기 때문에 컬러프레임->흑백이미지 변환 (속도상승)
        RE_frame = cv2.resize(GRAY_frame, (RE_width, RE_height), interpolation=cv2.INTER_LINEAR) # 흑백프레임 720 x 540 크기로 확대(화면에서 보기 편하도록)
        cv2.imshow("VideoFrame", RE_frame)

        qr = cv2.QRCodeDetector()  # openCV의 QR코드 검출기 객체 생성 (QR코드를 찾아주고, 안의 문자열도 읽어줌)
        data, box, straight_qrcode = qr.detectAndDecode(GRAY_frame) # data: QR안의 문자열, box: QR의 위치좌표, straight_qrcode : 보정된 QR이미지

        if data not in ex_data:   # 중복방지 (현재 읽은 QR데이터가 이전에 처리한적 없는 값이면 실행)
            print(data) # 디버깅용
            ex_data.append(data)    # 읽은 QR데이터 중복방지 리스트에 추가 -> 이제 같은 QR이 보여도 바로 처리 X 
            qr_num = "%s" % data    # 읽어온 QR 데이터를 문자열 형식으로 저장

            if qr_num[0:2] == "00":  # 광역자치단체 
                do = "서울특별시"     #(QR문자열 앞의 두자리가 00 이면)
            elif qr_num[0:2] == "03": 
                do = "인천광역시"     #(QR문자열 앞의 두자리가 03 이면)  
            elif qr_num[0:2] == "08":
                do = "경기도"        #(QR문자열 앞의 두자리가 08 이면)  

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

            if do is not None and si is not None: # QR앞자리는 맞았는데 뒷자리가 등록되지 않은 값일경우 모터동작X
                print(do + " " + si)

                # 서보모터 제어
                if do == "경기도":
                    set_servo_angle(servo1, 90)  # 1번 서보모터를 90도로 회
                    time.sleep(5)
                    set_servo_angle(servo1, 0)   # 5초 대기후 원점복귀
                    
                elif do == "서울특별시":
                    set_servo_angle(servo2, 90)  # 2번 서보모터를 90도로 회전
                    time.sleep(5)
                    set_servo_angle(servo2, 0)   # 5초 대기후 원점복귀

                reset_QR = 0  # 새로운 QR을 처리 했으니 중복방지 타이머를 초기화
                do = None    #값 초기화
                si = None

        reset_QR += 1   # 반복문이 한번 돌때마다 카운터 1증가
        if reset_QR == 96:  # 96이 되었을때 중복방지 리스트 초기화 (41ms마다 한번이기 때문에 약 4초마다 초기화)
            ex_data = []

finally:
    servo1.stop()
    servo2.stop()
    GPIO.cleanup()  # GPIO 설정 정리
    capture.release()
    cv2.destroyAllWindows()
