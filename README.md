# Galactic Unicorn Advanced Weather Clock

An advanced weather clock built for the 53x11 Pimoroni Galactic Unicorn display.

![WeatherStationExamples](https://github.com/TagWolf/UnicornWeatherStation/assets/8665128/ce3ee61b-f811-4c15-9eee-06c5e8b829d8)

![Galactic Unicorn Display](https://shop.pimoroni.com/cdn/shop/products/galactic-unicorn-1_768x768.jpg)

[Get Yours Here!](https://shop.pimoroni.com/products/space-unicorns?variant=40842033561683)

## Plans
- I will eventually update this so that each screen only contains one piece of labeled information with an icon. You will navigate the different screens with Vol+/-. However until then, the current button mappings are below.

## Features

- Displays current time with a gradient based on the time of day.
- Shows the date with a gradient based on the season.
- Fetches and displays live weather data:
  - Current temperature with a color gradient based on comfort levels.
  - Humidity with a gradient indicating moisture level.
  - Wind speed in mph with a gradient indicating wind strength.
  - Atmospheric pressure in inHg.
  - Cloud coverage percentage.
  - Visibility in meters.
  - Rain and Snowfall (1 hour and 3 hour)
- Button controls to toggle between time, date, and various weather metrics.
- Adjusts display brightness.

## Setup

1. Clone this repository
2. Grab an API key from https://openweathermap.org
3. Navigate to the project directory
4. Update the `WIFI_SSID`, `WIFI_PASSWORD`, and `OPEN_WEATHER_MAP_API_KEY` constants in the main script with your credentials.

5. Deploy the script and icons to your Pimoroni Galactic Unicorn display.
6. Power on the display and enjoy your advanced weather clock!
7. Use the designated buttons to navigate between different weather and time displays.

## Button Functions

| Button | Function                                  |
|--------|-------------------------------------------|
| A      | Temperature and Humidity                 |
| B      | Low and High Temperatures                |
| C      | Pressure and Wind Speed                  |
| D      | Cloud Coverage and Visibility (Rain/Snow If Present) |
| Zzz    | Date                                      |
| Lux -  | Decrease Brightness                      |
| Lux +  | Increase Brightness                      |


## Dependencies

- `galactic`: Library for the Pimoroni Galactic Unicorn display.
- `picographics`: Graphics library for displays.
- `math` : For math calculations and functions.
- `network`: For connecting to Wi-Fi.
- `ntptime`: For syncing time.
- `urequests`: For making API requests.
- `jpegdec`: For decoding and displaying JPEG images.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

[MIT License](LICENSE)

## Acknowledgements

- Thanks to Pimoroni for the Galactic Unicorn display and the community for their support and contributions.
- Thanks to ChatGPT for writing 98% of this code.
