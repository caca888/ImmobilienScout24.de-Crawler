import configparser
from pandas import DataFrame

class Spider:
    def __init__(self, config_file):
        self.config_file = config_file
        self.immoscout_data = DataFrame()
        self.config()

    @staticmethod
    def config(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        defaultConfig = config['DEFAULT']
        self.projectname = defaultConfig['PROJECT_NAME']
        self.domain = defaultConfig['DOMAIN']
        self.urllocation = defaultConfig['URL_LOCATION']
        self.urltype = defaultConfig['URL_TYPE']
        

    @staticmethod
    def boot():
        create_project_dir()
