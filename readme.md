# Python Web Scraper

This project is a Python-based web scraper that utilizes the Beautiful Soup and Requests modules to extract data from a website with a specific hierarchical structure. The scraper follows the structure: manufacturer -> category -> model -> section (optional) -> parts to gather information at each level.

## Features

- **Web Scraping**: The web scraper is built using Beautiful Soup and Requests modules to extract data from the target website. It follows the hierarchical structure of manufacturer, category, model, section (optional), and parts to collect relevant information.
- **Asynchronous Scraping**: The scraper iterates through all the links asynchronously, leveraging asynchronous methods to parallelize the scraping process. This improves the overall efficiency and reduces scraping time.
- **Data Processing and Storage**: The scraped data is processed and stored in a PostgreSQL database for efficient storage and retrieval.
- **Database Structure**: The project includes four tables - manufacturer, category, model, and parts - where each table has references to the previous table. This creates a relational database structure that maintains the hierarchical relationship between the scraped data.
- **FastAPI Integration**: A FastAPI is created to interact with the scraped data stored in the PostgreSQL database.
- **Swagger UI**: It is recommended to use Swagger UI with the FastAPI integration. Swagger UI provides a user-friendly interface to interact with the API endpoints and explore the available data.
- **Containerization with Docker**: The entire process is containerized using Docker. There are three Docker containers involved: the database container, the scraper container, and the FastAPI container. The Docker Compose file (`docker-compose.yml`) simplifies the containerization process.

## Installation

1. Clone the repository:

```shell
git clone https://github.com/your-username/your-project.git
```

2. Navigate to the project folder and run the below command
docker compose up

3. Make sure you have Docker and Docker Compose installed on your system with good internet connectivity.

4. It will take some time to scrape the data and store in the database. Once it is done open fastApi swagger UI
   - Open your browser and navigate to `http://localhost:8000/docs` to access the Swagger UI.
   - Explore the available endpoints and interact with the scraped data using the provided interface.


## Database Schema

The project includes the following four tables in the PostgreSQL database:

1. `manufacturer`: Stores information about manufacturers, including their names and identifiers.
2. `category`: Contains data related to categories, with references to the associated manufacturer.
3. `model`: Stores model information, linked to the corresponding category.
4. `parts`: Stores data related to parts, with references to the corresponding model.

## License

This project is licensed under the [MIT License](LICENSE).

Feel free to modify and adapt this project to suit your needs. However, please remember to give credit to the original authors by including a reference to this repository.