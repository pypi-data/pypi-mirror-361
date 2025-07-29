from .gateway import CoreGateway
from .http_gateway import HttpCoreGateway

def get_core_gateway() -> CoreGateway:
    return HttpCoreGateway()
