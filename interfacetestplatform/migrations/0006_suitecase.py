# Generated by Django 5.2.3 on 2025-06-13 14:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interfacetestplatform', '0005_casesuite'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuiteCase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.IntegerField(default=1, help_text='0：有效，1：无效', verbose_name='是否有效')),
                ('create_time', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
                ('case_suite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interfacetestplatform.casesuite', verbose_name='用例集合')),
                ('test_case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interfacetestplatform.testcase', verbose_name='测试用例')),
            ],
        ),
    ]
