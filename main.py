from itertools import count
from pynput import keyboard
from enum import Enum
import pyautogui as pag

settings = dict(
    PACE_X=20,
    PACE_Y=20,
    PACE_SCROLL=float(1),
    FAST_SCALE=float(5),
    SPECIAL_KEYS={keyboard.Key.shift, keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.alt_r},
    FAST_KEY=keyboard.Key.shift,
    CLICK_KEY=keyboard.Key.enter,
    DOUBLE_CLICK_MODIFIER=keyboard.Key.shift,
    RIGHT_CLICK_MODIFIER=keyboard.Key.ctrl,
    VIMALL_TOGGLE_KEYSET={keyboard.Key.esc},
    SCROLL_KEY=keyboard.Key.space,
    REVERSE_SCROLL=keyboard.Key.shift
)

# stack stores only special keys
stack = []
number_stack = []
activated = True

class Movement(Enum):
    UP = 'k'
    DOWN = 'j'
    LEFT = 'h'
    RIGHT = 'l'
    
    class UnrecognizedKey(Exception):
        
        def __init__(self, msg: str) -> None:
            self.msg = msg
            super().__init__(self.msg)
    
    @staticmethod
    def parse(char: str):
        char = char.lower()
        if char == Movement.UP.value:
            return Movement.UP
        elif char == Movement.DOWN.value:
            return Movement.DOWN
        elif char == Movement.LEFT.value:
            return Movement.LEFT
        elif char == Movement.RIGHT.value:
            return Movement.RIGHT
        else:
            raise Movement.UnrecognizedKey(f'Failed to recognize movement key: {char}')

def move(action: Movement, count: int, scale: float=1):
    if action == Movement.UP or action == Movement.DOWN:
        pace = settings['PACE_X']
        base = (0, scale if action == Movement.DOWN else -scale)
    elif action == Movement.LEFT or action == Movement.RIGHT:
        pace = settings['PACE_Y']
        base = (scale if action == Movement.RIGHT else -scale, 0)
    
    movement = (round(base[0] * pace * count), round(base[1] * pace * count))
    
    pag.moveRel(*movement)

def scroll(action: Movement, count: int, scale: float=1):
    if action == Movement.UP or action == Movement.DOWN:
        pace = settings['PACE_SCROLL']
        base = scale if action == Movement.UP else -scale
        # print(base * count * pace)
        pag.scroll(base * count * pace)

def on_press(key):
    global activated, settings, stack, number_stack
    # see if need to activate / deactivate
    all_stack = stack.copy()
    all_stack.append(key)
    all_stack = set(all_stack)
    if all_stack.issuperset(settings['VIMALL_TOGGLE_KEYSET']):
        activated = not activated
        
        if activated:
            print('Activated')
        else:
            print('Deactivated')
    
    if not activated:
        stack.clear()
        number_stack.clear()
        return
    
    try:
        # input is char
        key_char = key.char
        
        if key_char.isnumeric():
            # input is a number
            number_stack.append(key_char)
            # print(f'detected number input: {key_char}')
        else:
            # detect if it is h,j,k,l
            try:
                movement = Movement.parse(key_char)
                # print(f'detected movement: {movement}')
                scale = settings['FAST_SCALE'] if settings['FAST_KEY'] in stack else 1.0
                action_count = 1 if len(number_stack) == 0 else int(''.join(number_stack))
                move(movement, action_count, scale)
                # print('moving...')
                number_stack.clear()
            except Exception as e:
                # print(f'An error occurred: {e}')
                pass
            
    except AttributeError:
        # handle special key
        # print(f'detecting special key: {key.name}')
        if key in settings['SPECIAL_KEYS']:
            stack.append(key)
        else:
            if key == settings['CLICK_KEY']:
                # click
                if settings['DOUBLE_CLICK_MODIFIER'] in stack:
                    pag.doubleClick()
                    # print('double click')
                elif settings['RIGHT_CLICK_MODIFIER'] in stack:
                    pag.rightClick()
                    # print('right click')
                else:
                    pag.leftClick()
                    # print('left click')
            elif key == settings['SCROLL_KEY']:
                movement = Movement.UP if settings['REVERSE_SCROLL'] in stack else Movement.DOWN
                action_count = 1 if len(number_stack) == 0 else int(''.join(number_stack))
                print(action_count)
                # scale = settings['FAST_SCALE'] if settings['FAST_KEY'] in stack else 1.0
                # scroll(movement, action_count, scale)
                scroll(movement, action_count, 1.0)
                number_stack.clear()
        # print(f'current stack: {stack}')
        
def on_release(key):
    global activated
    if not activated:
        return
    
    try:
        _ = key.char
    except AttributeError:
        # print(f'released special key: {key.name}')
        if key in settings['SPECIAL_KEYS']:
            if key in stack:
                stack.pop()
            else:
                stack.clear()
        # print(f'current stack: {stack}')

def main():
    pag.FAILSAFE = False
    
    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

    # ...or, in a non-blocking fashion:
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)

    listener.start()

if __name__ == '__main__':
    main()