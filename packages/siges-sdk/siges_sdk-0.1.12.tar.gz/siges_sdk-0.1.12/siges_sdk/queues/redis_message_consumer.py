from concurrent.futures import ThreadPoolExecutor
import asyncio
import redis
import time
from typing import Callable, Any, Optional
from siges_sdk.queues.message_consumer import QueueMessageConsumer

class RedisQueueMessageConsumer(QueueMessageConsumer):
    redis_host = 'redis'
    redis_port = 6379
    redis_db = 0

    def __init__(self, 
                 queue_name: str, 
                 callback: Callable[[dict], Any], 
                 consumer_group: str,
                 max_stream_length: Optional[int] = None):
        """
        Args:
            queue_name: Nombre del stream de Redis
            callback: Función a ejecutar cuando se recibe un mensaje
            consumer_group: Nombre del grupo de consumidores
            max_stream_length: Número máximo de mensajes a mantener en el stream
        """
        super().__init__(queue_name, callback)
        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.is_running = False
        self.consumer_group = consumer_group
        self.consumer_name = f"{consumer_group}-{time.time()}"
        self.max_stream_length = max_stream_length
        self._ensure_stream_and_group()

    def _ensure_stream_and_group(self):
        """Asegura que exista el stream y el grupo de consumidores"""
        try:
            # Crear el grupo si no existe
            self.redis_client.xgroup_create(
                name=self.queue_name,
                groupname=self.consumer_group,
                mkstream=True,
                id='0'  # Comenzar desde el primer mensaje
            )
        except redis.exceptions.ResponseError as e:
            # Ignorar error si el grupo ya existe
            if 'BUSYGROUP' not in str(e):
                raise

        # Configurar la política de retención si se especificó
        if self.max_stream_length:
            self.redis_client.xadd(
                self.queue_name, 
                {'dummy': 'dummy'}, 
                maxlen=self.max_stream_length, 
                approximate=True
            )
            self.redis_client.xdel(self.queue_name, '0-0')  # Eliminar mensaje dummy

    def _consumer_thread(self):
        """Thread dedicado para consumir mensajes de Redis"""
        async def process_message(message_data):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                await self.callback(message_data)
            except Exception as e:
                print(f"Error procesando mensaje de {self.queue_name}: {str(e)}")
            finally:
                loop.close()

        while self.is_running:
            try:
                # Leer mensajes pendientes para este consumidor
                messages = self.redis_client.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams={self.queue_name: '>'},
                    count=1,
                    block=5000
                )

                if messages:
                    for stream, stream_messages in messages:
                        for message_id, message_data in stream_messages:
                            loop = asyncio.new_event_loop()
                            loop.run_until_complete(process_message(message_data))
                            # Marcar el mensaje como procesado por este consumidor
                            self.redis_client.xack(self.queue_name, self.consumer_group, message_id)

            except Exception as e:
                print(f"Error en consumer thread de {self.queue_name}: {str(e)}")
                time.sleep(1)

    def start(self):
        """Inicia el consumidor de la cola"""
        self.is_running = True
        self.future = self.executor.submit(self._consumer_thread)
        return self

    def stop(self):
        """Detiene el consumidor de la cola"""
        self.is_running = False
        self.executor.shutdown(wait=False)