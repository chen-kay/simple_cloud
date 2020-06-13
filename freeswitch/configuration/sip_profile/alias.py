import logging

log = logging.getLogger(__name__)


class Alias(object):
    """A alias of a configuration object"""
    def __init__(self, name):
        super(Alias, self).__init__()
        self.name = name

    def todict(self):
        '''
            Convert Section to a dictionary
        '''

        return {
            'tag': 'alias',
            'attrs': {
                'name': '%s' % self.name,
            }
        }
