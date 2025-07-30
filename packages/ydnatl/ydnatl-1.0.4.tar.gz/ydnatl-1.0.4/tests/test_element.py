import unittest

from ydnatl.core.element import HTMLElement
from ydnatl.tags.layout import Div
from ydnatl.tags.text import Span, Paragraph


class TestHTMLElement(unittest.TestCase):

    def test_prepend(self):
        """Test the prepend() method."""
        element = HTMLElement(tag="div")
        div = HTMLElement(tag="div")
        element.prepend(div)
        self.assertEqual(len(element.children), 1)
        self.assertEqual(str(element.children[0]), "<div></div>")

    def test_append(self):
        """Test the append() method."""
        element = HTMLElement(tag="div")
        div = HTMLElement(tag="div")
        element.append(div)
        self.assertEqual(len(element.children), 1)
        self.assertEqual(str(element.children[0]), "<div></div>")

    def test_filter(self):
        """Test the filter() method."""
        element = HTMLElement(tag="div")
        span = Span("Child 1")
        p = Paragraph("Child 2")
        div = Div("Child 3")
        element.append(span, p, div)

        filtered = list(element.filter(lambda x: x.tag == "span"))
        self.assertEqual(len(filtered), 1)
        self.assertEqual(str(filtered[0]), "<span>Child 1</span>")

    def test_remove_all(self):
        """Test the remove_all() method."""
        element = HTMLElement(tag="div")
        child1 = HTMLElement(tag="span")
        child2 = HTMLElement(tag="p")
        child3 = HTMLElement(tag="div")
        element.append(child1, child2, child3)

        element.remove_all(lambda x: x.tag == "span")
        self.assertEqual(len(element.children), 2)
        self.assertEqual(str(element.children[0]), "<p></p>")
        self.assertEqual(str(element.children[1]), "<div></div>")

    def test_clear(self):
        """Test the clear() method."""
        element = HTMLElement(tag="div")
        element.append(HTMLElement(tag="span"), HTMLElement(tag="p"))
        element.clear()
        self.assertEqual(len(element.children), 0)

    def test_pop(self):
        """Test the pop() method."""
        element = HTMLElement(tag="div")
        child1 = HTMLElement(tag="span")
        child2 = HTMLElement(tag="p")
        element.append(child1, child2)

        popped = element.pop(0)
        self.assertEqual(str(popped), "<span></span>")
        self.assertEqual(len(element.children), 1)
        self.assertEqual(str(element.children[0]), "<p></p>")

    def test_first_last(self):
        """Test the first() and last() methods."""
        element = HTMLElement(tag="div")
        child1 = HTMLElement(tag="span")
        child2 = HTMLElement(tag="p")
        element.append(child1, child2)

        self.assertEqual(str(element.first()), "<span></span>")
        self.assertEqual(str(element.last()), "<p></p>")

    def test_add_remove_attribute(self):
        """Test the add_attribute() and remove_attribute() methods."""
        element = HTMLElement(tag="div")
        element.add_attribute("id", "my-div")
        self.assertEqual(element.attributes, {"id": "my-div"})

        element.remove_attribute("id")
        self.assertEqual(element.attributes, {})

    def test_get_has_attribute(self):
        """Test the get_attribute() and has_attribute() methods."""
        element = HTMLElement(tag="div", id="my-div", class_name="container")
        self.assertEqual(element.get_attribute("id"), "my-div")
        self.assertEqual(element.get_attribute("class_name"), "container")
        self.assertTrue(element.has_attribute("id"))
        self.assertFalse(element.has_attribute("style"))

    def test_generate_id(self):
        """Test the generate_id() method."""
        element = HTMLElement(tag="div")
        element.generate_id()
        self.assertTrue(element.has_attribute("id"))
        self.assertTrue(element.get_attribute("id").startswith("el-"))

    def test_clone(self):
        """Test the clone() method."""
        element = HTMLElement(tag="div", id="my-div", text="Hello")
        child = HTMLElement(tag="span")
        element.append(child)

        cloned = element.clone()
        self.assertEqual(str(cloned), str(element))
        self.assertIsNot(cloned, element)
        self.assertIsNot(cloned.children[0], child)

    def test_find_by_attribute(self):
        """Test the find_by_attribute() method."""
        element = HTMLElement(tag="div")
        child1 = HTMLElement(tag="span", id="child1")
        child2 = HTMLElement(tag="p", id="child2")
        child3 = HTMLElement(tag="div", id="child3")
        element.append(child1, child2, child3)

        found = element.find_by_attribute("id", "child2")
        self.assertEqual(str(found), '<p id="child2"></p>')

        nested_child = HTMLElement(tag="span", id="nested")
        child3.append(nested_child)
        found_nested = element.find_by_attribute("id", "nested")
        self.assertEqual(str(found_nested), '<span id="nested"></span>')

    def test_get_attributes(self):
        """Test the get_attributes() method."""
        element = HTMLElement(
            tag="div", id="my-div", class_name="container", style="color: red"
        )
        self.assertEqual(
            element.get_attributes("id", "class_name"),
            {"id": "my-div", "class_name": "container"},
        )
        self.assertEqual(
            element.get_attributes(),
            {"id": "my-div", "class_name": "container", "style": "color: red"},
        )

    def test_count_children(self):
        """Test the count_children method."""
        element = HTMLElement(tag="div")
        element.append(HTMLElement(tag="span"), HTMLElement(tag="p"))
        self.assertEqual(element.count_children(), 2)

    def test_replace_child(self):
        """Test the replace_child() method."""
        element = HTMLElement(tag="div")
        element.append(HTMLElement(tag="span"), HTMLElement(tag="p"))
        self.assertEqual(element.count_children(), 2)
        self.assertEqual(str(element.children[0]), "<span></span>")
        self.assertEqual(str(element.children[1]), "<p></p>")
        element.replace_child(0, HTMLElement(tag="h1"))
        self.assertEqual(element.count_children(), 2)
        self.assertEqual(str(element.children[0]), "<h1></h1>")

    def test_callbacks(self):
        """Test the callback methods."""

        class TestElement(HTMLElement):
            def on_load(self):
                self.loaded = True

            def on_before_render(self):
                self.before_render_called = True

            def on_after_render(self):
                self.after_render_called = True

        element = TestElement(tag="div")
        self.assertTrue(hasattr(element, "loaded"))
        self.assertTrue(element.loaded)

        element.render()
        self.assertTrue(hasattr(element, "before_render_called"))
        self.assertTrue(element.before_render_called)

        self.assertTrue(hasattr(element, "after_render_called"))
        self.assertTrue(element.after_render_called)

    def test_add_attributes(self):
        """Test the add_attributes method."""
        element = HTMLElement(tag="div")
        element.add_attributes([("id", "my-div"), ("class", "container")])
        self.assertEqual(element.attributes, {"id": "my-div", "class": "container"})

        # Test overwriting existing attributes
        element.add_attributes([("id", "new-id"), ("style", "color: red")])
        self.assertEqual(
            element.attributes,
            {"id": "new-id", "class": "container", "style": "color: red"},
        )

    def test_to_dict(self):
        el1 = HTMLElement(tag="span", text="Child 1")
        el1.append(HTMLElement(tag="span", text="Child 2"))
        should_be = {
            "tag": "span",
            "self_closing": False,
            "attributes": {"text": "Child 1"},
            "text": "",
            "children": [
                {
                    "tag": "span",
                    "self_closing": False,
                    "attributes": {"text": "Child 2"},
                    "text": "",
                    "children": [],
                }
            ],
        }
        self.assertIsNotNone(el1.to_dict())
        self.assertIsInstance(el1.to_dict(), dict)
        self.assertEqual(el1.to_dict(), should_be)


if __name__ == "__main__":
    unittest.main()
