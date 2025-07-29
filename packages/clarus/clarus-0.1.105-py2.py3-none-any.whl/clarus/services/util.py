import clarus.services

def activity(output=None, **params):
    return clarus.services.api_request('Util', 'Activity', output=output, **params)

def assetpricedefinition(output=None, **params):
    return clarus.services.api_request('Util', 'AssetPriceDefinition', output=output, **params)

def bonddefinition(output=None, **params):
    return clarus.services.api_request('Util', 'BondDefinition', output=output, **params)

def dataframetransform(output=None, **params):
    return clarus.services.api_request('Util', 'DataframeTransform', output=output, **params)

def domain(output=None, **params):
    return clarus.services.api_request('Util', 'Domain', output=output, **params)

def generatetradex(output=None, **params):
    return clarus.services.api_request('Util', 'GenerateTradeX', output=output, **params)

def grid(output=None, **params):
    return clarus.services.api_request('Util', 'Grid', output=output, **params)

def mailgrid(output=None, **params):
    return clarus.services.api_request('Util', 'MailGrid', output=output, **params)

def oisindex(output=None, **params):
    return clarus.services.api_request('Util', 'OISIndex', output=output, **params)

def periodlength(output=None, **params):
    return clarus.services.api_request('Util', 'PeriodLength', output=output, **params)

def referenceentitydefinition(output=None, **params):
    return clarus.services.api_request('Util', 'ReferenceEntityDefinition', output=output, **params)

def report(output=None, **params):
    return clarus.services.api_request('Util', 'Report', output=output, **params)

def risktransform(output=None, **params):
    return clarus.services.api_request('Util', 'RiskTransform', output=output, **params)

def shiftsetgenerator(output=None, **params):
    return clarus.services.api_request('Util', 'ShiftSetGenerator', output=output, **params)

def simmcrifquotecodelookup(output=None, **params):
    return clarus.services.api_request('Util', 'SimmCrifQuoteCodeLookup', output=output, **params)

def simmcrifquotes(output=None, **params):
    return clarus.services.api_request('Util', 'SimmCrifQuotes', output=output, **params)

def swapquotecodedefinition(output=None, **params):
    return clarus.services.api_request('Util', 'SwapQuoteCodeDefinition', output=output, **params)

def tickers(output=None, **params):
    return clarus.services.api_request('Util', 'Tickers', output=output, **params)

