import logging

log = logging.getLogger(__name__)


class Gateway(object):
    """A gateway of a configuration object"""
    def __init__(self, name):
        super(Gateway, self).__init__()
        self.name = name
        self.parameters = []

    def addParameter(self, param, val):
        '''Set an extra parameter for a gateway
        :param param: The paramenter to add
        :type param: str
        :param val: The value of the paramenter
        :type val: str
        :raises: ValueError -- in case the param already exists
        '''
        try:
            self.getParameter(param)
        except ValueError:
            self.parameters.append({'name': param, 'value': val})
            return

        log.warning('Cannot replace existing parameter.')
        raise ValueError

    def getParameter(self, param):
        '''Retrieve the value of a parameter by its name
        :rtype: str
        :raises: ValueError -- in case the param does not exist
        '''
        for p in self.parameters:
            if p.get('name') == param:
                return p.get('value')

        raise ValueError

    def todict(self):
        '''
            Convert Section to a dictionary
        '''
        children = []
        if self.parameters:
            children = [{'tag': 'param', 'attrs': p} for p in self.parameters]
        return {
            'tag': 'gateway',
            'children': children,
            'attrs': {
                'name': self.name
            }
        }
