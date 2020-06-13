import logging

from .alias import Alias
from .domain import Domain
from .gateway import Gateway

log = logging.getLogger(__name__)


class Profile(object):
    alias = Alias
    domain = Domain
    gateway = Gateway
    """A profile of a configuration object"""
    def __init__(self, name):
        super(Profile, self).__init__()
        self.name = name
        self.gateways = []
        self.aliases = []
        self.parameters = []

    def addGateway(self, gateway):
        '''Add gateway to profile
        
        :param gateway: The gateway to add to the profile.
        :type gateway: object
        '''
        self.gateways.append(gateway)

    def addAlias(self, alias):
        '''Add alias to profile
        
        :param alias: The alias to add to the profile.
        :type alias: object
        '''
        self.aliases.append(alias)

    def addParameter(self, param, val):
        '''
            Set an extra parameter for a profile
        '''
        if not self.parameters:
            self.parameters = []
        try:
            self.getParameter(param)
        except ValueError:
            self.parameters.append({'name': param, 'value': val})
            return

        log.warning('Cannot replace existing parameter.')
        raise ValueError

    def getParameter(self, param):
        '''
            Retrieve the value of a parameter by its name
        '''
        if self.parameters:
            for p in self.parameters:
                if p.get('name') == param:
                    return p.get('value')

        raise ValueError

    def todict(self):
        '''
            Convert Section to a dictionary
        '''
        children = []
        if self.gateways:
            children.append({
                'tag': 'gateways',
                'children': [n.todict() for n in self.gateways]
            })
        if self.aliases:
            children.append({
                'tag': 'aliases',
                'children': [n.todict() for n in self.aliases]
            })
        if self.parameters:
            children.append({
                'tag':
                'settings',
                'children': [{
                    'tag': 'param',
                    'attrs': p
                } for p in self.parameters]
            })

        return {
            'tag': 'profile',
            'children': children,
            'attrs': {
                'name': '%s' % self.name,
            }
        }
