from robot import *

setVersion("2.1")
reset()

LINE_THRESHOLD = 100
CRUISE_SPEED = 100
TURN_SPEED = 30
SEARCH_INNER_SPEED = 55
SEARCH_OUTER_SPEED = 105
OBSTACLE_DISTANCE_CM = 15

MELODY = (523, 659, 784, 659)
DISCO_COLORS = (
    (255, 0, 0),
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 255),
)
DISCO_SETTERS = (
    setDiscoFrontLeft,
    setDiscoFrontRight,
    setDiscoBackLeft,
    setDiscoBackRight,
)

last_turn = 0
last_signaled_turn = 0
loop_count = 0
melody_index = 0
obstacle_active = False


def set_turn_signal(direction):
    global last_signaled_turn

    if direction == last_signaled_turn:
        return

    setHeadlightLeft(1 if direction < 0 else 0)
    setHeadlightRight(1 if direction > 0 else 0)
    last_signaled_turn = direction


def show_disco(step):
    for offset, set_light in enumerate(DISCO_SETTERS):
        color = DISCO_COLORS[(step + offset) % len(DISCO_COLORS)]
        set_light(color[0], color[1], color[2])


while True:
    distance = getDistance()
    if distance != 999 and distance <= OBSTACLE_DISTANCE_CM:
        drive(0)
        if not obstacle_active:
            beep(880, 0.2)
            delay(50)
            beep(660, 0.2)
            obstacle_active = True
            last_signaled_turn = None
        else:
            delay(50)
        continue

    obstacle_active = False

    middle = getSensorMiddle()
    front_left = getSensorFrontLeft()
    front_right = getSensorFrontRight()
    back_left = getSensorBackLeft()
    back_right = getSensorBackRight()

    front_left_on_line = front_left < LINE_THRESHOLD
    front_right_on_line = front_right < LINE_THRESHOLD
    middle_on_line = middle < LINE_THRESHOLD

    if front_left_on_line and not front_right_on_line:
        driveLeft(TURN_SPEED)
        driveRight(CRUISE_SPEED)
        last_turn = -1
        turn = -1
    elif front_right_on_line and not front_left_on_line:
        driveLeft(CRUISE_SPEED)
        driveRight(TURN_SPEED)
        last_turn = 1
        turn = 1
    elif front_left_on_line or middle_on_line:
        drive(CRUISE_SPEED)
        turn = 0
    elif back_left < LINE_THRESHOLD and back_right >= LINE_THRESHOLD:
        # line lost: back sensors show which side it is on
        driveLeft(SEARCH_INNER_SPEED)
        driveRight(SEARCH_OUTER_SPEED)
        last_turn = -1
        turn = -1
    elif back_right < LINE_THRESHOLD and back_left >= LINE_THRESHOLD:
        driveLeft(SEARCH_OUTER_SPEED)
        driveRight(SEARCH_INNER_SPEED)
        last_turn = 1
        turn = 1
    elif last_turn < 0:
        driveLeft(SEARCH_INNER_SPEED)
        driveRight(SEARCH_OUTER_SPEED)
        turn = -1
    elif last_turn > 0:
        driveLeft(SEARCH_OUTER_SPEED)
        driveRight(SEARCH_INNER_SPEED)
        turn = 1
    else:
        drive(SEARCH_INNER_SPEED)
        turn = 0

    set_turn_signal(turn)

    if loop_count % 8 == 0:
        show_disco(loop_count // 8)

    if loop_count % 12 == 0:
        beep(MELODY[melody_index], 0.08)
        melody_index = (melody_index + 1) % len(MELODY)

    loop_count += 1
    delay(5)
