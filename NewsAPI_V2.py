import base64
from google.cloud import storage
from newsapi import NewsApiClient
import pandas as pd
from datetime import datetime, timedelta

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    
    # The name of your GCS bucket
    # bucket_name = "your-bucket-name"
    
    # The path and the file to upload
    # source_file_name = "local/path/to/file"
    
    # The name of the file in GCS bucket once uploaded
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

def create_file_name(source):
    '''Generate a .txt filename using the current timestamp'''
    
    # Convert the current datetime to string
    date = datetime.now().strftime("%Y_%m_%d-%H_%M")

    file_name = source + date + '.csv'
    
    return file_name

def Newsapi(source,url,from_date,end_date):
    newsapi = NewsApiClient(api_key='6bfed5d92d2047e496bd7fe940fe2336')
    all_articles = newsapi.get_everything(#q='market',
                                      sources=source,
                                      domains=url,
                                      from_param=from_date,
                                      to=end_date,
                                      language='en',
                                      page_size=100)
    sources_data = all_articles['articles']
    df = pd.DataFrame.from_dict(sources_data)
    return df

def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    newsapi = NewsApiClient(api_key='6bfed5d92d2047e496bd7fe940fe2336')
    source_id=['abc-news','abc-news-au','al-jazeera-english','associated-press','axios','bbc-news',
           'breitbart-news','cbc-news','cbs-news','cnn','fox-news','google-news','independent',
           'msnbc','national-review','nbc-news','news24','news-com-au','newsweek','new-york-magazine',
           'politico','reddit-r-all','reuters','rte','the-american-conservative','the-globe-and-mail',
           'the-hill','the-hindu','the-huffington-post','the-irish-times','the-jerusalem-post',
           'the-times-of-india','the-washington-post','the-washington-times','time','usa-today','vice-news']
    source_url = ['https://abcnews.go.com','http://www.abc.net.au/news','http://www.aljazeera.com',
              'https://apnews.com/','https://www.axios.com','http://www.bbc.co.uk/news','http://www.breitbart.com',
              'http://www.cbc.ca/news','http://www.cbsnews.com','http://us.cnn.com','http://www.foxnews.com',
              'https://news.google.com','http://www.independent.co.uk','http://www.msnbc.com',
              'https://www.nationalreview.com/','http://www.nbcnews.com','http://www.news24.com',
              'http://www.news.com.au','https://www.newsweek.com','http://nymag.com','https://www.politico.com',
              'https://www.reddit.com/r/all','http://www.reuters.com','https://www.rte.ie/news',
              'http://www.theamericanconservative.com/','https://www.theglobeandmail.com','http://thehill.com',
              'http://www.thehindu.com','http://www.huffingtonpost.com','https://www.irishtimes.com',
              'https://www.jpost.com/','http://timesofindia.indiatimes.com','https://www.washingtonpost.com',
              'https://www.washingtontimes.com/','http://time.com','http://www.usatoday.com/news',
              'https://news.vice.com']
    

    today = datetime.today().strftime('%Y-%m-%d')
    yesterday = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')
    for i in range(len(source_id)):
        df = Newsapi(source_id[i],source_url[i],yesterday,today)
        file_name = create_file_name(source_id[i])
        df.to_csv('/tmp/'+file_name)
        bucket_name = 'articlebuckets'
        local_file_location = '/tmp/' + file_name
        upload_blob(bucket_name, local_file_location, file_name)