import requests
from bs4 import BeautifulSoup
from pandas import DataFrame


def get_main_sheet_info(url: str, class_name: str, tag: str = "a"):
    """Extract all the links available in the given class name

    Args:
        url (str): Main Page URL
        class_name (str): class name of the html tag
        tag (str, optional): html tag of links. Defaults to "a".

    Returns:
        List: all the links extracted in the given page 
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    container = soup.find(class_=class_name)
    if container is not None:
        all_links = container.find_all(tag)
    else:
        all_links = []
    return all_links


def process_dataframes(manufacture_df: DataFrame, df_category: DataFrame,
                       df_models: DataFrame, df_parts: DataFrame):
    """Preprocessing to store in database
        1. Create Id column for each dataframe.
        2. Removing un-necessary columns 

    Args:
        manufacture_df (DataFrame): manufacture_df
        df_category (DataFrame): df_category
        df_models (DataFrame): df_models
        df_parts (DataFrame): df_parts

    Returns:
        tuple[DataFrame, DataFrame, DataFrame, DataFrame]: preprocessed dataframes
    """
    manufacture_df['manufacturer_id'] = range(1, len(manufacture_df) + 1)
    

    df_category['category_id'] = range(1, len(df_category) + 1)
    df_category['manufacturer_id'] = df_category['manufacturer_link'].map(
        manufacture_df.set_index('manufacturer_link')['manufacturer_id'])
    
    df_models['model_id'] = range(1, len(df_models) + 1)
    df_models['category_id'] = df_models['category_link'].map(
        df_category.set_index('category_link')['category_id'])
    

    
    df_parts = df_parts.merge(df_models[["model_link","model_id"]], how = "left", on = "model_link")
    try:
        df_parts[['part_number', 'part_name']] = df_parts["part"].astype(str).str.split('-', n=1,expand=True)
    except:
        df_parts[['part_number', 'part_name']] = 0

    df_parts['part_id'] = range(1, len(df_parts) + 1)
    manufacture_df = manufacture_df[['manufacturer_id', 'manufacturer']]
    df_category = df_category[['category_id', 'category', 'manufacturer_id']]
    df_models = df_models[['model_id', 'model', 'category_id']]
    df_parts = df_parts[['part_id', 'part', 'part_number', 'part_name','model_id']]
    return manufacture_df, df_category, df_models, df_parts
