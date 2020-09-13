import os
import time
from event_bus import EventBus

DEFAULT_BELT_DRIVE_TIME = os.environ.get('DEFAULT_BELT_DRIVE_TIME') or 2
CATS_ALLOWED_TO_EAT = (os.environ.get('CATS_ALLOWED_TO_EAT') or 'lola').split(' ')
bus = EventBus()

@bus.on('cat-detected')
def on_cat_detected_check_id(id):
    print('on_cat_detected_check_id', id)
    if id in CATS_ALLOWED_TO_EAT:
        bus.emit('start-belt', DEFAULT_BELT_DRIVE_TIME)
    else:
        print(id, 'not allowed to eat')

@bus.on('start-belt')
def on_start_belt(timeout):
    print('on_start_belt', timeout)
    time.sleep(timeout)
    bus.emit('stop-belt')

@bus.on('stop-belt')
def on_stop_belt():
    print('on_stop_belt')

if __name__ == '__main__':
    print('RCF - Reduce Cat Fast\n')
    bus.emit('cat-detected', 'lola')
