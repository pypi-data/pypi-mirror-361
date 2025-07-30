from django import test
from django.views.generic import View
from io import StringIO

from response_helpers import views


class SampleCSVResponse(views.CSVResponseView):
    field_names = ["first_field", "second_field"]

    def get_data(self):
        return [
            {
                "first_field": "one",
                "second_field": "two",
            },
            {
                "first_field": "second_one",
                "second_field": "second_two",
            },
        ]


class SampleCustomCSVResponse(views.CSVResponseView):
    field_names = ["fox", "cat", "bat", "goat", "snake"]

    def get_data(self):
        return [
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
        return dict(zip(field_names, [_.upper() for _ in field_names]))


class CSVResponseViewTests(test.TestCase):

    def setUp(self):
        self.test_object = views.CSVResponseView()

    def test_subclasses_generic_view(self):
        self.assertTrue(issubclass(views.CSVResponseView, View))

    def test_get_filename_uses_filename_from_class_when_present(self):
        file_name = "MyFile"
        self.test_object.file_name = file_name
        self.assertEqual(file_name, self.test_object.get_file_name())

    def test_get_filename_removes_extension_when_csv(self):
        self.test_object.file_name = "foo.csv"
        self.assertEqual("foo", self.test_object.get_file_name())

        self.test_object.file_name = "foo.bax"
        self.assertEqual("foo.bax", self.test_object.get_file_name())

        # only remove '.csv' if file extention
        self.test_object.file_name = "save.as.csv.for.file.name"
        self.assertEqual("save.as.csv.for.file.name", self.test_object.get_file_name())

    def test_get_filename_uses_default_filename_when_not_explicitly_set(self):
        self.assertEqual("csv_download", self.test_object.get_file_name())

    def test_get_field_names_returns_field_names_when_defined(self):
        field_names = ["one", "two"]
        self.test_object.field_names = field_names
        self.assertEqual(field_names, self.test_object.get_field_names())

    def test_get_header_row_returns_dict_of_field_names(self):
        field_names = ["one", "two"]
        self.test_object.field_names = field_names
        header_row = self.test_object.get_header_row()
        self.assertEqual(
            {
                "one": "one",
                "two": "two",
            },
            header_row,
        )

    def test_custom_get_header_row_returns_custom_dict(self):
        test_object = SampleCustomCSVResponse()
        header_row = test_object.get_header_row()
        expected_header = {
            "cat": "CAT",
            "bat": "BAT",
            "goat": "GOAT",
        }
        self.assertEqual(expected_header, header_row)

    def test_custom_methods_return_csv_of_data_as_content(self):
        request = test.RequestFactory().get("/")
        test_object = SampleCustomCSVResponse()
        response = test_object.get(request)

        s = StringIO()
        for i in response.streaming_content:
            s.write(i.decode("utf-8"))

        # column order set by get_field_names()
        expected_rows = [
            "BAT,CAT,GOAT",
            "bat_1,cat_1,goat_1",
            "bat_2,cat_2,goat_2",
            "",
        ]
        self.assertEqual("\r\n".join(expected_rows), s.getvalue())

    def test_get_method_returns_csv_of_data_as_content(self):
        request = test.RequestFactory().get("/")
        test_object = SampleCSVResponse()
        response = test_object.get(request)

        s = StringIO()
        for i in response.streaming_content:
            s.write(i.decode("utf-8"))

        self.assertEqual("first_field,second_field\r\none,two\r\nsecond_one,second_two\r\n", s.getvalue())
