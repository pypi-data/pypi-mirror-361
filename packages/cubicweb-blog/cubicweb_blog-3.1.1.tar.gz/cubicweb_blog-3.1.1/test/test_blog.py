import unittest
from cubicweb_web.devtools.testlib import AutomaticWebTest


class AutomaticWebTest(AutomaticWebTest):
    def to_test_etypes(self):
        return {
            "Blog",
            "BlogEntry",
            "MicroBlog",
            "MicroBlogEntry",
        }


if __name__ == "__main__":
    unittest.main()
