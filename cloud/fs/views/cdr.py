from lxml import etree
from rest_framework.response import Response
from rest_framework.views import APIView

# from cloud.fs.models import service_cdr_handle


class cdrHandle:
    def __init__(self, uuid, data):
        self.status = 2
        try:
            self.xml = etree.XML(data)
        except Exception:
            self.xml = None

    def save_cdr_data(self):
        pass

    @property
    def username(self):
        pass


class CdrViews(APIView):
    '''话单处理
    '''
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        a_uuid = request.GET.get('uuid')
        cdr = request.data.get('cdr', None)
        handle = cdrHandle(a_uuid, cdr)
        # if cdr:
        #     service_cdr_handle(a_uuid, cdr)
        return Response()
