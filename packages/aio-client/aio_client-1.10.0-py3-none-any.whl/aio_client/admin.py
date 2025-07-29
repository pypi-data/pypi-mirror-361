# coding: utf-8
from django.contrib import admin

from aio_client.base.models import RequestLog
from aio_client.consumer.helpers import consumer_post_request
from aio_client.consumer.models import GetConsumerReceipt
from aio_client.consumer.models import GetConsumerResponse
from aio_client.consumer.models import PostConsumerRequest
from aio_client.provider.helpers import provider_post_request
from aio_client.provider.models import GetProviderReceipt
from aio_client.provider.models import GetProviderRequest
from aio_client.provider.models import PostProviderRequest


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp_created', 'request_type')
    list_filter = ('request_type', 'state')
    date_hierarchy = 'timestamp_created'

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


class MessageLogAdmin(admin.ModelAdmin):
    # поле state изменяется только в модели GetProviderRequest в апи функциии
    list_display = ('message_id', 'origin_message_id', 'display_created',
                    'message_type', 'state', 'request_error', 'request_state')
    list_filter = ('message_type', 'state')
    list_select_related = ('request_id',)
    # date_hierarchy = 'request_id__timestamp_created'
    search_fields = ('message_id', 'origin_message_id')
    raw_id_fields = ('request_id',)

    def display_created(self, obj):
        return obj.request_id.timestamp_created

    display_created.short_description = u'Создан'

    def request_state(self, obj):
        return RequestLog.get_state_name(obj.request_id.state)
    request_state.short_description = u'Статус запроса'

    def request_error(self, obj):
        return obj.request_id.error
    request_error.short_description = u'Текст ошибки запроса'


@admin.register(GetProviderRequest)
class GetProviderRequestAdmin(MessageLogAdmin):
    """Поставщик. Заявка от СМЭВ"""

    fields = ('state', 'request_id', 'message_type', 'message_id',
              'origin_message_id', 'body', 'attachments', 'is_test_message',
              'replay_to')
    search_fields = ('message_id', 'origin_message_id', 'body')


@admin.register(GetConsumerResponse)
class GetConsumerResponseAdmin(MessageLogAdmin):
    """Потребитель. Ответ СМЭВ"""

    fields = ('state', 'request_id', 'message_type', 'message_id',
              'origin_message_id', 'body', 'attachments',
              'content_failure_code', 'content_failure_comment')
    search_fields = ('message_id', 'origin_message_id', 'body')

    actions = (
        'set_not_sent',
    )

    def set_not_sent(self, request, queryset):
        """Установить статус 'Не отправлено' для выбранных записей"""

        queryset.update(state=GetConsumerResponse.NOT_SENT)

    set_not_sent.short_description = ('Установить статус '
                                      '"Не отправлено" для выбранных '
                                      'Потребитель.Ответ СМЭВs')


# У исходящих запросов в случае ошибки заполняется request_id.state
# поэтому показываем его в пост моделях
@admin.register(PostProviderRequest, PostConsumerRequest)
class PostRequestAdmin(MessageLogAdmin):
    list_filter = ('message_type', 'request_id__state', 'request_id__error')
    search_fields = ('message_id', 'origin_message_id', 'body')

    def send_error_requests(self, request, queryset):
        not_send = 0
        queryset = queryset.select_related('request_id')
        for obj in queryset:
            if obj.request_id.state != RequestLog.ERROR:
                not_send += 1
                continue
            if isinstance(obj, PostProviderRequest):
                provider_post_request(obj)
            else:
                consumer_post_request(obj)
        self.message_user(
            request,
            u"%d отправили" % (queryset.count()-not_send))

    send_error_requests.short_description = (
        u"Повторно отправить сообщения в статусе ошибка")

    actions = [send_error_requests]


admin.site.register(
    (
        GetConsumerReceipt,
        GetProviderReceipt,
    ),
    MessageLogAdmin
)
