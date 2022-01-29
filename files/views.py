from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.http import HttpResponse

from rest_framework.viewsets import ModelViewSet

from files.serializers import FileSerializer
from files.models import File

import mimetypes


class FileViewSet(ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]

    @action(methods=['get'], detail=True)
    def download(self, request, pk=None):
        _file = get_object_or_404(File, pk=pk)
        response = HttpResponse(_file.file)

        file_type, encoding = mimetypes.guess_type(_file.file_name)
        if file_type is None:
            file_type = 'application/octet-stream'

        response['Content-Type'] = file_type
        response['Content-Length'] = str(_file.file.size)
        if encoding is not None:
            response['Content-Encoding'] = encoding

        if u'WebKit' in request.META['HTTP_USER_AGENT']:
            # Safari 3.0 and Chrome 2.0
            filename_header = 'filename=%s' % _file.file_name
        elif u'MSIE' in request.META['HTTP_USER_AGENT']:
            # IE does not support internationalized filename at all
            filename_header = ''
        else:
            # For others like Firefox
            filename_header = 'filename*=UTF-8\'\'%s' % _file.file_name

        response['Content-Disposition'] = 'attachment; ' + filename_header
        return response

    def perform_create(self, serializer):
        serializer.save(file_name=serializer.validated_data['file'].name)


@receiver(post_delete, sender=File)
def submission_delete(sender, instance, **kwargs):
    instance.file.delete(False)
