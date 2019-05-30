import click, json, os
from logzero import logger

class LaimsApp(object):
    context = None
    class __LaimsAppSingleton(object):
        def __init__(self, config_file, config):
            config2 = {}
            if config_file:
                if not os.path.exists(config_file):
                    raise Exception("Given config file {} does not exist!".format(config_file))
                config2 = LaimsApp.load_config(config_file)
            elif config_file is None:
                config_file = os.path.join(click.get_app_dir('laims'), 'config.json')
                if os.path.exists(config_file):
                    config2 = LaimsApp.load_config(config_file)
            for key in config2:
                if key in config and config[key] is not None: continue
                config[key] = config2[key]
            self.config = config

#-- __LaimsAppSingleton            

    def __init__(self, config_file=None, config={}):
        if LaimsApp.context: raise Exception("Attempting to reinitialize LAIMS App!")
        LaimsApp.context = LaimsApp.__LaimsAppSingleton(config_file=config_file, config=config)

    def __getattr__(self, name):
        if name in LaimsApp.context.config:
            return LaimsApp.context.config[name]
        return None

    def __setattr__(self, name, val=None):
        LaimsApp.context.config[name] = val
        return LaimsApp.context.config[name]

    @staticmethod
    def load_config(config_file):
        if not os.path.exists(config_file):
            logger.error('No configuration file found at {0}'.format(self.config_file))
            return
        config = None
        with open(config_file) as f:
            config = json.load(f)
        config["config_file"] = config_file
        return config    

    def log_config(self):
        logger.info('Using config at {0}'.format(self.config_file))
        logger.info('Using database at {0}'.format(self.database))

#-- LaimsApp
