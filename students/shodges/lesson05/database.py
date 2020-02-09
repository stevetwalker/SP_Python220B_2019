from pymongo import MongoClient
from pathlib import Path
import csv, logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)
LOG_FORMAT = "%(asctime)s %(filename)s:%(lineno)-3d %(levelname)s %(message)s"
LOG_FILE = 'db.log'

FORMATTER = logging.Formatter(LOG_FORMAT)
FILE_HANDLER = logging.FileHandler(LOG_FILE)
FILE_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)

class DBConnection():
    """
    Class to instantiate the connection to the Mongo DB.
    """

    def __init__(self, host='127.0.0.1', port=27017):
        """
        Initialize the connection class.
        """
        self.host = host
        self.port = port
        self.connection = None

    def __enter__(self):
        """
        Connect to the DB when entering the context manager.
        """
        self.connection = MongoClient(self.host, self.port)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close the connection when exiting the context manager.
        """
        self.connection.close()

def import_data(directory_name, product_file, customer_file, rentals_file):
    """
    Import data from specified CSV's into the database.
    """
    data_directory = Path(directory_name)
    with open(data_directory/product_file, mode='r') as product_input:
        product_list = [row for row in csv.DictReader(product_input)]
        logging.debug('Read in product data from %s: %s', product_file, product_list)

    with open(data_directory/customer_file, mode='r') as customer_input:
        customer_list = [row for row in csv.DictReader(customer_input)]
        logging.debug('Read in customer data from %s: %s', customer_file, customer_list)

    with open(data_directory/rentals_file, mode='r') as rentals_input:
        rentals_list = [row for row in csv.DictReader(rentals_input)]
        logging.debug('Read in rental data from %s: %s', rentals_file, rentals_list)

    mongo = DBConnection()

    with mongo:
        db = mongo.connection.media

        products = db['products']
        product_result = products.insert_many(product_list)
        if product_result.acknowledged is True:
            logging.debug('Wrote %d records to products', len(product_result.inserted_ids))
        else:
            logging.warning('Failed to write records to products')

        customers = db['customers']
        customer_result = customers.insert_many(customer_list)
        if customer_result.acknowledged is True:
            logging.debug('Wrote %d records to customers', len(customer_result.inserted_ids))
        else:
            logging.warning('Failed to write records to customers')

        rentals = db['rentals']
        rentals_result = rentals.insert_many(rentals_list)
        if rentals_result.acknowledged is True:
            logging.debug('Wrote %d records to rentals', len(rentals_result.inserted_ids))
        else:
            logging.warning('Failed to write records to rentals')

    return ((len(product_result.inserted_ids), len(customer_result.inserted_ids),
             len(rentals_result.inserted_ids)), (0 if product_result.acknowledged is True else 1) +
            (0 if customer_result.acknowledged is True else 1) +
            (0 if rentals_result.acknowledged is True else 1))
