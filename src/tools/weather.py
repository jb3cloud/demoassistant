import logging
import aiohttp

logger = logging.getLogger("weather")

async def get_weather_impl(location: str) -> str:
    """This function will return the weather for the given location."""
    logger.info(f"Getting weather for {location}")
    url = f"https://wttr.in/{location}?format=%C+%t"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                weather_data = await response.text()
                # response from the function call is returned to the LLM
                return f"The weather in {location} is {weather_data}."
            else:
                raise f"Failed to get weather data, status code: {response.status}"
