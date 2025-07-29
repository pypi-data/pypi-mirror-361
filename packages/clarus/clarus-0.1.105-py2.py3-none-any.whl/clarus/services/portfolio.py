import clarus.services

def cash(output=None, **params):
    return clarus.services.api_request('Portfolio', 'Cash', output=output, **params)

def cashbydate(output=None, **params):
    return clarus.services.api_request('Portfolio', 'CashByDate', output=output, **params)

def cashvm(output=None, **params):
    return clarus.services.api_request('Portfolio', 'CashVM', output=output, **params)

def fd_mtm(output=None, **params):
    return clarus.services.api_request('Portfolio', 'FD_MTM', output=output, **params)

def fixings(output=None, **params):
    return clarus.services.api_request('Portfolio', 'Fixings', output=output, **params)

def mtm(output=None, **params):
    return clarus.services.api_request('Portfolio', 'MTM', output=output, **params)

def notional(output=None, **params):
    return clarus.services.api_request('Portfolio', 'Notional', output=output, **params)

def position(output=None, **params):
    return clarus.services.api_request('Portfolio', 'Position', output=output, **params)

def simm_mtm(output=None, **params):
    return clarus.services.api_request('Portfolio', 'SIMM_MTM', output=output, **params)

def summary(output=None, **params):
    return clarus.services.api_request('Portfolio', 'Summary', output=output, **params)

def trades(output=None, **params):
    return clarus.services.api_request('Portfolio', 'Trades', output=output, **params)

def vm_mtm(output=None, **params):
    return clarus.services.api_request('Portfolio', 'VM_MTM', output=output, **params)

