# Generated by Django 5.2.3 on 2025-06-13 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interfacetestplatform', '0004_rename_test_testcase_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseSuite',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('suite_desc', models.CharField(blank=True, max_length=100, null=True, verbose_name='用例集合描述')),
                ('if_execute', models.CharField(default=0, help_text='0:执行，1：不执行', verbose_name='是否执行')),
                ('test_case_model', models.CharField(blank=True, help_text='data/keyword', max_length=100, null=True, verbose_name='测试执行模式')),
                ('creator', models.CharField(blank=True, max_length=50, null=True, verbose_name='创建人')),
                ('create_time', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '用例集合表',
                'verbose_name_plural': '用例集合表',
            },
        ),
    ]
