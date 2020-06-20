from django.http.response import HttpResponse
from rest_framework.views import APIView

from cloud.fs.conf import xml, base

import traceback


class ConfigViews(APIView):
    '''服务配置
    '''
    authentication_classes = []
    permission_classes = []

    @base.print_run_time
    def post(self, request, *args, **kwargs):
        config = xml.XmlConfig(request)
        try:
            config.render_xml()
        except Exception as e:
            print(request.data, e)
            traceback.print_exc()
            raise e
        return HttpResponse(config.to_xml(), content_type='text/xml')

