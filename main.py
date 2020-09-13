import os
import time
from lib.pn532.spi import PN532_SPI
import RPi.GPIO as GPIO
from lib.servo.Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor, Raspi_StepperMotor
import time
import atexit
from event_bus import EventBus
from lib.waveshare_epd import epd2in7
from PIL import Image,ImageDraw,ImageFont

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')


DEFAULT_BELT_DRIVE_TIME = os.environ.get('DEFAULT_BELT_DRIVE_TIME') or 2
CATS_ALLOWED_TO_EAT = (os.environ.get('CATS_ALLOWED_TO_EAT') or 'lola').split(' ')
bus = EventBus()
draw = None
font24 = None

@bus.on('cat-detected')
def on_cat_detected_check_id(id):
    print('on_cat_detected_check_id', id)
    draw.text((10, 0), 'hello ' + id, font = font24, fill = 0)
    # if id in CATS_ALLOWED_TO_EAT:
    bus.emit('start-belt', DEFAULT_BELT_DRIVE_TIME)
    # else:
    #     print(id, 'not allowed to eat')


@bus.on('start-belt')
def on_start_belt(timeout):
    print('on_start_belt', timeout)
    print("Interleaved coil steps")
    myStepper.step(200, Raspi_MotorHAT.FORWARD, Raspi_MotorHAT.INTERLEAVE)
    time.sleep(timeout)
    bus.emit('stop-belt')


@bus.on('stop-belt')
def on_stop_belt():
    print('on_stop_belt')
    draw.text((10, 0), 'Done! ', font=font24, fill=0)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(2).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(3).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(4).run(Raspi_MotorHAT.RELEASE)

if __name__ == '__main__':
    print('RCF - Reduce Cat Fast\n')
    try:
        print('Connecting the NFC Card\n')
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()
        print('Connecting to the servo')
        mh = Raspi_MotorHAT(0x6F)
        myStepper = mh.getStepper(200, 1)  # 200 steps/rev, motor port #1
        myStepper.setSpeed(30)  # 30 RPM
        atexit.register(turnOffMotors)
        print('Connecting to the e-reader')
        epd = epd2in7.EPD()
        epd.init()
        epd.Clear(0xFF)
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)

        print('Waiting for RFID/NFC card...')
        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=0.5)
            print('.', end="")
            # Try again if no card is available.
            if uid is None:
                continue
            print('Found card with UID:', [hex(i) for i in uid])
            bus.emit('cat-detected', uid)
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
        epd.Dev_exit()
        epd2in7.epdconfig.module_exit()
