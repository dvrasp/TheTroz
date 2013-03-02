import warnings
import configobj
import spells

def load(fileName):
    configObj = configobj.ConfigObj(fileName)
    config = flatten(configObj)
    validate(config)
    return config

def flatten(d):
    newDict = dict()
    for key, value in d.iteritems():
        if isinstance(value, dict):
            for key2, value2 in flatten(value).iteritems():
                newDict['.'.join((key, key2))] = value2
        else:
            newDict[key] = value
    return newDict

def validate(config):
    for spell in spells.ALL:
        baseMsg = 'spell:%s is being disabled;' % spell
        for key, value in spell.config.iteritems():
            if key not in config:
                print (
                    '%s a required configuration is missing: "%s"' % (
                        baseMsg, key
                    )
                )
                del spells.VALIDATED[spell]
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
                    del spells.VALIDATED[spell]
                    break

                if configValue not in expectedValues:
                    warnings.warn(
                        "%s '%s' must be one of the following: %s"  % (
                            baseMsg, key, expectedValues
                        )
                    )
                    del spells.VALIDATED[spell]
