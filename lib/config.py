import warnings
import spells
import ConfigParser
import lib.registry

def load(fileName):
    """
    Load and validate the configuration from a given file

    :type fileName: str
    :param fileName: The configuration file name to load

    :rtype: dict
    :return: The loaded configuration
    """

    configObj = ConfigParser.ConfigParser()
    configObj.optionxform = str # Keep case (default converts to lower case)
    configObj.read([fileName])
    config = dict(configObj.items('Config'))
    validate(config)
    return config

def validate(config):
    """
    Inspect configuration and disable spells in which required configurations
    are missing

    :type config: dict
    :param config: The deserialized config
    """

    for spell in lib.registry.all():
        baseMsg = 'spell:%s is being disabled;' % spell['spell'].__name__
        for key, value in spell['spell'].config.iteritems():
            if key not in config:
                print (
                    '%s a required configuration is missing: "%s"' % (
                        baseMsg, key
                    )
                )
                spell['enabled'] = False
                break
            else:
                configValue = config[key]

                if isinstance(value, (list, tuple)):
                    expectedType = value[0]
                    expectedValues = value[1:]
                else:
                    expectedType = value
                    expectedValues = [configValue]

                try:
                    config[key] = expectedType(configValue)
                except ValueError:
                    print (
                        "%s '%s' should be a %s, not a %s." % (
                            baseMsg, key, expectedType, configValue
                        )
                    )
                    spell['enabled'] = False
                    break

                if configValue not in expectedValues:
                    warnings.warn(
                        "%s '%s' must be one of the following: %s"  % (
                            baseMsg, key, expectedValues
                        )
                    )
                    spell['enabled'] = False
