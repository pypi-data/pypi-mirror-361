import csv
try:
    from django.utils.six import StringIO
except ModuleNotFoundError:
    from io import StringIO

from django.http import HttpResponse, HttpRequest
from django.template.loader import render_to_string
from django.template.context import RequestContext
from functools import wraps


def render(template_name, request, context_data=None, response_type=HttpResponse, **kwargs):
    """
    renders template to an HttpResponse always giving RequestContext
    """
    content = render_to_string(template_name, context_data, context_instance=RequestContext(request))
    return response_type(content, **kwargs)


def render_to(template_name, response=HttpResponse):
    """
    decorator to allow a view to return a dictionary and render
    the contents to a template as an HttpResponse with RequestContext.

    USAGE:
    @render_to('myapp/my_template_name.html')
    def sample_view(response, *args, **kwargs):
        return {'some': 'data'}

    """

    def renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            """
            if the view returns something other than a context_data
            dictionary, maybe the user is returning a redirect or some
            other response, so we won't try to render to the template.
            """
            if not isinstance(request, HttpRequest):
                raise AssertionError("request is " + request.__class__.__name__ + ". Must be HttpRequest...")

            context_data = func(request, *args, **kwargs)
            if not isinstance(context_data, dict):
                return context_data
            return render(template_name, request, context_data, response)

        return wrapper

    return renderer


class CSVResponse(object):
    """
    Takes an iterable of dictionaries, converts their values to
    a csv format and delivers back an HttpResponse that will download
    the file for the user.

    ATTRIBUTES:
    file_name: what the file will be named when delivered (don't add .csv)
    field_names: a list of headers for the csv file in the order desired

    USAGE:
    def example_view(request):
        list_of_dictionaries = get_list_of_dictionaries() # i.e. do your query
        csv_response = CSVResponse(list_of_dictionaries)
        return csv_response.response

    """
    file_name = ""
    field_names = None

    def __init__(self, data_iterable):
        self.data_iterable = data_iterable

    @property
    def response(self):
        csv_data = self._create_csv()

        response = HttpResponse(csv_data)
        response["Content-Type"] = "text/csv"
        response["Content-Disposition"] = "attachment; filename={}.csv;".format(self.get_file_name())
        response["Content-Length"] = len(csv_data)
        return response

    def get_file_name(self):
        """
        Creates a download file name
        """
        _file_name = self.file_name or "download"
        return _file_name if not _file_name.endswith(".csv") else _file_name[:-4]

    def get_field_names(self):
        return self.field_names or []

    def get_header_row(self):
        field_names = self.get_field_names()
        return dict(zip(field_names, field_names))

    def _create_csv(self):
        """
        StringIO holds the csv data in a memory buffer that acts
        like a regular file. Python's csv library does all the
        heaving lifting and worrying about creating the csv properly.
        """
        fobj = StringIO()
        try:
            self._write_csv_contents(fobj)
            return fobj.getvalue()
        finally:
            fobj.close()

    def _write_csv_contents(self, fobj):
        """
        fobj should be a file like object DictWriter can write to.
        """
        writer = csv.DictWriter(fobj, fieldnames=self.get_field_names(), extrasaction="ignore")
        writer.writerow(self.get_header_row())
        writer.writerows(self.data_iterable)
