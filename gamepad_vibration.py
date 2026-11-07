import math
import sys
import time

try:
    import pygame
    from pygame._sdl2 import controller as sdl_controller
except ModuleNotFoundError as error:
    if error.name != "pygame":
        raise
    print(
        "pygame was not found. Run the application with ./run.sh "
        "to install the dependency in a virtual environment.",
        file=sys.stderr,
    )
    raise SystemExit(1) from error


WIDTH = 640
HEIGHT = 420
BACKGROUND = (24, 27, 34)
PANEL = (37, 42, 52)
TEXT = (235, 238, 244)
MUTED = (158, 168, 183)
ACCENT = (91, 174, 255)
ON = (74, 205, 137)
OFF = (224, 100, 100)
DEADZONE = 0.12


def find_controller():
    for index in range(sdl_controller.get_count()):
        if sdl_controller.is_controller(index):
            return sdl_controller.Controller(index)
    return None


def draw_text(surface, font, text, position, color=TEXT):
    surface.blit(font.render(text, True, color), position)


def stick_intensity(x, y):
    magnitude = min(1.0, math.hypot(x, y))
    return 0.0 if magnitude <= DEADZONE else (magnitude - DEADZONE) / (1.0 - DEADZONE)


def draw_intensity_bar(surface, font, label, intensity, y):
    draw_text(surface, font, f"{label}: {round(intensity * 100)}%", (52, y))
    bar_rect = pygame.Rect(52, y + 30, WIDTH - 104, 18)
    pygame.draw.rect(surface, (58, 65, 78), bar_rect, border_radius=9)
    fill_rect = bar_rect.copy()
    fill_rect.width = round(bar_rect.width * intensity)
    if fill_rect.width:
        pygame.draw.rect(surface, ACCENT, fill_rect, border_radius=9)


def draw_interface(
    surface, font, small_font, connected, name, enabled, left_intensity, right_intensity
):
    surface.fill(BACKGROUND)
    pygame.draw.rect(surface, PANEL, (24, 24, WIDTH - 48, HEIGHT - 48), border_radius=18)

    draw_text(surface, font, "Gamepad Vibration", (52, 48))
    draw_text(
        surface,
        small_font,
        f"Gamepad: {name}" if connected else "No gamepad found — connect one",
        (52, 98),
        MUTED if connected else OFF,
    )

    state_text = "ON" if enabled else "OFF"
    state_color = ON if enabled else OFF
    pygame.draw.circle(surface, state_color, (66, 164), 9)
    draw_text(surface, font, f"Vibration {state_text}", (86, 148), state_color)

    draw_intensity_bar(surface, small_font, "Left motor", left_intensity, 202)
    draw_intensity_bar(surface, small_font, "Right motor", right_intensity, 272)

    draw_text(surface, small_font, "X — toggle vibration", (52, 350), MUTED)
    draw_text(
        surface,
        small_font,
        "Left stick — left motor, right stick — right motor",
        (52, 378),
        MUTED,
    )
    pygame.display.flip()


def run():
    pygame.init()
    sdl_controller.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gamepad Vibration")
    font = pygame.font.Font(None, 34)
    small_font = pygame.font.Font(None, 25)
    clock = pygame.time.Clock()

    gamepad = None
    enabled = False
    previous_x = False
    applied_intensities = (0.0, 0.0)
    left_intensity = 0.0
    right_intensity = 0.0
    name = ""
    next_scan = 0.0
    running = True

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            now = time.monotonic()
            if gamepad is not None and not gamepad.attached():
                gamepad.quit()
                gamepad = None
                enabled = False
                previous_x = False
                applied_intensities = (0.0, 0.0)
                left_intensity = 0.0
                right_intensity = 0.0

            if gamepad is None and now >= next_scan:
                gamepad = find_controller()
                if gamepad is not None:
                    name = gamepad.name
                    enabled = False
                    previous_x = False
                    applied_intensities = (0.0, 0.0)
                    left_intensity = 0.0
                    right_intensity = 0.0
                next_scan = now + 1.0

            if gamepad is not None:
                x_pressed = gamepad.get_button(pygame.CONTROLLER_BUTTON_X)
                if x_pressed and not previous_x:
                    enabled = not enabled
                previous_x = x_pressed

                left_x = gamepad.get_axis(pygame.CONTROLLER_AXIS_LEFTX) / 32768
                left_y = gamepad.get_axis(pygame.CONTROLLER_AXIS_LEFTY) / 32768
                right_x = gamepad.get_axis(pygame.CONTROLLER_AXIS_RIGHTX) / 32768
                right_y = gamepad.get_axis(pygame.CONTROLLER_AXIS_RIGHTY) / 32768

                left_intensity = stick_intensity(left_x, left_y)
                right_intensity = stick_intensity(right_x, right_y)
                intensities = (left_intensity, right_intensity)

                if enabled:
                    if any(
                        abs(current - applied) >= 0.01
                        or (current == 0.0 and applied != 0.0)
                        for current, applied in zip(intensities, applied_intensities)
                    ):
                        if not gamepad.rumble(left_intensity, right_intensity, 0):
                            raise RuntimeError(
                                "This gamepad does not support vibration (rumble)."
                            )
                        applied_intensities = intensities
                elif applied_intensities != (0.0, 0.0):
                    gamepad.stop_rumble()
                    applied_intensities = (0.0, 0.0)

            draw_interface(
                screen,
                font,
                small_font,
                gamepad is not None,
                name,
                enabled,
                left_intensity if enabled else 0.0,
                right_intensity if enabled else 0.0,
            )
            clock.tick(60)
    finally:
        if gamepad is not None:
            if enabled and gamepad.attached():
                gamepad.stop_rumble()
            gamepad.quit()
        sdl_controller.quit()
        pygame.quit()


if __name__ == "__main__":
    try:
        run()
    except pygame.error as error:
        print(f"pygame/SDL error: {error}", file=sys.stderr)
        raise
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise
