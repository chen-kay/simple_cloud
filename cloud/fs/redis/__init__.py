from .call import CallRedis
from .domain import DomainRedis
from .gateway import GatewayRedis
from .monitor import MonitorRedis
from .project import ProjectRedis
from .user import UserRedis

call = CallRedis()
domain = DomainRedis()
gateway = GatewayRedis()
project = ProjectRedis()
user = UserRedis()
monitor = MonitorRedis()