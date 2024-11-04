import logging, aiohttp, json
from config import Config

logger = logging.getLogger("bing_search")

async def bing_news_search_impl(query: str, max_results: int = 5, freshness: str = "Day") -> str:
    """
    Queries the Bing News API for the given search terms and returns formatted news articles.
    The output includes meta-instructions for an LLM to guide how to interpret and process the content.
    """
    logger.info(f"Searching Bing for query: {query}")
    subscription_key = Config.BING_API_KEY
    if not subscription_key:
        raise Exception("BING_API_KEY is not set")

    url = f"https://api.bing.microsoft.com/v7.0/news/search?q={query}&count={max_results}&freshness={freshness}&safeSearch=Strict"
    
    async with aiohttp.ClientSession() as session:
        session.headers.update({"Ocp-Apim-Subscription-Key": subscription_key})
        async with session.get(url) as response:
            if response.status == 200:
                response_data = json.loads(await response.text())

                # Meta-instructions for the LLM
                results_text = (
                    "INSTRUCTIONS:\n"
                    "The following content contains news articles retrieved based on the query: "
                    f"'{query}'. Each article contains a title, a brief description, "
                    "the provider (source of the article), and the date it was published. "
                    "Summarize the key points in a conversational, voice-friendly manner. "
                    "Avoid listing the articles; instead, provide a concise, natural-sounding summary "
                    "that highlights the most relevant information based on the query."
                )
                
                # Extract articles from the response
                articles = response_data.get("value", [])
                
                if not articles:
                    logger.info("No articles found.")
                    return results_text + "No news articles found for the query."

                logger.info(f"Found {len(articles)} articles.")
                for article in articles:
                    title = article.get("name", "No title")
                    #url = article.get("url", "No URL")
                    description = article.get("description", "No description available")
                    provider_list = article.get("provider", [])
                    provider_names = ", ".join([provider.get("name", "Unknown provider") for provider in provider_list])
                    date_published = article.get("datePublished", None)
                    logger.info(f"  {title}")

                    # Format the article into a readable block of text
                    article_text = (
                        f"Article:\n"
                        f"Title: {title}\n"
                        #f"URL: {url}\n"
                        f"Description: {description}\n"
                        f"Provider(s): {provider_names}\n"
                        f"Published on: {date_published}\n"
                    )

                    # If the 'about' field exists, include related entities
                    # related_entities = article.get("about", [])
                    # if related_entities:
                    #     entity_names = ", ".join([entity.get("name", "Unknown entity") for entity in related_entities])
                    #     article_text += f"Related Entities: {entity_names}\n"
                    
                    article_text += "\n"
                    results_text += article_text
                
                return results_text
            
            else:
                raise Exception(f"Failed to get search results, status code: {response.status}")
