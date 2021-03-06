from cluster_config.utils import cli
from cluster_config.utils import file
from cluster_config.utils import log
from cluster_config.utils import dict, file, log, cli

#the hocon file extension https://github.com/typesafehub/config/blob/master/HOCON.md
HOCON_EXT = "conf"

#json file extension
JSON_EXT = "json"

#yaml file extension
YAML_EXT = "yaml"

#user config file prefix
USER_PREFIX = "user"

#merge config file prefix
MERGE_PREFIX = "merged"

#CDH configuration file name
CDH_CONFIG_NAME = "cdh"


#CDH config file name
CDH_CONFIG = "{0}.{1}".format(CDH_CONFIG_NAME, JSON_EXT)

#user cdh config file name
USER_CDH_CONFIG = "{0}-{1}.{2}".format(USER_PREFIX, CDH_CONFIG_NAME, JSON_EXT)

#merged file name
MERGED_CDH_CONFIG = "{0}-{1}.{2}".format(MERGE_PREFIX, CDH_CONFIG_NAME, JSON_EXT)

#the possible answers for interactive conflict resolution
USER = type('obj', (object,), {'single' : "user", "persistent" : "au"})

#the possible answers for interactive conflict resolution
GENENERATED = type('obj', (object,), {'single' : "auto", "persistent": "ag"})

#interactive max retry incase the user types in the wrong info
RETRY = 5

#fomula args file name
FORMULA_ARGS = "formula-args.{0}".format(YAML_EXT)

#all cdh configs
CDH_CLUSTER_CONFIGS = "ALL-CDH-CLUSTER-CONFIGURATIONS.{0}".format(JSON_EXT)

#allowed dict merge conflict resolutions
CONFLICT_RESOLUTION = ["interactive", "user", "generated"]


DEFAULT_FORMULA = "formula.py"
