import httpx
from .gateway import CoreGateway, PluginRegister
import logging

logger = logging.getLogger(__name__)

class PluginRegisterRequest:
    def __init__(self, plugin_register: PluginRegister):
        self.plugin_register = plugin_register

    def to_dict(self) -> dict:
        return self.plugin_register.to_dict()

class HttpCoreGateway(CoreGateway):
    """
    Implementación HTTP del gateway para comunicarse con el core.
    """
    def __init__(self, core_url: str = "http://core"):
        self.core_url = core_url
    
    async def register_plugin(self, plugin_register: PluginRegister) -> None:
        """
        Registra un plugin en el core mediante una solicitud HTTP.
        
        Args:
            plugin_register: Solicitud de registro del plugin
        
        Raises:
            Exception: Si ocurre un error al registrar el plugin
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.core_url}/plugin/register", 
                    json=PluginRegisterRequest(plugin_register).to_dict(),
                    timeout=10.0
                )
                if response.status_code != 200:
                    raise Exception(f"Error al registrar plugin: {response.json()}")
                logger.info(f"Plugin {plugin_register.name} registrado correctamente")
            except httpx.RequestError as e:
                logger.error(f"Error de conexión al registrar plugin: {e}")
                raise Exception(f"Error de conexión al registrar plugin: {e}")
