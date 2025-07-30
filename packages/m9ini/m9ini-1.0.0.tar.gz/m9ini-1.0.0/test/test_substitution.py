import _test_case

from m9ini import uConfig, uConfigParameters, uConfigSection

class TestExpansion(_test_case.uTestCase):

    def setUp(self):
        self.WriteSubHeader(self._testMethodName)
        self.config_ini = self.GetFilepath("test_config.ini")
        self.config = uConfig(self.config_ini)
        self.assertEqual(len(self.config.GetFailures(False)), 0)
        self.assertEqual(uConfigSection._section_lock.counter, 0)
        
    def test_substitution(self):
        config_ini = self.GetFilepath("test_subst.ini")
        config = uConfig(config_ini)
        self.assertFalse(config.HasFailures())

        # simple substitution
        # [4.1] `[={property}]` Simple replacement using a local property
        self.assertEqual(config.GetSectionValue(":simple1", "Color"), "Red")
        # [5.1] `[=>{section}:{id}.{name}]` Simple replacement of a remote property
        self.assertEqual(config.GetSectionValue(":simple2", "Try1"), "Red")
        # [5.3] `[=>:{id}.{name}]` Simple replacement of a remote property (id only)
        # [4.3] References cannot be embedded, but can chain
        self.assertEqual(config.GetSectionValue(":simple2", "Try2"), "Red")

        # [5.1] `[=>{section}:{id}.{name}]` Simple replacement of a remote property
        # [5.11] Section name redirect to a local property
        # [4.3] References cannot be embedded, but can chain
        self.assertEqual(config.GetSectionValue(":simple2", "Try3"), "Red")
        # [5.3] `[=>:{id}.{name}]` Simple replacement of a remote property (id only)
        # [5.11] Section name redirect to a local property
        # [4.3] References cannot be embedded, but can chain
        self.assertEqual(config.GetSectionValue(":simple2", "Try4"), "Red")
        # [5.1] `[=>{section}:{id}.{name}]` Simple replacement of a remote property
        # [5.12] Section id redirect to a local property
        # [4.3] References cannot be embedded, but can chain
        self.assertEqual(config.GetSectionValue(":simple2", "Try5"), "Red")
        # [5.3] `[=>:{id}.{name}]` Simple replacement of a remote property (id only)
        # [5.12] Section id redirect to a local property
        # [4.3] References cannot be embedded, but can chain
        self.assertEqual(config.GetSectionValue(":simple2", "Try6"), "Red")
        # [5.3] `[=>:{id}.{name}]` Simple replacement of a remote property (id only)
        # [5.13] Property name redirect to a local property
        # Property is a property name to a property section
        self.assertEqual(config.GetSectionValue(":simple2", "Try7"), "Pink")
        # [5.3] `[=>:{id}.{name}]` Simple replacement of a remote property (id only)
        # [5.13] Property name redirect to a local property
        # Property is an index intoto a text block
        self.assertEqual(config.GetSectionValue(":simple2", "Try8"), "Pink")

        # clear failures
        config.GetFailures()
        # bad section
        self.assertEqual(config.GetSectionValue(":simple2", "Try11"), "[=>$BadSection:$SimpleId.Color]")
        self.assertFailureCodes(config, ["[E13]", "[E10]"])
        # bad id
        self.assertEqual(config.GetSectionValue(":simple2", "Try12"), "[=>$SimpleSection:$BadSection.Color]")
        self.assertFailureCodes(config, ["[E13]", "[E10]"])
        # bad option
        self.assertEqual(config.GetSectionValue(":simple2", "Try13"), "[=>:select2.$BadOption]")
        self.assertFailureCodes(config, ["[E13]"])
        # section not found - this is the old [5.9]
        self.assertEqual(config.GetSectionValue(":simple2", "Try28"), "[=>SimpleSubstitution:SimpleId.Color]")
        self.assertFailureCodes(config, ["[E10]"])
        # section not found - this is the old [5.9]
        self.assertEqual(config.GetSectionValue(":simple2", "Try29"), "[=>:SimpleId.Color]")
        self.assertFailureCodes(config, ["[E10]"])

        # simple random selection
        # [4.2] `[={property}.?]` Random list element of a local property
        colors="Red,Pink,Purple,Black,Violet,Crimson,Silver,Gold".split(',')
        self.assertTrue(config.GetSectionValue(":select1", "Random1") in colors)
        # [5.5] `[=>{section}:{id}.?]` Random property of a remote section
        self.assertTrue(config.GetSectionValue(":select1", "Random2") in colors)
        # [5.7] `[=>{section}:{id}.?]` Random line of a remote text block
        self.assertTrue(config.GetSectionValue(":select1", "Random3") in colors)
        # [5.4] `[=>:{id}.{name}.?]` Random list element of a remote property (id only)
        self.assertTrue(config.GetSectionValue(":select1", "Random4") in colors)
        # [5.5] `[=>:{id}.{name}.?]` Random list element of a remote property (id only)
        # [4.3] References cannot be embedded, but can chain
        self.assertTrue(config.GetSectionValue(":select1", "Random5") in colors)
        # [5.6] `[=>{section}:{id}.?.?]` Random list element of a random property in a section
        self.assertTrue(config.GetSectionValue(":select1", "Random6") in ['Red', 'Purple', 'Pink', 'Blue', 'Green', 'Yellow'])
        # [5.8] `[=>{section}:{id}.?.?]` Random list element of a random line in a text block
        self.assertTrue(config.GetSectionValue(":select1", "Random7") in ['Red', 'Purple', 'Pink', 'Blue', 'Green', 'Yellow'])

        # link reference
        # [6.1] `{property}=>{section}` Link to a remote section
        self.assertEqual(config.GetSectionValue("LinkTest", "Animal1"), "[Animal:tabby]")
        section = config.GetSectionLink("LinkTest", "Animal1")
        self.assertTrue(isinstance(section, uConfigSection))
        if section is not None:
            self.assertEqual(section.GetSpecification(), "Animal:tabby")
        # [6.2] `{property}=>{section}:{id}` Link to a remote section (with id)
        self.assertEqual(config.GetSectionValue("LinkTest", "Animal2"), "[Animal:tabby]")
        section = config.GetSectionLink("LinkTest", "Animal2")
        self.assertTrue(isinstance(section, uConfigSection))
        if section is not None:
            self.assertEqual(section.GetSpecification(), "Animal:tabby")
        # [6.3] `{property}=>:{id}` Link to a remote section (id only)
        self.assertEqual(config.GetSectionValue("LinkTest", "Animal3"), "[Animal:tabby]")
        section = config.GetSectionLink("LinkTest", "Animal3")
        self.assertTrue(isinstance(section, uConfigSection))
        if section is not None:
            self.assertEqual(section.GetSpecification(), "Animal:tabby")

        # [6.12] `{property}=>{section}:${property}` Section id redirect to a local property
        # [6.13] `{property}=>:${property}` Section id redirect to a local property (id only)
        self.assertEqual(config.GetSectionValue("LinkTest", "Animal6a"), "[Animal:tabby]")
        self.assertEqual(config.GetSectionValue("LinkTest", "Animal6b"), "[Animal:tabby]")
        # [6.11] `{property}=>${property}` Section name redirect to a local property
        self.assertEqual(config.GetSectionValue("LinkTest", "Animal6d"), "[Animal:tabby]")
        self.assertEqual(config.GetSectionValue("SubstTest:subst_id", "AnimalColor"), "orange")

        # section link failures
        config.GetFailures()
        # DELETE [6.4] `{property}=>{id}` Link to a remote section (id only)
        self.assertEqual(config.GetSectionValue("LinkTest", "Animal6c"), None)
        self.assertFailureCodes(config, ["[E01]"])
        self.assertEqual(config.GetSectionValue("LinkTest", "Animal4"), None)
        self.assertFailureCodes(config, ["[E01]"])
        self.assertEqual(config.GetSectionLink("LinkTest", "Animal4"), None)
        self.assertFailureCodes(config, ["[E01]"])
        # DELETE [6.5] `{section}=>{id}` Link to a remote section (property name is section name)
        self.assertEqual(config.GetSectionValue("LinkTest", "Animal4"), None)
        self.assertFailureCodes(config, ["[E01]"])

        self.assertEqual(config.GetSectionValue("LinkTest", "Animal"), "[Animal:tabby]")
        section = config.GetSectionLink("LinkTest", "Animal")
        self.assertTrue(isinstance(section, uConfigSection))
        if section is not None:
            self.assertEqual(section.GetSpecification(), "Animal:tabby")


        self.assertEqual(config.GetSectionValue("LinkTest", "xAnimal6a"), None)
        self.assertFailureCodes(config, ["[E13]", "[E01]"])
        self.assertEqual(config.GetSectionValue("LinkTest", "xAnimal6b"), None)
        self.assertFailureCodes(config, ["[E13]", "[E01]"])
        self.assertEqual(config.GetSectionValue("LinkTest", "xAnimal6c"), None)
        self.assertFailureCodes(config, ["[E13]", "[E01]"])

        # Linked values
        self.assertEqual(config.GetSectionValue("LinkTest", "AnimalTest1"), "[Animal:tabby]")
        self.assertEqual(config.GetSectionValue("LinkTest", "AnimalTest2"), "orange")

        # [6.7] Where `{section}` or `{id}` contain replacements
        self.assertEqual(config.GetSectionValue("LinkTest", "Animal7a"), "[Animal:tabby]")
        self.assertEqual(config.GetSectionValue("LinkTest", "Animal7b"), "[Animal:tabby]")
        section = config.GetSectionLink("LinkTest", "Animal7a")
        self.assertTrue(isinstance(section, uConfigSection))
        if section is not None:
            self.assertEqual(section.GetSpecification(), "Animal:tabby")
        section = config.GetSectionLink("LinkTest", "Animal7b")
        self.assertTrue(isinstance(section, uConfigSection))
        if section is not None:
            self.assertEqual(section.GetSpecification(), "Animal:tabby")

        # link chain
        self.assertEqual(config.GetSectionValue("LinkTest", "TestLink"), "Toast")
        self.assertEqual(config.GetSectionValue("LinkTest", "TestLinks1"), "Toast")
        self.assertEqual(config.GetSectionValue("LinkTest", "TestLinks2"), "Toast")

        # link chain failures
        config.GetFailures()
        self.assertEqual(config.GetSectionValue("LinkTest", "xTestLink1"), "[=xChainLink.Value2]")
        self.assertFailureCodes(config, ["[E11]"])
        self.assertEqual(config.GetSectionValue("LinkTest", "xTestLink2"), "[=xChainLink1.Value2]")
        self.assertFailureCodes(config, ["[E01]"])

        # recursive link chain
        self.assertEqual(config.GetSectionValue("LinkTest", "Recurse1"), "[=>:chain2.Recurse2]")
        self.assertFailureCodes(config, ["[E19]"])

        # failure scenarios
        config.GetFailures()
        self.assertFalse(config.HasFailures())
        ret = config.GetSectionValue(":simple1", "Fail")
        self.assertEqual(len(config.GetFailures()), 1)
        ret = config.GetSectionValue(":simple2", "Fail1")
        self.assertEqual(len(config.GetFailures()), 1)
        ret = config.GetSectionValue(":simple2", "Fail2")
        self.assertEqual(len(config.GetFailures()), 1)
        ret = config.GetSectionValue(":simple1", "Recurse")
        self.assertEqual(len(config.GetFailures()), 1)
        ret = config.GetSectionValue(":select1", "Fail1")
        self.assertEqual(len(config.GetFailures()), 1)
        ret = config.GetSectionValue(":select1", "Fail2")
        self.assertEqual(len(config.GetFailures()), 1)

        section = config.GetSectionById("simple2")
        prop1 = section.GetProperties(Resolve=False)
        prop2 = section.GetProperties(Resolve=True)
        self.assertEqual(prop1['*id'], prop2['*id']) 
        self.assertEqual(prop1['*class'], prop2['*class']) 
        self.assertEqual(prop1['*name'], prop2['*name']) 
        self.assertEqual(prop1['SimpleId'], prop2['SimpleId']) 
        self.assertEqual(prop1['Try2'], '[=>:simple1.Color]') 
        self.assertEqual(prop2['Try2'], 'Red') 
        self.assertEqual(prop1['Fail2'], '[=>:Nope.Nope]') 
        self.assertEqual(prop2['Fail2'], '[=>:Nope.Nope]') 
        self.assertEqual(prop2['BadLink'], None)
        self.assertEqual(prop1['SimpleLink'], '>SimpleSelection:select1') 
        self.assertTrue(isinstance(prop2['SimpleLink'], uConfigSection))

        # animal tests
        self.assertTrue('[' in config.GetSectionValue("LinkTest", "Animal1"))
        self.assertFalse('[' in config.GetSectionValue(":subst_id", "AnimalColor"))
        self.assertFalse('[' in config.GetSectionValue(":subst_id", "AnimalDesc"))
        self.assertFalse('[' in config.GetSectionValue(":tabby", "Description"))

        # bird test
        self.assertFalse('[' in config.GetSectionValue(":bird_0", "Color"))
        self.assertFalse('[' in config.GetSectionValue(":bird_0", "Description"))
        self.assertFalse('[' in config.GetSectionValue(":bird_s1", "Color"))
        self.assertFalse('[' in config.GetSectionValue(":bird_s1", "Description"))
        self.assertFalse('[' in config.GetSectionValue(":bird_s2", "Color"))
        self.assertFalse('[' in config.GetSectionValue(":bird_s2", "Description"))
        self.assertFalse('[' in config.GetSectionValue(":bird_s3", "Color"))
        self.assertFalse('[' in config.GetSectionValue(":bird_s3", "Description"))
        self.assertFalse('[' in config.GetSectionValue(":bird_s4", "Color"))
        self.assertFalse('[' in config.GetSectionValue(":bird_s4", "Description"))
        self.assertFalse('[' in config.GetSectionValue(":bird_s5", "Color"))
        self.assertFalse('[' in config.GetSectionValue(":bird_s5", "Description"))
        self.assertFalse('[' in config.GetSectionValue(":bird_b1", "Color"))
        self.assertFalse('[' in config.GetSectionValue(":bird_b1", "Description"))
        self.assertFalse('[' in config.GetSectionValue(":bird_b2", "Color"))
        self.assertFalse('[' in config.GetSectionValue(":bird_b2", "Description"))
        self.assertFalse('[' in config.GetSectionValue(":bird_b3", "Color"))
        self.assertFalse('[' in config.GetSectionValue(":bird_b3", "Description"))
        self.assertFalse('[' in config.GetSectionValue(":bird_b4", "Color"))
        self.assertFalse('[' in config.GetSectionValue(":bird_b4", "Description"))
        self.assertFalse('[' in config.GetSectionValue(":bird_b5", "Color"))
        self.assertFalse('[' in config.GetSectionValue(":bird_b5", "Description"))

        section = config.GetSection("test_lines")
        lines = section.BuildConfigLines()  # Raw=False
        self.assertEqual(lines, ['[test_lines::l1,label,l3]', '*class=two', 'Source=Pink', 'New=Two', 'Color=Pink'])
        lines = section.BuildConfigLines(Raw=True)
        self.assertEqual(lines, ['[test_lines::l1,label,l3]', '*class=two', 'Source=Red', 'Color=Red'])

        lines = config.BuildConfigLines(Resolve=False)
        lines = config.BuildConfigLines()
        # print(f">> {lines}")
       
        c1=config.GetSectionValue(":select1", "Random1")
        c2=config.GetSectionValue(":select1", "Random1")
        c3=config.GetSectionValue(":select1", "Random1")
        self.assertTrue(c1==c2 and c2==c3)

        # SOURCE REFERENCE IN LINKS
        self.assertEqual(config.GetSectionValue("SourceTest_Source", "Test1"), "red roses")
        self.assertEqual(config.GetSectionValue("SourceTest_Source", "Test2"), "red roses")

        # PROPERTY LINK INDIRECTION - ID
        sections = config.GetSections("pliMySection")
        self.assertEqual(len(config.GetSections("pliMySection")), 2)
        self.assertEqual(config.GetSectionValue("pliMySection:base_1", "color_id"), 'id_1')
        self.assertEqual(config.GetSectionValue("pliMySection:base_1", "Example"), 'red')
        self.assertEqual(config.GetSectionValue("pliMySection:base_2", "Example"), 'blue')
        sv = config.GetSectionValue("pliMySection:base_1", "Example")

        # PROPERTY LINK INDIRECTION - PROPERTY
        config = uConfig(config_ini)
        sv = config.GetSectionValue("ppiMySection", "Example")
