import datetime

import json

from django.contrib import admin

from cnap.models import *

import os
import uuid
import datetime
import simple_history
from import_export.admin import ExportActionMixin

from dateutil.relativedelta import relativedelta

from django.contrib import admin, messages
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.forms import *
from django.http import HttpResponseRedirect
from django.core.files import File

import environ

import requests

from rangefilter.filters import DateRangeFilter

from django_tabbed_changeform_admin.admin import DjangoTabbedChangeformAdmin

from django_admin_multiple_choice_list_filter.list_filters import MultipleChoiceListFilter

from django.contrib.auth.models import Group, Permission

from cnap.generate_docx import template_to_pdf

from django.conf import settings

env = environ.Env()
MEDIA_URL = getattr(settings, 'MEDIA_URL')
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')

# ------------------------------ MODEL ------------------------------ #
"""
Адмін модель: Організації
"""
class RemoveAdminDefaultMessageMixin:

    def remove_default_message(self, request):
        storage = messages.get_messages(request)
        try:
            del storage._queued_messages[-1]
        except KeyError:
            pass
        return True

    def response_add(self, request, obj, post_url_continue=None):
        """override"""
        response = super().response_add(request, obj, post_url_continue)
        self.remove_default_message(request)
        return HttpResponseRedirect('../')
        # return response

    def response_change(self, request, obj):
        """override"""
        response = super().response_change(request, obj)
        self.remove_default_message(request)
        return response

    def response_delete(self, request, obj_display, obj_id):
        """override"""
        response = super().response_delete(request, obj_display, obj_id)
        self.remove_default_message(request)
        return response


class CertificateApplicationAdmin(DjangoTabbedChangeformAdmin, RemoveAdminDefaultMessageMixin, ExportActionMixin):
    # PERMISSIONS
    def has_add_permission(self, request, obj=None): 
        return True

    def has_change_permission(self, request, obj=None): 
        return True

    def has_delete_permission(self, request, obj=None): return False

    def save_model(self, request, obj, form, change):
        if obj.application_status == CertificateApplicationStatusType.CREATED:
            obj.application_status = CertificateApplicationStatusType.PROCESSING
            obj.save()

        if "_make_request" in request.POST:

            try:
                r = requests.get('http://ec2-3-74-215-137.eu-central-1.compute.amazonaws.com:8080/r1/XROAD-TEST/GOV/12341234/DRUGS_UNITED_INFOSYSTEM/get_medical_ensurance?person_unique_code=' + obj.applicant_unique_code, headers={'X-Road-Client': 'XROAD-TEST/CNAP/00000001/CNAP_INFO_SYSTEM'})
                r.raise_for_status()

                response_data = r.json()

                if response_data['status'] == "success":
                    obj.applicant_fullname = response_data['data']['person_fullname']
                    obj.applicant_home_address = response_data['data']['person_home_address']
                    obj.applicant_medical_ensurance = response_data['data']['person_medical_ensurance']
                    obj.application_status = CertificateApplicationStatusType.ON_REVIEW
                else:
                    obj.failure_reason = response_data['error_text']
                    obj.application_status = CertificateApplicationStatusType.FAILED

            except requests.exceptions.RequestException as err:
                print ("OOps: Something Else",err)
                obj.failure_reason = err

            except requests.exceptions.HTTPError as errh:
                print ("Http Error:",errh)
                obj.failure_reason = err

            except requests.exceptions.ConnectionError as errc:
                print ("Error Connecting:",errc)
                obj.failure_reason = err

            except requests.exceptions.Timeout as errt:
                print ("Timeout Error:",errt)
                obj.failure_reason = err

        if "_executed" in request.POST:
            context = {
                'applicant_fullname': obj.applicant_fullname,
                'applicant_home_address': obj.applicant_home_address,
                'applicant_medical_ensurance': obj.applicant_medical_ensurance,
            }

            file_uuid = template_to_pdf(context, '/vol/web/media', 0, file_name=str(uuid.uuid4()))
            obj.application_file = os.path.join(file_uuid + '.pdf')


        if "_rejected" in request.POST:
            print('None')


            # r = requests.get('http://3.74.215.137:8080/r1/XROAD-TEST/GOV/12341234/DRUGS_UNITED_INFOSYSTEM/get_user_information', params=request.POST, headers={'X-Road-Client': 'XROAD-TEST/CNAP/00000001/CNAP_INFO_SYSTEM'})
            # print(r)

        #     admin_comment = form.cleaned_data.get('admin_comment', None)

        #     if not admin_comment:
        #         self.message_user(request, 'Необхідно вказати причину відхилення',
        #                             messages.ERROR)
        #         return None

        #     obj.status = InformationResourceApplicationStatus.REJECTED
        #     obj.executed_by = request.user
        #     obj.executed_at = datetime.datetime.now()

        #     obj.save_with_auditlog_event(actor_permission=None, actor=request.user, event_type=HistoryEventType.REJECT_IRS_APPLICATION)
        #     # obj.save()
        # elif "_auto_executed" in request.POST:
        #     obj.status = InformationResourceApplicationStatus.COMPLETED
        #     obj.executed_by = request.user
        #     obj.executed_at = datetime.datetime.now()
        #     obj.save_with_auditlog_event(actor_permission=None, actor=request.user, event_type=HistoryEventType.EXECUTE_IRS_APPLICATION)

        #     if obj.application_type == InformationResourceApplicationType.CREATE:
        #         information_resource = InformationResource(
        #                         name=obj.name,
        #                         description=obj.description,
        #                         nreir_identifier=obj.nreir_identifier,
        #                         administrator_organization_name=obj.administrator_organization_name,
        #                         administrator_organization_code=obj.administrator_organization_code,
        #                         legal_basis=obj.legal_basis,
        #                         owner=obj.organization,
        #                         published=True,
        #                     )
        #         information_resource.save()
        #         information_resource.operators.set(obj.operators.all())

        #         obj.information_eresource = information_resource
        #         obj.save()
                
        #     else:
        #         information_resource = obj.information_eresource
            
        #     if obj.application_type == InformationResourceApplicationType.EDIT:
        #         information_resource.name=obj.name
        #         information_resource.description=obj.description
        #         information_resource.nreir_identifier=obj.nreir_identifier
        #         information_resource.administrator_organization_name=obj.administrator_organization_name
        #         information_resource.administrator_organization_code=obj.administrator_organization_code
        #         information_resource.legal_basis=obj.legal_basis
        #         information_resource.published=True
        #         information_resource.save()

        #     if obj.application_type == InformationResourceApplicationType.ADD_OPERATOR:
        #         information_resource.operators.set(obj.operators.all())

        #     if obj.application_type == InformationResourceApplicationType.DELETE_OPERATOR:
        #         # self.message_user(request, 'Необхідно повідомити адміністраторів про технічне виконання заявки на основі внесення змін.',
        #         #                     messages.ERROR)
        #         for op in obj.operators.all():
        #             information_resource.operators.remove(op)
        #             information_resource.past_operators.add(op)
        #         # self.message_user(request, 'Заглушка для технічних дій з боку адміністратора ДП ДІЯ.',
        #         #                     messages.ERROR)

        #     if obj.application_type == InformationResourceApplicationType.ARCHIVE:
        #         information_resource.is_deleted = True
        #         information_resource.save()

        #     if obj.application_type == InformationResourceApplicationType.UNARCHIVE:
        #         information_resource.is_deleted = False
        #         information_resource.save()

        #     if obj.application_type == InformationResourceApplicationType.PUBLISH:
        #         information_resource.published = True
        #         information_resource.save()

        #     if obj.application_type == InformationResourceApplicationType.DEPUBLISH:
        #         information_resource.published = False
        #         information_resource.save()
            
        super(CertificateApplicationAdmin, self).save_model(request, obj, form, change)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = CertificateApplication.objects.get(id=object_id)
        extra = extra_context or {}

        extra["obj"] = obj

        # print(obj.organization.member_code)
        
        return super(CertificateApplicationAdmin, self).change_view(request,
                                                             object_id,
                                                             form_url,
                                                             extra_context=extra)

    def get_readonly_fields(self, request, obj=None):
        readfields = ['id', 'application_status', 'created_at', 'updated_at', 'сertificate_no',
            'applicant_fullname',
            'applicant_home_address',
            'applicant_medical_ensurance',
            'application_file',
            'failure_reason',]
        return readfields
    #                 'sent_externally_by', 'sent_externally_at', 'created_by', 'confirmed_by', 'confirmed_at', 'signed_by', 'signed_at', 'operator_legal_basis',
    #                 'status_html', 'submitter', 'organization', 
    #                 'name', 'description', 'information_eresource', 'administrator_organization_name',
    #                 'administrator_organization_code', 'legal_basis', 'head_person_full_name',
    #                 'head_person_position', 'head_person_document', 'head_person_document_file',
    #                 'nreir_identifier', 'nreir_link', 'submitter_crud_reason', 'operators', 
    #                 'application_file', 'operator_legal_basis_file',
    #                 'sign_file', 'cancel_reason']
        
    #     if obj.status == InformationResourceApplicationStatus.COMPLETED or obj.status == InformationResourceApplicationStatus.REJECTED or obj.status == InformationResourceApplicationStatus.CANCELED:
    #         readfields += ['admin_comment']

    #     if obj.status != InformationResourceApplicationStatus.SENT_EXTERNALLY or obj.application_type in [InformationResourceApplicationType.PUBLISH, InformationResourceApplicationType.DEPUBLISH, InformationResourceApplicationType.ARCHIVE, InformationResourceApplicationType.UNARCHIVE]:
    #         readfields += ['additional_application_copy', 'application_external_sign_uploaded', 'registration_no', 'registration_date']
            
    #     if obj.application_type != InformationResourceApplicationType.CREATE or (obj.application_type == InformationResourceApplicationType.CREATE and (obj.status == InformationResourceApplicationStatus.COMPLETED or obj.status == InformationResourceApplicationStatus.REJECTED)):
    #         readfields += ['information_eresource']
        
    #     return readfields

    # def get_name(self, obj):
    #     return obj.information_eresource.name if obj.information_eresource else obj.name

    # get_name.short_description = 'Назва е-ресурсу'

    # def get_fieldsets(self, request, obj=None):
    #     fieldsets = super(InformationResourceApplicationAdmin, self).get_fieldsets(request, obj)
    #     if obj and obj.application_type in [InformationResourceApplicationType.ADD_OPERATOR, InformationResourceApplicationType.DELETE_OPERATOR]:
    #         fieldsets[3][1]['fields'] = [
    #             'operators',
    #             'operator_legal_basis',
    #             'operator_legal_basis_file',
    #             ('head_person_full_name', 'head_person_position',),
    #             ('head_person_document', 'head_person_document_file',),
    #             'application_file',
    #             'sign_file',
    #         ]

    #     if obj and obj.application_type in [InformationResourceApplicationType.PUBLISH, InformationResourceApplicationType.DEPUBLISH, InformationResourceApplicationType.ARCHIVE, InformationResourceApplicationType.UNARCHIVE]:
    #         fieldsets[3][1]['fields'] = []
            
    #     return fieldsets

    fieldsets = [
        (None, {'fields': [
            'id',
            'application_status',
            'applicant_unique_code',
            'сertificate_no',
            'applicant_fullname',
            'applicant_home_address',
            'applicant_medical_ensurance',
            'failure_reason',
            'application_file',
            'created_at',
            'updated_at',
        ],
        "classes": ["tab-detail"]}),
        ('Заявка', {'fields': [
            'application_file',
        ],
        "classes": ["tab-meta"]}),
    ]

    tabs = [
        ("Деталі", ["tab-detail"]),
        ("Заявка", ["tab-meta"]),
    ]
    
    list_display = ('id', 'application_status', )
    list_filter = (
        'application_status',
    )
    list_per_page = 40

    add_form_template = "changeform_template.html"
    change_form_template = "changeform_template.html"





class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'create_date', 'author')
    list_filter = ('title', 'create_date', 'author')
    readonly_fields = ['file_preview']
    exclude = ('author',)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()


    def file_preview(self, obj):
        html = 'Шаблон не завантажено'
        filename = obj.main_file
        if filename:
            _name, ext = os.path.splitext(str(filename))
            print(f'Название файла: {filename}')
            if ext == '.pdf':
                html = '<embed src=\'%s\' type=\'application/pdf\' width=\'850px\' height=\'800px\' />' % (
                    obj.main_file.url)
            elif ext in ['.jpg', '.png', '.jpeg', '.webp']:
                html = "<img src='%s'/>" % (obj.main_file.url)
            else:
                html = "<a href='%s' download>Неможливо вiдобразити файл. Натиснiть для завантаження</a>" % (
                    obj.main_file.url)
        return format_html(html)





admin.site.register(CertificateApplication, CertificateApplicationAdmin)
admin.site.register(Template, TemplateAdmin)

admin.site.index_title = "Обробка довідок"

