import socketio


# rabbitmq地址
RABBITMQ = 'amqp://admin:admin@81.68.197.3:5672/my_vhost'
JWT_SECRET = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA'


# 创建读取rabbitmq消息队列的管理对象
mgr = socketio.KombuManager(RABBITMQ)

# 创建socketio服务器对象
sio = socketio.Server(async_mode='eventlet', client_manager=mgr)

# app对象是交给eventlet服务器
app = socketio.Middleware(sio)
