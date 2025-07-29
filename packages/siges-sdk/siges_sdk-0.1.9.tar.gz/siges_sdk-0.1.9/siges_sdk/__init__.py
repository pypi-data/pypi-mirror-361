__version__ = "0.1.9"

# Importar los subpaquetes para asegurar que estén disponibles
import siges_sdk.core
import siges_sdk.queues

__all__ = ["core", "queues"]