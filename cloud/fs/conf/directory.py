import hashlib

from cloud.fs.models import service_get_directory
from freeswitch.directory import Domain, User

from .base import BaseXml


class Directory(BaseXml):
    def __init__(self, request):
        super().__init__(request)
        self.domain = self.request.data.get('domain')

    def generate_xml_conf(self, data):
        domain = self.domain
        self.xml = Domain(domain)
        self.xml.addParameter(
            'dial-string',
            '{^^:sip_invite_domain=${dialed_domain}:presence_id=${dialed_user}@${dialed_domain}}${sofia_contact(*/${dialed_user}@${dialed_domain})}'
        )
        self.xml.addVariable('use_profile', domain)
        for row in data:
            username = row.get('username', None)
            password = row.get('password', None)
            eff_caller = row.get('username', None)
            user = User(username, cacheable=6000)
            user.addParameter('a1-hash',
                              self._hash_password(domain, username, password))
            user.addVariable('effective_caller_id_number', eff_caller)
            user.addVariable('user_context', domain)
            self.xml.addUser(user)

    def get_xml_data(self):
        # print(self.request.data)
        return service_get_directory(self.domain)

    def _hash_password(self, domain, username, password):
        hash = hashlib.md5()
        hash.update((username + ":" + domain + ":" + password).encode('utf8'))
        password_hash = hash.hexdigest()
        return password_hash
