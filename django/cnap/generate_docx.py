import sys
import subprocess
import re

import uuid
import os
from docxtpl import DocxTemplate
from cnap.models import Template


def convert_to(folder, source, timeout=None):
    args = [libreoffice_exec(), '--headless', '--convert-to',
            'pdf', '--outdir', folder, source]

    process = subprocess.run(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             timeout=timeout)
    filename = re.search('-> (.*?) using filter',
                         process.stdout.decode())

    if filename is None:
        raise LibreOfficeError(process.stdout.decode())
    else:
        return filename.group(1)


def libreoffice_exec():
    # TODO: Provide support for more platforms
    if sys.platform == 'darwin':
        return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    return 'libreoffice'


class LibreOfficeError(Exception):
    def __init__(self, output):
        self.output = output


def template_to_pdf(context, save_abs_path, template_number, file_name=None):
    if not file_name:
        file_name = str(uuid.uuid4())

    docx_file_name = file_name + '.docx'

    docx_path = os.path.join(save_abs_path, docx_file_name)

    print(docx_path)

    docx_template = Template.objects.get(request_trigger=template_number)
    doc = DocxTemplate(docx_template.main_file)

    doc.render(context)
    doc.save(docx_path)

    convert_to(save_abs_path, docx_path)
    return file_name
