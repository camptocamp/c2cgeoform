import pprint
from typing import Any, cast

import deform
import pyramid.response

from c2cgeoform import JSONDict, JSONList


class AbstractViewsTests:
    """
    Base class for views testing
    """

    _prefix = None  # url prefix (index view url). Example : /users

    def get(self, test_app: Any, path: str = "", locale: str = "en", status: int = 200, **kwargs: Any) -> Any:
        return test_app.get(
            f"{self._prefix}{path}",
            headers={"Cookie": f"_LOCALE_={locale}"},
            status=status,
            **kwargs,
        )

    def get_item(self, test_app: Any, item_id: str, **kwargs: Any) -> pyramid.response.Response:
        return self.get(test_app, f"/{item_id}", **kwargs)

    def check_left_menu(self, resp: pyramid.response.Response, title: str) -> None:
        link = resp.html.select_one(".navbar li.active a")
        assert f"http://localhost{self._prefix}" == link.attrs["href"]
        assert title == link.getText()

    def check_grid_headers(
        self, resp: pyramid.response.Response, expected_col_headers: JSONList, check_actions: bool = True
    ) -> None:
        pretty_printer = pprint.PrettyPrinter(indent=4)
        effective_cols = [
            (th.attrs["data-field"], th.getText(), th.attrs["data-sortable"]) for th in resp.html.select("th")
        ]
        expected_col_headers = [[x[0], x[1], len(x) == 3 and x[2] or "true"] for x in expected_col_headers]  # type: ignore[arg-type,index]
        assert expected_col_headers == effective_cols, str.format(  # type: ignore[comparison-overlap]
            "\n\n{}\n\n differs from \n\n{}",
            pretty_printer.pformat(expected_col_headers),
            pretty_printer.pformat(effective_cols),
        )
        if check_actions:
            actions = resp.html.select_one('th[data-field="actions"]')
            assert "false" == actions.attrs["data-sortable"]

    def check_new_button(self, resp: pyramid.response.Response) -> None:
        assert 1 == len(list(filter(lambda x: str(x.contents) == "['New']", resp.html.findAll("a"))))

    def check_search(
        self,
        test_app: Any,
        search: str = "",
        offset: int = 0,
        limit: int = 10,
        sort: str = "",
        order: str = "",
        total: Any = None,
        **kwargs: Any,
    ) -> Any:
        json = test_app.get(
            f"{self._prefix}/grid.json",
            params={
                "offset": offset,
                "limit": limit,
                "search": search,
                "sort": sort,
                "order": order,
                **kwargs,
            },
            status=200,
        ).json
        if total is not None:
            assert total == json["total"]
        return json

    def check_checkboxes(self, form: deform.Form, name: str, expected: list[JSONDict]) -> None:
        for i, exp in enumerate(expected):
            field = form.get(name, index=i)
            checkbox = form.html.select_one(f"#{field.id}")
            label = form.html.select_one(f"label[for={field.id}]")
            assert exp["label"] == list(label.stripped_strings)[0]
            assert exp["value"] == checkbox["value"]
            assert exp["checked"] == field.checked

    def get_first_field_named(self, form: deform.Form, name: str) -> Any:
        return form.fields.get(name)[0]

    def set_first_field_named(self, form: deform.Form, name: str, value: Any) -> None:
        form.fields.get(name)[0].value__set(value)

    def _check_sequence(self, sequence: Any, expected: Any) -> None:
        seq_items = sequence.select(".deform-seq-item")
        assert len(expected) == len(seq_items)
        for seq_item, exp in zip(seq_items, expected):
            self._check_mapping(seq_item, exp)

    def _check_mapping(self, mapping_item: Any, expected: list[JSONDict]) -> None:
        for exp in expected:
            input_tag = mapping_item.select_one('[name="{}"]'.format(exp["name"]))
            if "value" in exp:
                if exp.get("readonly", False):
                    item = mapping_item.select_one(".item-{}".format(exp["name"]))
                    assert input_tag is None
                    assert exp["value"] or "" == item.select("p").stripped_strings[0]
                elif input_tag.name == "select":
                    value = exp["value"]
                    assert isinstance(value, list)
                    self._check_select(input_tag, cast(list[JSONDict], value))
                elif input_tag.name == "textarea":
                    assert (exp["value"] or "") == (input_tag.string or "")
                else:
                    assert (exp["value"] or "") == input_tag.attrs.get("value", "")
            if exp.get("hidden", False):
                assert "hidden" == input_tag["type"]
            if "label" in exp:
                label_tag = mapping_item.select_one('label[for="{}"]'.format(input_tag["id"]))
                assert exp["label"] == label_tag.getText().strip()

    def _check_select(self, select: Any, expected: list[JSONDict]) -> None:
        for exp, option in zip(expected, select.find_all("option")):
            if "text" in exp:
                assert exp["text"] == option.text
            if "value" in exp:
                assert exp["value"] == option["value"]
            if "selected" in exp:
                assert exp["selected"] == ("selected" in option.attrs)

    def _check_submission_problem(self, resp: pyramid.response.Response, expected_msg: str) -> None:
        assert (
            "There was a problem with your submission"
            == resp.html.select_one('div[class="error-msg-lbl"]').text
        )
        assert (
            "Errors have been highlighted below" == resp.html.select_one('div[class="error-msg-detail"]').text
        )
        assert (
            expected_msg
            == resp.html.select_one("[class~='has-error']")
            .select_one("[class~='help-block']")
            .getText()
            .strip()
        )
