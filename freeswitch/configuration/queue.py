import logging

log = logging.getLogger(__name__)

__all__ = ['Queue']


class Queue(object):
    def __init__(self, name):
        super(Queue, self).__init__()
        self.name = name
        self.parameters = []

    def addParameter(self, param, val):
        try:
            self.getParameter(param)
        except ValueError:
            self.parameters.append({'name': param, 'value': val})
            return

        log.warning('Cannot replace existing parameter.')
        raise ValueError

    def getParameter(self, param):
        for p in self.parameters:
            if p.get('name') == param:
                return p.get('value')

        raise ValueError

    def todict(self):
        if self.parameters:
            children = [{'tag': 'param', 'attrs': p} for p in self.parameters]

        return {
            'tag': 'queue',
            'children': children,
            'attrs': {
                'name': self.name
            }
        }
