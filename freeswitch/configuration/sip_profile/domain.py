import logging

log = logging.getLogger(__name__)


class Domain(object):
    """A domain of a configuration object"""
    def __init__(self, name, alias=True, parse=False):
        super(Domain, self).__init__()
        self.name = name
        self.alias = alias
        self.parse = parse

    def todict(self):
        '''
            Convert Section to a dictionary
        '''
        return {
            'tag': 'domain',
            'attrs': {
                'name': self.name,
                'alias': self.alias,
                'parse': self.parse
            }
        }
