import subprocess

try:
    import win32api
    import win32print
except:
    pass

import settings


def print_label(data):
    """Create a pdf label and send it to the printer."""

    # Label will report these values
    product = data['product']
    weight = "%.0f" % data['weight']
    date = data['date']

    # Open the rst file we use as a template to create labels
    template = open(settings.RST2PDF_TEMPLATE, 'r').read().decode('utf-8')

    # Replace wildcards with current real values
    template = template.replace('{{ product }}', product)
    template = template.replace('{{ weight }}', weight)
    template = template.replace('{{ date }}', date)

    # Use this to avoid problems with utf-8 content
    template = template.encode('utf-8')

    # Write and save the rst file
    rst_file = open(settings.RST2PDF_RST, 'w')
    rst_file.write(template)
    rst_file.close()

    # Run external program rst2pdf
    cmd = [
        settings.RST2PDF_CMD, # rst2pdf executable
        settings.RST2PDF_RST, # rst input file
        '-o',
        settings.RST2PDF_PDF, # pdf output file
        '-s',
        settings.RST2PDF_CONF # conf file
        ]
    subprocess.call(cmd)

    # Print!
    try:
        # See snippet from http://stackoverflow.com/questions/4498099/silent-printing-of-a-pdf-in-python
        # p = subprocess.Popen(
        #     [r'C:\Program Files\Ghostgum\gsview\gsprint.exe', settings.RST2PDF_PDF], 
        #     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # stdout, stderr = p.communicate()
        # print stdout
        # print stderr

        # See snippet from http://timgolden.me.uk/python/win32_how_do_i/print.html
        win32api.ShellExecute(0, 'print', settings.RST2PDF_PDF, None, '.', 0)
    except Exception as ex:
        print ex
