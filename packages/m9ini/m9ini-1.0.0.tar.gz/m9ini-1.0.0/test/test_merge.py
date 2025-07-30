import _test_case

from m9ini import uConfig, uConfigParameters, uConfigSection

class TestMerge(_test_case.uTestCase):

    def setUp(self):
        self.WriteSubHeader(self._testMethodName)
        self.config_ini = self.GetFilepath("test_config.ini")
        self.config = uConfig(self.config_ini)
        self.assertEqual(len(self.config.GetFailures(False)), 0)

    def test_merge_sections(self):
        config_ini = self.GetFilepath("test_merge.ini")
        config = uConfig(config_ini)
        section1 = config.GetSection("First")
        section2 = config.GetSection("Second")
        
        section = config.NewMergedSection("Merged", section1, section2)
        self.assertFailureCodes(config, ["[E11]"])
        self.assertTrue(isinstance(section, uConfigSection))
        self.assertEqual(section.GetName(), "Merged")
        self.assertEqual(config.GetSectionValue("Merged", "x"), "xxx")
        self.assertEqual(config.GetSectionValue("Merged", "y"), "two")
        self.assertEqual(config.GetSectionValue("Merged", "z"), "")
        self.assertEqual(config.GetSectionValue("Merged", "Test"), "black xxx")
        self.assertEqual(config.GetSectionValue("Merged", "More"), "ha")
        self.assertEqual(section.FormatString("[=Test]"), "black xxx")

        section = config.NewMergedSection("Merged2", section1, {'y':'red', 'z':'black', 'Test':'[=z] [=x]', 'More':'[=ho]'})
        self.assertTrue(isinstance(section, uConfigSection))
        self.assertEqual(section.GetName(), "Merged2")
        self.assertEqual(config.GetSectionValue("Merged2", "x"), "one")
        self.assertEqual(config.GetSectionValue("Merged2", "y"), "two")
        self.assertEqual(config.GetSectionValue("Merged2", "z"), "")
        self.assertEqual(config.GetSectionValue("Merged2", "Test"), "one")
        self.assertEqual(config.GetSectionValue("Merged2", "More"), "[=ho]")
        self.assertFailureCodes(config, ["[E11]"])
        self.assertEqual(section.FormatString("[=Test]"), "one")

        section = config.NewMergedSection("Merged3", section1, section2, Raw=True, Resolve=False)
        self.assertTrue(isinstance(section, uConfigSection))
        self.assertEqual(section.GetName(), "Merged3")
        self.assertEqual(config.GetSectionValue("Merged3", "x"), "one")
        self.assertEqual(config.GetSectionValue("Merged3", "y"), "two")
        self.assertEqual(config.GetSectionValue("Merged3", "z"), "")
        self.assertEqual(config.GetSectionValue("Merged3", "Test"), "one")
        self.assertEqual(config.GetSectionValue("Merged3", "More"), "[=ho]")
        self.assertFailureCodes(config, ["[E11]"])
        self.assertEqual(section.FormatString("[=Test]"), "one")

        self.assertEqual(config.FormatString("[=>Merged.Test]"), "black xxx")
        self.assertEqual(config.FormatString("[=>Merged2.Test]"), "one")
        self.assertEqual(config.FormatString("[=>Merged3.Test]"), "one")

        self.assertEqual(config.GetSectionValue("Third", "LinkTest"), "[=Other.Test]")
        self.assertFailureCodes(config, ["[E11]"])
        self.assertEqual(config.GetSectionValue("Third", "PropTest"), "[=NewProp]")
        self.assertFailureCodes(config, ["[E11]"])
        section = config.GetSection("Third")
        section.SetProperty("NewProp", "Silver")
        self.assertEqual(config.GetSectionValue("Third", "PropTest"), "Silver")
        merged1 = config.GetSection("Merged")
        section.SetLink("Other", merged1)
        self.assertEqual(config.GetSectionValue("Third", "LinkTest"), "black xxx")
        dprop = section.GetProperties()
        self.assertEqual(dprop['PropTest'], "Silver")
        self.assertEqual(dprop['NewProp'], "Silver")
        self.assertTrue(isinstance(dprop['Other'], uConfigSection))
        self.assertEqual(dprop['Other'].GetValue("z"), "")

        # test expansion order
        snames = [section.GetName() for section in config.sections][1:6]
        self.assertEqual(snames, ['First', 'Expand_First', 'Second', 'Expand_Second', 'Third'])