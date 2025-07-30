try:
    from unittest import mock

except ImportError:
    import mock


from django.test import TestCase

from response_helpers import helpers


class CustomCSVResponse(helpers.CSVResponse):
    field_names = ["fox", "cat", "bat", "goat", "snake"]
    file_name = "foo.csv"
    data_iterable = [
        {
            "fox": "fox_1",
            "cat": "cat_1",
            "bat": "bat_1",
            "goat": "goat_1",
            "snake": "snake_1",
        },
        {
            "fox": "fox_2",
            "cat": "cat_2",
            "bat": "bat_2",
            "goat": "goat_2",
            "snake": "snake_2",
        },
    ]

    def get_field_names(self):
        return [_ for _ in sorted(self.field_names) if _.endswith("at")]

    def get_header_row(self):
        field_names = self.get_field_names()
        return dict(zip(field_names, map(lambda x: str(x).upper(), field_names)))


class CSVHelperResponseTests(TestCase):

    def setUp(self):
        pass

    def test_properties_default_when_not_defined(self):
        csv_response = helpers.CSVResponse([])
        self.assertEqual("", csv_response.file_name)
        self.assertEqual(None, csv_response.field_names)

        self.assertEqual("download", csv_response.get_file_name())
        self.assertEqual([], csv_response.get_field_names())

    def test_properties_updated_after_object_created(self):
        csv_response = helpers.CSVResponse([])

        self.assertEqual("", csv_response.file_name)
        self.assertEqual(None, csv_response.field_names)

        fields = ["field1", "field2"]
        file_name = "foo.csv"
        csv_response.field_names = fields
        csv_response.file_name = file_name
        self.assertEqual(fields, csv_response.field_names)
        self.assertEqual(file_name, csv_response.file_name)
        self.assertEqual("foo", csv_response.get_file_name())

    def test_get_file_name_returns_file_name_property(self):
        csv_response = helpers.CSVResponse([])
        file_name = "A File Name"
        csv_response.file_name = file_name
        self.assertEqual(file_name, csv_response.get_file_name())

    def test_get_field_names_returns_fields_names(self):
        csv_response = helpers.CSVResponse([])
        self.assertListEqual([], csv_response.get_field_names())

        csv_response.field_names = ["foo", "bar"]
        self.assertListEqual(["foo", "bar"], csv_response.get_field_names())

    def test_get_file_name_default_value_when_file_name_empty(self):
        csv_response = helpers.CSVResponse([])
        csv_response.file_name = ""
        self.assertEqual("download", csv_response.get_file_name())

    def test_get_file_name_removes_csv_extention(self):
        csv_response = helpers.CSVResponse([])

        csv_response.file_name = "foo.csv"
        self.assertEqual("foo", csv_response.get_file_name())

        csv_response.file_name = "bar.bux"
        self.assertEqual("bar.bux", csv_response.get_file_name())

        # only remove '.csv' if file extention
        csv_response.file_name = "save.as.csv.for.file.name"
        self.assertEqual("save.as.csv.for.file.name", csv_response.get_file_name())

    def test_turns_data_iterable_into_csv_in_create_csv(self):
        """
        Tests that we're writing out the header row and also all
        the items in our data iterable we sent in.
        """
        field_names = ["field1", "field2"]
        data_iterable = [
            {"field1": "test1.1", "field2": "test1.2"},
            {"field1": "test2.1", "field2": "test2.2"},
        ]
        csv_response = helpers.CSVResponse(data_iterable)
        csv_response.field_names = field_names
        result = csv_response._create_csv()
        self.assertEqual("field1,field2\r\ntest1.1,test1.2\r\ntest2.1,test2.2\r\n", result)

    def test_sets_response_content_to_csv_data(self):
        with mock.patch("response_helpers.helpers.CSVResponse._create_csv") as create_csv:
            csv_data = b"some,csv\r\ndata,here\r\n"
            create_csv.return_value = csv_data
            csv_response = helpers.CSVResponse([])

            response = csv_response.response
            self.assertEqual(csv_data, response.content)

    def test_custom_get_methods_returns_correct(self):
        test_obj = CustomCSVResponse(CustomCSVResponse.data_iterable)
        self.assertEqual(test_obj.field_names, ["fox", "cat", "bat", "goat", "snake"])
        self.assertEqual(test_obj.file_name, "foo.csv")
        self.assertEqual(test_obj.get_file_name(), "foo")
        self.assertEqual(test_obj.get_header_row(), {"bat": "BAT", "cat": "CAT", "goat": "GOAT"})

    def test_custom_get_methods_return_csv_of_data_as_content(self):
        csv_response = CustomCSVResponse(CustomCSVResponse.data_iterable)
        result = csv_response._create_csv()
        expected = ["BAT,CAT,GOAT", "bat_1,cat_1,goat_1", "bat_2,cat_2,goat_2", ""]
        self.assertEqual("\r\n".join(expected), result)

    @mock.patch("response_helpers.helpers.CSVResponse._write_csv_contents", mock.Mock())
    @mock.patch("response_helpers.helpers.StringIO")
    def test_closes_string_io_object_in_create_csv(self, string_io):
        io_object = string_io.return_value
        csv_response = helpers.CSVResponse([])
        csv_response._create_csv()
        io_object.close.assert_called_once_with()

    def test_sets_response_mime_type_to_text_csv(self):
        with mock.patch("response_helpers.helpers.CSVResponse._create_csv") as create_csv:
            create_csv.return_value = ""
            csv_response = helpers.CSVResponse([])

            response = csv_response.response
            self.assertEqual("text/csv", response["Content-Type"])

    def test_sets_response_content_disposition_to_attachment_and_filename(self):
        with mock.patch("response_helpers.helpers.CSVResponse._create_csv") as create_csv:
            create_csv.return_value = ""
            csv_response = helpers.CSVResponse([])
            csv_response.file_name = "csv_file"

            response = csv_response.response
            expected_disposition = "attachment; filename=csv_file.csv;"
            self.assertEqual(expected_disposition, response["Content-Disposition"])

    def test_sets_response_content_length_to_csv_data_length(self):
        with mock.patch("response_helpers.helpers.CSVResponse._create_csv") as create_csv:
            csv_data = "some,csv\r\ndata,here\r\n"
            create_csv.return_value = csv_data
            csv_response = helpers.CSVResponse([])

            response = csv_response.response
            self.assertEqual(str(len(csv_data)), response["Content-Length"])


class RenderTests(TestCase):

    def test_renders_an_http_response_by_default(self):
        with mock.patch("response_helpers.helpers.render_to_string"):
            response = helpers.render(None, mock.Mock())
            self.assertTrue(isinstance(response, helpers.HttpResponse))

    def test_renders_response_type_with_content_and_kwargs(self):
        with mock.patch("response_helpers.helpers.render_to_string") as render_to_string:
            kwargs = {"some": "kwargs"}
            response_type = mock.Mock()
            response = helpers.render(None, mock.Mock(), response_type=response_type, **kwargs)
            self.assertEqual(response_type.return_value, response)
            response_type.assert_called_once_with(render_to_string.return_value, **kwargs)

    @mock.patch("response_helpers.helpers.RequestContext")
    def test_gives_template_name_context_and_request_context_to_render_to_string(self, request_context):
        with mock.patch("response_helpers.helpers.render_to_string") as render_to_string:
            template_name = "my_template"
            context_data = mock.sentinel.context
            request = mock.Mock()

            helpers.render(template_name, request, context_data)
            render_to_string.assert_called_once_with(
                template_name, context_data, context_instance=request_context.return_value
            )
            request_context.assert_called_once_with(request)


class RenderToTests(TestCase):

    def test_render_to_wraps_function(self):

        @helpers.render_to("")
        def some_func():
            pass

        self.assertEqual("some_func", some_func.__name__)
