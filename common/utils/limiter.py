<<<<<<< HEAD
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# 限流器
limiter = Limiter(key_func=get_remote_address)
=======
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# 限流器
limiter = Limiter(key_func=get_remote_address)
>>>>>>> e834388b2bd5275608c69e52dec55b044d66af04
