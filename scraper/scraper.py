import aiohttp
import asyncio
from bs4 import BeautifulSoup
from aiohttp import ClientSession
from utils import get_main_sheet_info, process_dataframes
from config import CATALOGUE_URL, DOMAIN
import pandas as pd
from db_operations import MasterDB
from scraper_logger import logger
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Scraper(object):
    def __init__(self, urls:list[str], domain:str, class_name:str, tag:str = "a"):
        """This is a webscraper especially created to scrape manufacture data. It scrapes the given URL in
        asynchronous manner. So make sure to not to overload the target Website.
        
        Args:
            urls (list[str]): List of URLs to scrape
            domain (str): Domain of the website. This would be added as a suffix to the url
            class_name (str): Classname of html div to scrape the necessary data
            tag (str, optional): html tag of links. Defaults to "a".
            
        How to run:
        step_1 -> Intialize the Scraper object with the required arguments
        scraper = Scraper(urls, domain, class_name)
        step_2 -> call the variable extracted_data. No need to call any method
        data = scraper.extracted_data
        
        """
        self.urls = urls
        self.domain = domain
        self.class_name = class_name
        self.tag = tag
        self.extracted_data  = []
        asyncio.run(self.main())

    async def fetch(self, session:ClientSession, url: str):
        """Extract the data from given url and return required information

        Args:
            session (ClientSession): Http session
            url (str): url of the webpage to be extracted

        Returns:
            List[List]: Returs required information.
        """
        try:
            async with session.get(url) as response:
                # 1. Extracting the Text:
                text = await response.text()
                # 2. Extracting desired_details
                all_links = await self.get_desired_details(text)
                if len(all_links)>0:
                    req_data =  [[url,row.text.strip(), f"{self.domain}{row.get('href')}"] for row in all_links]
                else:
                    req_data = [[url, None, None]]
                return req_data
        except Exception as e:
            print(str(e))
            return [[url, None, None]]
            
    async def get_desired_details(self, content:str):
        """Extract the Useful links from the html content

        Args:
            content (str): html content recieved from the url

        Returns:
            List[str]: List of links(tag<a> elements)
        """
        soup = BeautifulSoup(content, "html.parser")
        container = soup.find(class_= self.class_name)
        if container is not None:
            all_links = container.find_all(self.tag)
        else:
            all_links = []
        return all_links

    async def main(self):
        """Orchestrator of this scraper. Creates the client session and run asynchronously
        
        """
        tasks = []
        headers = {
            "user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        async with aiohttp.ClientSession(headers=headers) as session:
            for url in self.urls:
                tasks.append(self.fetch(session, url))

            htmls = await asyncio.gather(*tasks)
            self.extracted_data = [item for sublist in htmls for item in sublist]
            
if __name__ == "__main__":
    
    # Get Manufacturers details and create a dataframe
    logger.info("Extracting Manufacturers data")
    manufacturer_links = get_main_sheet_info(CATALOGUE_URL, "c_container allmakes")
    urls = [[row.text.strip(), f"{DOMAIN}{row.get('href')}"] for row in manufacturer_links]
    df_manufacturer = pd.DataFrame(urls, columns = ["manufacturer","manufacturer_link"])
    # df_manufacturer.to_csv("df_manufacturer.csv")
    # df_manufacturer  = pd.read_csv("df_manufacturer.csv")
    # # Get Category details and create a dataframe
    logger.info("Extracting categories data")
    scraper = Scraper(urls = df_manufacturer["manufacturer_link"].to_list(),
                     domain = DOMAIN,
                     class_name = "c_container allmakes allcategories")
    df_category = pd.DataFrame(scraper.extracted_data,
                               columns = ["manufacturer_link", "category", "category_link"])
    # df_category.to_csv("df_category.csv")
    # df_category= pd.read_csv("df_category.csv")
    # Get Model details and create a dataframe
    logger.info("Extracting models data")
    scraper = Scraper(urls = df_category["category_link"].to_list(),
                domain = DOMAIN,
                class_name = "c_container allmodels")
    df_models =  pd.DataFrame(scraper.extracted_data, columns = ["category_link", "model", "model_link"])
    # df_models.to_csv("df_models.csv")
    # Get Section details and create a dataframe
    logger.info("Extracting Sections data")
    model_links = df_models["model_link"].unique()
    # Create an empty DataFrame to store the results
    df_sections = pd.DataFrame()
    
    # Process model links in chunks
    chunk_size = 25
    for i in range(0, len(model_links), chunk_size):
        # Get the chunk of model links
        
        chunk = model_links[i:i+chunk_size]

        # Perform scraping for the current chunk
        scraper = Scraper(urls=chunk, domain=DOMAIN, class_name="c_container modelSections")
        df_chunk = pd.DataFrame(scraper.extracted_data, columns=["model_link", "section", "section_link"])

        # Append the results to the main DataFrame
        df_sections = pd.concat([df_sections,df_chunk])
        logger.info(f"Extraction of sections data for {i+chunk_size} models completed")
        
    
    # Combining sections and models as there are very limited sections are available
    df_models = df_models.merge(df_sections, how = "left", on = "model_link")
    df_models.loc[df_models.section_link.isna(), "section_link"] = df_models["model_link"]
    df_models.to_csv("df_models_2.csv")
    # Get Part details and create a dataframe
    logger.info("Extracting Part data") 
    model_sections = df_models["section_link"].unique()
    # Create an empty DataFrame to store the results
    df_parts = pd.DataFrame()
    
    # Process model links in chunks
    chunk_size = 5
    for i in range(0, len(model_sections), chunk_size):
        
        # Get the chunk of model links
        chunk = model_sections[i:i+chunk_size]

        # Perform scraping for the current chunk
        scraper = Scraper(urls=chunk, domain=DOMAIN, class_name="c_container allparts")
        df_chunk = pd.DataFrame(scraper.extracted_data, columns=["section_link", "part", "part_link"])

        # Append the results to the main DataFrame
        df_parts = pd.concat([df_sections,df_chunk])
        logger.info(f"Extraction of parts data for {i+chunk_size} models completed")
        
    # df_parts.to_csv("df_parts.csv")
    logger.info(f"Preparing the data for db storage")
    # df_models= pd.read_csv("df_models_2.csv")
    # df_parts= pd.read_csv("df_parts.csv")
    df_manufacturer, df_category, df_models, df_parts = process_dataframes(
                                                            df_manufacturer, df_category, df_models, df_parts
                                                        )
    
    
    db = MasterDB()
    logger.info(f"Saving the data to db")
    db.save_df_to_db(df_manufacturer, "manufacturer")
    db.save_df_to_db(df_category, "category")
    db.save_df_to_db(df_models, "models")
    db.save_df_to_db(df_parts, "parts")
    db.close()
    logger.info(f"Scraping completed Succesfully and stored in db")
