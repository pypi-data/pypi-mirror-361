import _test_case

from m9ini import uConfig, uConfigParameters, uConfigSection

class TestExpansion(_test_case.uTestCase):

    def setUp(self):
        self.WriteSubHeader(self._testMethodName)
        self.config_ini = self.GetFilepath("test_config.ini")
        self.config = uConfig(self.config_ini)
        self.assertEqual(len(self.config.GetFailures(False)), 0)
        
    def test_expansion(self):
        config_ini = self.GetFilepath("test_expand.ini")
        config = uConfig(config_ini)
        self.assertFailureCodes(config, ["[E14]", "[E14]", "[F10]"])
        self.assertEqual(config.CountSections("Expansion"), 12)
        self.assertEqual(config.CountSections(":tooth"), 4)
        self.assertEqual(config.CountSections(":nail"), 4)
        self.assertEqual(config.CountSections(":tail"), 4)
        self.assertEqual(config.CountSections("Span_One"), 1)
        self.assertEqual(config.CountSections("Span_Two"), 1)
        self.assertEqual(config.GetSectionValue("Expansion:tooth", "Orange"), "orange")
        self.assertEqual(config.GetSectionValue("Span_One:SpanId", "Description"), "orange cat red bird")
        self.assertEqual(config.GetSectionValue("Span_One:SpanId", "base"), "[Animal:tabby]")
        self.assertEqual(config.GetSectionLink("Span_One:SpanId", "base").GetSpecification(), "Animal:tabby")
        self.assertEqual(config.CountSections("Block"), 4)
        self.assertEqual(config.CountSections(":pink_block"), 1)
        self.assertEqual(config.GetSectionValue("Block:pink_block", "Description"), "a pink stone block")
        self.assertEqual(config.CountSections("Kitten"), 4)
        self.assertEqual(config.CountSections(":Fuzzy_kitten"), 1)
        self.assertEqual(config.GetSectionValue("Kitten:Fuzzy_kitten", "Description"), "a small Fuzzy kitten")
        self.assertEqual(config.GetSectionValue("Kitten:Fuzzy_kitten", "SourceReference"), "Fuzzy")
        self.assertEqual(config.GetSectionValue("Kitten:Fuzzy_kitten", "BaseTest1"), "Red")
        self.assertEqual(config.GetSectionValue("Kitten:Fuzzy_kitten", "BaseTest2"), "Pink")

        self.assertEqual(config.GetSectionValue("Kitten:Fuzzy_kitten", "BaseTest3"), "Blue")
        print ('KNOWN ISSUE: Issues [E11] for a backwards reference')
        config.GetFailures() # clear known issue

        self.assertEqual(config.CountSections("NoBaseNoVector"), 1)
        self.assertEqual(config.CountSections("NoBase"), 6)
        self.assertEqual(config.CountSections("NoBase:strawberry_smoothie"), 1)
        self.assertEqual(config.CountSections("ListBase"), 4)
        self.assertEqual(config.CountSections("ListBase:Fire"), 1)
        self.assertEqual(config.CountSections("ListBaseInternal"), 3)
        self.assertEqual(config.CountSections("ListBaseInternal:Sweet"), 1)

        self.assertEqual(config.CountSections("NumericalExpansion:step"), 10)
        smax = -999
        smin = 999
        sections = config.GetSections("NumericalExpansion:step")
        for section in sections:
            num = section.GetFloat("Number")
            smax = max(smax, num)
            smin = min(smin, num)
        self.assertEqual(int(smin), 0)
        self.assertEqual(int(smax+.01), 1)

        self.assertEqual(config.CountSections("NumericalExpansion:plus"), 10)
        smax = -999
        smin = 999
        sections = config.GetSections("NumericalExpansion:plus")
        for section in sections:
            num = section.GetFloat("Number")
            smax = max(smax, num)
            smin = min(smin, num)
        self.assertEqual(int(smin), 0)
        self.assertEqual(int(smax+.01), 1)

        self.assertEqual(config.GetSectionValue("FieldTest", "Field1"), "333")
        self.assertEqual(config.GetSectionValue("FieldTest", "Field2"), "333")
        self.assertEqual(config.GetSectionValue("FieldTest", "Field3"), "555")
        self.assertEqual(config.GetSectionValue("FieldTest", "Field4"), "666")
        self.assertEqual(config.GetSectionValue("FieldTest", "SomeField"), "333")
        self.assertEqual(config.GetSectionValue("FieldTest", "SecondField"), "555")
        self.assertEqual(config.GetSection("FieldTest").GetId(), "parent_base_id")
        self.assertEqual(config.GetSectionValue("FieldTest", "*id"), "parent_base_id")
        self.assertEqual(config.GetSection("FieldTest").FormatString("[=*id]"), "parent_base_id")
        self.assertEqual(config.GetSection("FieldTest").FormatString("[=base.*id]"), "base_id")

        # no base reference scenarios
        # sv = config.GetSectionValue("NoBaseNoVector", "Fruit")
        # sv = config.GetSectionValue("NoBaseBaseReference", "Fruit")

        # not found scenarios
        self.assertEqual(config.GetSection("FieldTest").FormatString("[=not.found]"), "[=not.found]")
        self.assertFailureCodes(config, ["[E11]"])
        self.assertEqual(config.GetSection("FieldTest").FormatString("[=not.found]",Empty=True), "")
        self.assertFailureCodes(config, ["[E11]"])
        self.assertEqual(config.GetSection("FieldTest").FormatString("[=not.found] [=Field1]",Empty=True), "333")
        self.assertFailureCodes(config, ["[E11]"])
        self.assertEqual(config.GetSection("FieldTest").FormatString("[=>not.found]",Empty=True), "")
        self.assertFailureCodes(config, ["[E10]"])
        self.assertEqual(config.GetSection("FieldTest").FormatString("[=>not.found] [=Field1]",Empty=True), "333")
        self.assertFailureCodes(config, ["[E10]"])
        self.assertEqual(config.GetSection("FieldTest").FormatString("[=:::bad.syntax]",Empty=True), "")
        self.assertFailureCodes(config, ["[E04]"])
        self.assertEqual(config.GetSection("FieldTest").FormatString("[=>:::bad.syntax]",Empty=True), "")
        self.assertFailureCodes(config, ["[E05]"])

        section = config.GetSection("FieldTest")
        prop = section.GetProperties()
        self.assertTrue(section.HasValue("SomeField"))
        self.assertTrue("SomeField" in prop)
        self.assertEqual(prop["Field1"], "333")
        self.assertEqual(prop["Field2"], "333")
        self.assertEqual(prop["Field3"], "555")
        self.assertEqual(prop["Field4"], "666")
        self.assertEqual(prop["SomeField"], "333")
        self.assertEqual(prop["SecondField"], "555")
        self.assertEqual(prop["Field1"], "333")
        self.assertEqual(prop["Field1"], "333")

        config.WriteConfigLines(r"test\output\{YMD}-{TSM} TestExpansion-Re.ini")
