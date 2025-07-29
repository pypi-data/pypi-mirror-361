import pytest
import redis
from unittest.mock import MagicMock, patch
import asyncio
from siges_sdk.queues import (
    QueueMessageProducer,
    QueueMessageConsumer,
    get_message_producer
)
from siges_sdk.queues.redis_message_producer import RedisMessageProducer
from siges_sdk.queues.redis_message_consumer import RedisQueueMessageConsumer

def test_message_producer_provider():
    """Test que verifica que el proveedor de productor de mensajes devuelve una instancia correcta"""
    producer = get_message_producer()
    assert isinstance(producer, QueueMessageProducer)
    assert isinstance(producer, RedisMessageProducer)

@patch('redis.Redis')
def test_redis_message_producer_send(mock_redis):
    """Test que verifica el envío de mensajes a través del productor Redis"""
    # Configurar el mock
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance
    
    # Crear el productor
    producer = RedisMessageProducer()
    
    # Enviar un mensaje
    queue_name = "test-queue"
    message = {"key": "value", "test": 123}
    producer.send_message(queue_name, message)
    
    # Verificar que se llamó a xadd con los parámetros correctos
    mock_redis_instance.xadd.assert_called_once()
    args, kwargs = mock_redis_instance.xadd.call_args
    assert args[0] == queue_name
    # El mensaje debe incluir un ID generado
    assert "id" in kwargs or (len(args) > 1 and "id" in args[1])

@patch('redis.Redis')
def test_redis_message_consumer_init(mock_redis):
    """Test que verifica la inicialización correcta del consumidor Redis"""
    # Configurar el mock
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance
    
    # Crear una función de callback
    async def callback(message):
        return True
    
    # Crear el consumidor
    queue_name = "test-queue"
    consumer_group = "test-group"
    consumer = RedisQueueMessageConsumer(
        queue_name=queue_name,
        callback=callback,
        consumer_group=consumer_group
    )
    
    # Verificar que se inicializó correctamente
    assert consumer.queue_name == queue_name
    assert consumer.callback == callback
    assert consumer.consumer_group == consumer_group
    assert consumer.is_running == False
    
    # Verificar que se llamó a xgroup_create
    mock_redis_instance.xgroup_create.assert_called_once_with(
        name=queue_name,
        groupname=consumer_group,
        mkstream=True,
        id='0'
    )

@patch('redis.Redis')
def test_redis_message_consumer_start_stop(mock_redis):
    """Test que verifica el inicio y detención del consumidor Redis"""
    # Configurar el mock
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance
    
    # Crear una función de callback
    async def callback(message):
        return True
    
    # Crear el consumidor
    consumer = RedisQueueMessageConsumer(
        queue_name="test-queue",
        callback=callback,
        consumer_group="test-group"
    )
    
    # Iniciar el consumidor
    consumer.start()
    assert consumer.is_running == True
    
    # Detener el consumidor
    consumer.stop()
    assert consumer.is_running == False

@patch('redis.Redis')
def test_redis_message_consumer_with_max_length(mock_redis):
    """Test que verifica la configuración de max_stream_length en el consumidor Redis"""
    # Configurar el mock
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance
    
    async def callback(message):
        return True
    
    # Crear el consumidor con max_stream_length
    queue_name = "test-queue"
    consumer_group = "test-group"
    max_length = 1000
    
    consumer = RedisQueueMessageConsumer(
        queue_name=queue_name,
        callback=callback,
        consumer_group=consumer_group,
        max_stream_length=max_length
    )
    
    # Verificar que se llamó a xadd para configurar el max_length
    mock_redis_instance.xadd.assert_called_once_with(
        queue_name,
        {'dummy': 'dummy'},
        maxlen=max_length,
        approximate=True
    )
    
    # Verificar que se eliminó el mensaje dummy
    mock_redis_instance.xdel.assert_called_once_with(queue_name, '0-0')

@patch('redis.Redis')
def test_redis_message_consumer_process_message(mock_redis):
    """Test que verifica el procesamiento de mensajes en el consumidor Redis"""
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance
    
    # Simular mensajes en la cola
    mock_redis_instance.xreadgroup.side_effect = [
        [[b'test-queue', [(b'1234-0', {b'key': b'value'})]]],  # Primera llamada
        None  # Segunda llamada
    ]
    
    processed_messages = []
    async def callback(message):
        processed_messages.append(message)
    
    consumer = RedisQueueMessageConsumer(
        queue_name="test-queue",
        callback=callback,
        consumer_group="test-group"
    )
    
    # Iniciar y detener rápidamente para procesar un mensaje
    consumer.start()
    # Esperar un momento para que se procese el mensaje
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.1))
    consumer.stop()
    
    # Verificar que se procesó el mensaje
    assert len(processed_messages) == 1
    assert b'key' in processed_messages[0]
    
    # Verificar que se confirmó el mensaje
    mock_redis_instance.xack.assert_called_with(
        "test-queue",
        "test-group",
        b'1234-0'
    )

@patch('redis.Redis')
def test_redis_message_consumer_error_handling(mock_redis):
    """Test que verifica el manejo de errores en el consumidor Redis"""
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance
    
    # Simular un error en xreadgroup
    mock_redis_instance.xreadgroup.side_effect = redis.RedisError("Test error")
    
    async def callback(message):
        return True
    
    consumer = RedisQueueMessageConsumer(
        queue_name="test-queue",
        callback=callback,
        consumer_group="test-group"
    )
    
    # El consumidor debería manejar el error sin fallar
    consumer.start()
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.1))
    consumer.stop()
    
    # Verificar que se intentó leer mensajes
    assert mock_redis_instance.xreadgroup.called 