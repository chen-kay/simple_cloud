from cloud.fs.conf.base import BaseXml
from cloud.fs.models import ServiceBackends as _backends
from cloud.fs.settings import fs_settings
from freeswitch.configuration import Section
from freeswitch.configuration.sip_profile import Profile
from freeswitch.configuration.sip_profile.external import external_settings
from freeswitch.configuration.sip_profile.gateway import Gateway
from freeswitch.configuration.sip_profile.internal import internal_settings


class Sofia(BaseXml):
    def __init__(self, request):
        super().__init__(request)
        self.profile = request.data.get('profile', None)

    def render_xml(self):
        data = self.get_xml_data()
        self.generate_xml_conf(data)

    def generate_xml_conf(self, data):
        gateway = data
        self.profiles = Section('profiles')
        self.generate_external_xml(gateway)
        self.generate_internal_xml()
        self.xml.addSection(self.profiles)

    def get_xml_data(self):
        return _backends.service_get_gateway()

    def generate_external_xml(self, data):
        '''
        '''
        profiles = self.profiles
        profile = Profile('external')
        for key, value in external_settings.items():
            _val = self.get_default_external(key)
            profile.addParameter(key, _val if _val else value)
        profile.addGateway(self.__default_gateway())
        for item in data:
            name = item.get('gateway_name', '')
            realm = item.get('realm', '')
            username = item.get('username', '')
            password = item.get('password', '')
            register = item.get('register', False)
            if not name or not realm:
                continue
            if register and (not username or not password):
                continue
            gateway = Gateway(name)
            gateway.addParameter('realm', realm)
            if register:
                gateway.addParameter('username', username)
                gateway.addParameter('password', password)
            gateway.addParameter('from-user', '')
            gateway.addParameter('from-domain', '')
            gateway.addParameter('caller-id-in-from', 'true')
            gateway.addParameter('register', register)
            profile.addGateway(gateway)
        profiles.addVariable(profile)

    def generate_internal_xml(self):
        '''
        '''
        profiles = self.profiles
        profile = Profile('internal')
        for key, value in internal_settings.items():
            _val = self.get_default_internal(key)
            profile.addParameter(key, _val if _val else value)
        # for item in data:
        #     alias = Alias(item.get('name', ''))
        #     profile.addAlias(alias)
        profiles.addVariable(profile)

    def get_default_external(self, key):
        default = self._external_settings
        if key in default:
            return default[key]
        return None

    def get_default_internal(self, key):
        default = self._internal_settings
        if key in default:
            return default[key]
        return None

    @property
    def _external_settings(self):
        return {
            'sip-port': fs_settings.DEFAULT_EXTERNAL_SIP_PORT,
            'ext-rtp-ip': fs_settings.DEFAULT_EXT_RTP_IP,
            'ext-sip-ip': fs_settings.DEFAULT_EXT_SIP_IP,
        }

    @property
    def _internal_settings(self):
        return {
            'sip-port': fs_settings.DEFAULT_INTERNAL_SIP_PORT,
            'ext-rtp-ip': fs_settings.DEFAULT_EXT_RTP_IP,
            'ext-sip-ip': fs_settings.DEFAULT_EXT_SIP_IP,
            'ws-binding': fs_settings.DEFAULT_WS_BINDING,
            'wss-binding': fs_settings.DEFAULT_WSS_BINDING,
        }

    def __default_gateway(self):
        gateway = Gateway(fs_settings.DEFAULT_GATEWAY_NAME)
        for key, value in fs_settings.DEFAULT_GATEWAY.items():
            gateway.addParameter(key, value)
        return gateway
