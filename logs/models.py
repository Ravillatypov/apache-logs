from django.db import models


class AccessLog(models.Model):
    ip = models.GenericIPAddressField(verbose_name='IP адрес', default='', db_index=True)
    date = models.DateTimeField(verbose_name='Дата и время', db_index=True, null=True)
    method = models.CharField(verbose_name='HTTP метод', max_length=10, db_index=True)
    path = models.CharField(verbose_name='Путь', max_length=255, default='')
    response_code = models.SmallIntegerField(verbose_name='Код ответа', null=True)
    response_size = models.IntegerField(verbose_name='Размер ответа', null=True, db_index=True)
    user_agent = models.CharField(verbose_name='Агент', max_length=255, null=True)

    def __str__(self):
        return f'[{self.date}] {self.ip}, {self.method}, {self.path}'

    class Meta:
        ordering = ('-date',)
        index_together = ('ip', 'method')
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'


class Parsing(models.Model):
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(db_index=True)
    url = models.URLField()
    content_length = models.BigIntegerField()

    def __str__(self):
        return f'[{self.url}] {self.content_length}'

    class Meta:
        ordering = ('-started_at',)
        verbose_name = 'Парсинг'
        verbose_name_plural = 'Парсинг'
