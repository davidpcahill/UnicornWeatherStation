from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN
import math
import network
import ntptime
import time
import urequests as requests
import jpegdec

WIFI_SSID = "WIFI_SSID" # Replace with your Wi-Fi SSID
WIFI_PASSWORD = "WIFI_PASSWORD" # Replace with your Wi-Fi password
OPEN_WEATHER_MAP_API_KEY = "API_KEY" # Replace with your openweathermap.org API key
CITY = "San Jose"  # Replace with your city
COUNTRY_CODE = "US"  # Replace with your country code
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY_CODE}&units=imperial&APPID={OPEN_WEATHER_MAP_API_KEY}"
UTC_OFFSET = -7 * 3600  # Example for PDT. Adjust as needed.
BUTTON_PRESS_TIMEOUT = (
    10  # Time in seconds after which the clock will be displayed again
)
WEATHER_FETCH_INTERVAL = 300
# constants for controlling the background colour throughout the day
MIDDAY_HUE = 1.1
MIDNIGHT_HUE = 0.8
HUE_OFFSET = -0.1
MIDDAY_SATURATION = 1.0
MIDNIGHT_SATURATION = 1.0
MIDDAY_VALUE = 0.8
MIDNIGHT_VALUE = 0.3

gu = GalacticUnicorn()
graphics = PicoGraphics(display=DISPLAY_GALACTIC_UNICORN)
graphics.set_font("bitmap8")
width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT
WHITE = graphics.create_pen(109, 131, 176)
BLACK = graphics.create_pen(0, 0, 0)
RED = graphics.create_pen(241, 72, 24)
BLUE = graphics.create_pen(24, 153, 241)

current_state = "clock"
state_start_time = None
last_button_press_time = None
last_weather_fetch_time = 0


@micropython.native  # noqa: F821
def from_hsv(h, s, v):
    i = math.floor(h * 6.0)
    f = h * 6.0 - i
    v *= 255.0
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)

    i = int(i) % 6
    if i == 0:
        return int(v), int(t), int(p)
    if i == 1:
        return int(q), int(v), int(p)
    if i == 2:
        return int(p), int(v), int(t)
    if i == 3:
        return int(p), int(q), int(v)
    if i == 4:
        return int(t), int(p), int(v)
    if i == 5:
        return int(v), int(p), int(q)


def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        return True

    wlan.active(True)
    wlan.config(pm=0xA11140)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    max_wait = 100
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        time.sleep(0.2)

    return wlan.isconnected()


def sync_time():
    if connect_to_wifi():
        try:
            ntptime.settime()
            tm = time.localtime(time.mktime(time.localtime()) + UTC_OFFSET)
            machine.RTC().datetime((tm[0], tm[1], tm[2], 0, tm[3], tm[4], tm[5], 0))
            print("Time set")
        except OSError:
            pass


def get_weather_data():
    global last_weather_fetch_time, weather_data

    if time.time() - last_weather_fetch_time < WEATHER_FETCH_INTERVAL and weather_data:
        return weather_data

    for _ in range(3):
        try:
            sync_time()
            weather_data = requests.get(URL).json()
            last_weather_fetch_time = time.time()
            print(weather_data)
            return weather_data
        except OSError as e:
            print("Error fetching weather data:", e)
            time.sleep(5)
    else:
        return


def hpa_to_inHg(hpa):
    return hpa * 0.02953


def get_temperature_color(temp):
    if temp <= 32:
        return graphics.create_pen(255, 255, 255)  # White
    elif 32 < temp <= 65:
        decrease_value = int((temp - 32) * (255 / 33))
        return graphics.create_pen(
            255 - decrease_value, 255 - decrease_value, 255
        )  # Transition from white to blue
    elif 65 < temp <= 72:
        return graphics.create_pen(0, 0, 255)  # Blue
    elif 72 < temp <= 85:
        red_value = int((temp - 72) * (255 / 13))
        return graphics.create_pen(
            red_value, red_value, 255 - red_value
        )  # Transition from blue to yellow
    else:
        return graphics.create_pen(255, 0, 0)  # Red


def get_humidity_color(humidity):
    green_value = int(255 - humidity * 2.55)
    return graphics.create_pen(0, green_value, 255)  # Cyan to blue gradient


def get_wind_speed_color(speed):
    green_value = int(255 - speed * 2.55)  # Assuming max speed is 100mph for full blue
    return graphics.create_pen(0, green_value, 255)  # Cyan to blue gradient


def get_pressure_color(pressure):
    if pressure <= 980:
        return graphics.create_pen(0, 0, 255)  # Dark blue for low pressure
    elif 980 < pressure <= 1013:
        blue_value = int(255 - (pressure - 980) * (255 / 33))
        return graphics.create_pen(
            0, 255 - blue_value, blue_value
        )  # Gradient from dark blue to light blue
    elif 1013 < pressure <= 1040:
        green_value = int((pressure - 1013) * (255 / 27))
        return graphics.create_pen(
            0, green_value, 255 - green_value
        )  # Gradient from light blue to green
    else:
        return graphics.create_pen(0, 255, 0)  # Bright green for high pressure


def get_cloud_coverage_color(coverage):
    MIN_GRAY = 50
    gray_value = int(MIN_GRAY + (255 - MIN_GRAY) * (1 - coverage / 100))
    return graphics.create_pen(
        gray_value, gray_value, gray_value
    )  # Adjusted gray gradient for cloud coverage


def get_visibility_color(visibility):
    MIN_GRAY = 50
    max_visibility_m = 10000  # 10km in meters
    gray_value = int(MIN_GRAY + (255 - MIN_GRAY) * (visibility / max_visibility_m))
    return graphics.create_pen(
        gray_value, gray_value, gray_value
    )  # Gray gradient for visibility


def get_clock_color(hour):
    if 0 <= hour < 6:
        blue_value = int(128 + hour * (127 / 6))
        return graphics.create_pen(0, 0, blue_value)
    elif 6 <= hour < 12:
        red_value = int((hour - 6) * (255 / 6))
        green_value = int((hour - 6) * (255 / 6))
        return graphics.create_pen(red_value, green_value, 255 - red_value)
    elif 12 <= hour < 18:
        red_value = int(255 - (hour - 12) * (127 / 6))
        green_value = int(255 - (hour - 12) * (85 / 6))
        return graphics.create_pen(255, green_value, red_value)
    else:  # 18 <= hour < 24
        blue_value = int(255 - (hour - 18) * (127 / 6))
        return graphics.create_pen(255, 0, blue_value)


def get_date_color(month):
    if month in [12, 1, 2]:  # Winter
        return graphics.create_pen(0, 0, 255)
    elif month in [3, 4, 5]:  # Spring
        green_value = int(85 + (month - 3) * (85 / 3))
        return graphics.create_pen(0, green_value, 0)
    elif month in [6, 7, 8]:  # Summer
        return graphics.create_pen(255, 255, 0)
    else:  # Autumn
        red_value = int(255 - (month - 9) * (85 / 3))
        green_value = int(128 + (month - 9) * (42 / 3))
        return graphics.create_pen(red_value, green_value, 0)


def display_time():
    _, _, _, hour, minute, second, _, _ = time.localtime()

    time_through_day = (((hour * 60) + minute) * 60) + second
    percent_through_day = time_through_day / 86400
    percent_to_midday = 1.0 - ((math.cos(percent_through_day * math.pi * 2) + 1) / 2)
    hue = ((MIDDAY_HUE - MIDNIGHT_HUE) * percent_to_midday) + MIDNIGHT_HUE
    sat = (
        (MIDDAY_SATURATION - MIDNIGHT_SATURATION) * percent_to_midday
    ) + MIDNIGHT_SATURATION
    val = ((MIDDAY_VALUE - MIDNIGHT_VALUE) * percent_to_midday) + MIDNIGHT_VALUE
    gradient_background(hue, sat, val, hue + HUE_OFFSET, sat, val)

    clock = "{:02}:{:02}:{:02}".format(hour, minute, second)

    # calculate text position so that it is centred
    w = graphics.measure_text(clock, 1)
    x = int(width / 2 - w / 2 + 1)
    y = 2

    clock_color = get_clock_color(hour)
    outline_text(clock, x, y, clock_color, BLACK)


def display_date():
    # Fetch current date
    year, month, day, _, _, _, _, _ = time.localtime()
    date_str = "{:02}/{:02}/{:04}".format(month, day, year)

    # Calculate text position so that it is centered
    w = graphics.measure_text(date_str, 1)
    x = int(width / 2 - w / 2 + 1)
    y = 2

    date_color = get_date_color(month)
    outline_text(date_str, x, y, date_color, BLACK)


def display_weather(button):
    global current_state, state_start_time
    # Fetch weather data
    weather_data = get_weather_data()
    # Test weather data
    # weather_data = {'timezone': -18000, 'sys': {'type': 2, 'sunrise': 1694348124, 'country': 'US', 'id': 2035640, 'sunset': 1694393860}, 'base': 'stations', 'main': {'pressure': 1020, 'feels_like': 62.69, 'temp_max': 62.6, 'temp': 62.6, 'temp_min': 62.6, 'humidity': 88, 'sea_level': 1020, 'grnd_level': 944}, 'visibility': 10000, 'id': 5063678, 'clouds': {'all': 100}, 'coord': {'lon': -99.8296, 'lat': 40.1375}, 'rain': {'1h': 20.75, '3h': 15.75}, 'name': 'Beaver City', 'cod': 200, 'weather': [{'id': 500, 'icon': '10d', 'main': 'Rain', 'description': 'light rain'}], 'dt': 1694385881, 'wind': {'gust': 15.08, 'speed': 11.18, 'deg': 24}}
    if not weather_data:
        outline_text("No Data", 11, 2)
        return

    if button == "a":
        # Display Weather Icon, Temperature, and Humidity
        icon_id = weather_data["weather"][0]["icon"]
        icon_file = f"{icon_id}.jpg"
        # Assuming you have a function to display the jpeg image
        display_jpeg(icon_file, 0, 0)

        temp = round(weather_data["main"]["temp"])
        humidity = weather_data["main"]["humidity"]
        temp_color = get_temperature_color(temp)
        outline_text(f"{temp}°F", 14, 2, temp_color, BLACK)
        humidity_color = get_humidity_color(humidity)
        outline_text(f"{humidity}%", 36, 2, humidity_color, BLACK)

    elif button == "b":
        # Display Min Temp and Max Temp
        temp_min = round(weather_data["main"]["temp_min"])
        temp_max = round(weather_data["main"]["temp_max"])
        # Display thermometer icons (assuming you have them as jpeg)
        # display_jpeg("cold_thermometer.jpg", 10, 10)
        # display_jpeg("hot_thermometer.jpg", 10, 50)
        outline_text(f"{temp_min}°F", 6, 2, BLUE, BLACK)
        outline_text(f"{temp_max}°F", 30, 2, RED, BLACK)

    elif button == "c":
        # Display Pressure and Wind Speed and Direction
        pressure = weather_data["main"]["pressure"]
        pressure_inHg = hpa_to_inHg(pressure)
        pressure_color = get_pressure_color(pressure)
        wind_speed = round(weather_data["wind"]["speed"])
        wind_dir = weather_data["wind"]["deg"]
        wind_speed_color = get_wind_speed_color(wind_speed)
        # outline_text(f"{pressure}h", 2, 2, pressure_color, BLACK)
        outline_text(f"{pressure_inHg:.2f}", 2, 2, get_pressure_color(pressure))
        outline_text(f"{wind_speed}mph", 27, 2, wind_speed_color, BLACK)
        # Displaying wind direction as an arrow or text can be added here

    else:
        elapsed_time = time.time() - state_start_time if state_start_time else 0
        # Additional screens for rain or snow
        rain = weather_data.get("rain", {})
        snow = weather_data.get("snow", {})

        if current_state == "d_rain_snow":
            if elapsed_time >= 5:
                current_state = "clock"
                return
            if rain:
                rain_1h = rain.get("1h", 0)
                rain_3h = rain.get("3h", 0)
                outline_text(f'{rain_1h}"', 2, 2)
                outline_text(f'{rain_3h}"', 30, 2)
                return
            elif snow:
                snow_1h = snow.get("1h", 0)
                snow_3h = snow.get("3h", 0)
                outline_text(f'{snow_1h}"', 2, 2)
                outline_text(f'{snow_3h}"', 30, 2)
                return

        # Display Cloud coverage % and visibility
        cloud_coverage = weather_data["clouds"]["all"]
        cloud_coverage_color = get_cloud_coverage_color(cloud_coverage)
        visibility_m = weather_data.get("visibility", "N/A")
        if visibility_m != "N/A":
            visibility_km = visibility_m / 1000
            visibility_str = f"{visibility_km:.1f}km"
        else:
            visibility_str = "N/A"
        visibility_color = get_visibility_color(visibility_m)
        outline_text(f"{cloud_coverage}%", 2, 2, cloud_coverage_color, BLACK)
        outline_text(visibility_str, 24, 2, visibility_color, BLACK)

        if elapsed_time >= 5:
            current_state = "d_rain_snow"
            state_start_time = time.time()


def display_jpeg(filename, x, y):
    j = jpegdec.JPEG(graphics)
    j.open_file(filename)
    j.decode(x, y, jpegdec.JPEG_SCALE_FULL)


def adjust_brightness(delta):
    gu.adjust_brightness(delta)


def clear_screen():
    graphics.clear()


def outline_text(text, x, y, text_color=WHITE, bg_color=BLACK):
    graphics.set_pen(bg_color)
    graphics.text(text, x - 1, y - 1, -1, 1)
    graphics.text(text, x, y - 1, -1, 1)
    graphics.text(text, x + 1, y - 1, -1, 1)
    graphics.text(text, x - 1, y, -1, 1)
    graphics.text(text, x + 1, y, -1, 1)
    graphics.text(text, x - 1, y + 1, -1, 1)
    graphics.text(text, x, y + 1, -1, 1)
    graphics.text(text, x + 1, y + 1, -1, 1)

    graphics.set_pen(text_color)
    graphics.text(text, x, y, -1, 1)
    graphics.set_pen(WHITE)


def gradient_background(start_hue, start_sat, start_val, end_hue, end_sat, end_val):
    half_width = width // 2
    for x in range(0, half_width):
        hue = ((end_hue - start_hue) * (x / half_width)) + start_hue
        sat = ((end_sat - start_sat) * (x / half_width)) + start_sat
        val = ((end_val - start_val) * (x / half_width)) + start_val
        colour = from_hsv(hue, sat, val)
        graphics.set_pen(
            graphics.create_pen(int(colour[0]), int(colour[1]), int(colour[2]))
        )
        for y in range(0, height):
            graphics.pixel(x, y)
            graphics.pixel(width - x - 1, y)

    colour = from_hsv(end_hue, end_sat, end_val)
    graphics.set_pen(
        graphics.create_pen(int(colour[0]), int(colour[1]), int(colour[2]))
    )
    for y in range(0, height):
        graphics.pixel(half_width, y)


# Main loop
button_actions = {
    GalacticUnicorn.SWITCH_A: "a",
    GalacticUnicorn.SWITCH_B: "b",
    GalacticUnicorn.SWITCH_C: "c",
    GalacticUnicorn.SWITCH_D: "d",
}

gu.set_brightness(0.5)
sync_time()

while True:
    clear_screen()

    for button, action in button_actions.items():
        if gu.is_pressed(button) and current_state != action:
            print(f"Button {action.upper()} Pressed")
            current_state = action
            last_button_press_time = time.time()
            current_state = "d_cloud" if action == "d" else action
            state_start_time = time.time()

    if gu.is_pressed(GalacticUnicorn.SWITCH_SLEEP) and current_state != "date":
        print("SLEEP Button Pressed")
        current_state = "date"
        last_button_press_time = time.time()

    if current_state in ["a", "b", "c", "d_cloud", "d_rain_snow"]:
        display_weather(current_state)
    elif current_state == "clock":
        display_time()
    elif current_state == "date":
        display_date()

    if (
        last_button_press_time
        and (time.time() - last_button_press_time) > BUTTON_PRESS_TIMEOUT
    ):
        current_state = "clock"

    brightness = gu.get_brightness()
    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
        adjust_brightness(+0.005)
        print(brightness)
    elif gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
        adjust_brightness(-0.005)
        print(brightness)

    gu.update(graphics)
