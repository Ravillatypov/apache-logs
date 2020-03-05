from django.db import models


class AccessLog(models.Model):
    ip = models.CharField(verbose_name='IP адрес', max_length=15, default='', db_index=True)
    date = models.DateTimeField(verbose_name='Дата и время', db_index=True, null=True)
    method = models.CharField(verbose_name='HTTP метод', max_length=6)
    path = models.CharField(verbose_name='Путь', max_length=255, default='')
    response_code = models.SmallIntegerField(verbose_name='Код ответа', null=True)
    response_size = models.IntegerField(verbose_name='Размер ответа', null=True)
    user_agent = models.CharField(verbose_name='Агент', max_length=255, null=True)

    def __str__(self):
        return f'[{self.date}] {self.ip}, {self.method}, {self.path}'

    class Meta:
        ordering = ('date',)
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'
