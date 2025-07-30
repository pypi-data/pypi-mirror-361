import _test_case

from m9ini import uConfig, uConfigParameters, uConfigSection

import os

class TestConfig(_test_case.uTestCase):

    def setUp(self):
        self.WriteSubHeader(self._testMethodName)
        self.config_ini = self.GetFilepath("test_config.ini")
        self.config = uConfig(self.config_ini)
        self.assertEqual(len(self.config.GetFailures(False)), 0)

    def test_config_structure(self):
        # by default, GetValue () accesses root level
        self.assertEqual(self.config.GetValue('empty'), "")
        self.assertEqual(self.config.GetValue('not-found'), None)
        self.assertEqual(self.config.GetValue('foo'), '9')
        # test that a number is converting properly
        self.assertEqual(self.config.GetNumber('foo'), 9)
        # test that a number does not convert properly
        self.assertEqual(self.config.GetSectionNumber('lala_99', 'foo'), False)
        # test that a value was not found
        self.assertEqual(self.config.GetSectionNumber('lala_99', 'badfoo'), None)
        # section name can be specified
        self.assertEqual(self.config.GetSectionNumber('section_c', 'foo'), 6)
        # values will be trimmed of spaced before
        self.assertEqual(self.config.GetSectionValue('section_a', 'value_1'),self.config.GetSectionValue('section_a', 'value_2'))
        # there is list support
        self.assertEqual(len (self.config.GetSectionList('section_a', 'list_1')),6)
        self.assertEqual(self.config.GetSectionList('section_a', 'list_1') [5],'13')
        # there is multiple section support
        self.assertEqual(self.config.CountSections('section_b'),3)
        self.assertEqual(self.config.GetSectionByIndex('section_b', 1).GetValue('foo'),'Y')
        # there is id support -- on the section header and the id value
        self.assertEqual(self.config.GetSectionById('b99').GetValue('foo'),'Y')
        self.assertEqual(self.config.GetSectionById('b99').GetClass(),'section_b')
        self.assertEqual(self.config.GetSection(Name='section_b', Id='b99').GetValue('foo'),'Y')
        self.assertEqual(self.config.GetSection(Name='section_c', Id='c99').GetValue('foo'),'6')
        # test some types
        self.assertTrue(isinstance (self.config.GetSection('section_b'),uConfigSection))
        self.assertEqual(self.config.GetSection(Name='section_b', Id='not found'), None)
        # labels
        self.assertEqual(self.config.GetSection(Label='funny').GetValue('foo'),'6')
        self.assertEqual(self.config.GetSection(Label='funny').GetClass (),'class_c')
        # start with
        self.assertEqual(self.config.GetSection(Name='$lala').GetValue('foo'),'b99')
        self.assertEqual(self.config.GetSection(Id='$xor').GetValue('foo'),'b99')
        self.assertEqual(self.config.GetSection(Label='$zsome').GetValue('foo'),'b99')
        # Test starts with ($)
        self.assertEqual(self.config.GetSection(Label='$fun').GetClass (),'class_c')
        self.assertEqual(self.config.GetSection('mysection_blue').GetValue('def2'),'y_default')
        # multiple entries converts to a list
        l = self.config.GetSection('mysection_blue').GetList('list')
        self.assertEqual(len(l),5)
        self.assertEqual(l[2],"third")
        # default values
        self.assertEqual(self.config.GetNumber('not found'), None)
        self.assertEqual(self.config.GetNumber('not found', 999), 999)
        # text blocks
        self.assertFalse(self.config.GetSection(Name="lala_99").IsTextBlock())
        self.assertEqual(self.config.GetSection(Name="lala_99").GetTextBlock(), None)
        block_section = self.config.GetSectionById("block_id")
        self.assertTrue(block_section.IsTextBlock())
        text_block = block_section.GetTextBlock()
        self.assertFalse(text_block is None)
        self.assertEqual(len(text_block), 3)
        # text block index access
        self.assertEqual(self.config.GetSectionValue(":b99", "block_access"), "this is funny")

    def test_config_blank(self):
        config_ini = self.GetFilepath("test_blank.ini")
        config = uConfig(config_ini)
        section = config.GetSection("Blank")
        self.assertEqual(section.HasValue("two"), True)
        self.assertEqual(section.GetValue("two"), "")
        section = config.GetSection("Blank2")
        self.assertEqual(section.HasValue("two"), True)
        self.assertEqual(section.GetValue("two"), "")
        self.assertEqual(section.HasValue("four"), True)
        self.assertEqual(section.GetValue("four"), "")
        self.assertEqual(section.FormatString("x[=two]x"), "xx")

    def test_config_include(self):
        self.assertEqual(self.config.GetSection('global_section').GetValue('global_value'),'lalala')
        self.assertEqual(self.config.GetSection('section_a').GetValue('value_3'),'override_value')

        config_ini = self.GetFilepath("test_include.ini")
        config = uConfig(config_ini)
        self.assertFalse(config.HasFailures())
        self.assertEqual(config.CountSections("Include"), 3)

        config_ini = self.GetFilepath("test_include_d.ini")
        config = uConfig(config_ini)
        self.assertFailureCodes(config, ["[F06]"])
        self.assertEqual(config.CountSections("Include"), 3)

        config_ini = self.GetFilepath("test_include_r.ini")
        config = uConfig(config_ini)
        self.assertFailureCodes(config, ["[F06]"])
        self.assertEqual(config.CountSections("Include"), 1)

    def test_config_overrides(self):
        # default section
        # [1.2] def1 in one section, but not in target section
        x1 =self.config.GetSectionById('b99').GetValue('def1')
        self.assertEqual(self.config.GetSectionById('b99').GetValue('def1'),'x_default')
        # [1.3] there are two matching sections, take the first
        x2 =self.config.GetSectionById('b99').GetValue('def2')
        self.assertEqual(self.config.GetSectionById('b99').GetValue('def2'),'first')
        self.assertEqual(self.config.GetSection('section_c').GetValue('def2'),'second')

        # override section
        self.assertEqual(self.config.GetSection('section_c').GetNumber('xval'),3)
        self.assertTrue(self.config.GetSection('section_c').HasValue('somelist'))
        self.assertEqual(self.config.GetSection('section_c').GetList('somelist')[0],'x')

    def test_config_section(self):
        # test header specification
        section = self.config.GetSection(":id_only")
        self.assertTrue(section is not None)
        self.assertEqual(section.GetName(), None)
        self.assertEqual(section.GetId(), "id_only")
        self.assertEqual(section.GetSpecification(), ":id_only")
        section = self.config.GetSectionById("id_only")
        self.assertTrue(section is not None)
        section = self.config.GetSection("test_labels")
        self.assertEqual(section.GetName(), "test_labels")
        self.assertEqual(section.GetId(), None)
        self.assertEqual(section.GetSpecification(), "test_labels")

        # test basic config section
        cs = uConfigSection(None, "my_cs", {'over':99, 'foo':'yes'})
        self.assertEqual(cs.GetName(), "my_cs")
        self.assertEqual(cs.GetClass(), "my_cs")
        self.assertEqual(cs.GetId(), None)
        self.assertEqual(cs.GetValue('over'), 99)
        self.assertEqual(cs.GetValue('red'), None)

        # test id in section header
        cs = uConfigSection(None, "my_cs:my_id", {'over':99, 'foo':'yes'})
        self.assertEqual(cs.GetName(), "my_cs")
        self.assertEqual(cs.GetClass(), "my_cs")
        self.assertEqual(cs.GetId(), "my_id")

        # test id, class, and label settings
        cs = uConfigSection(None, "my_cs:my_id", {'over':99, 'foo':'yes', '*id':'id2', '*class':'some_class', '*label':'tag'})
        self.assertEqual(cs.GetId(), "id2")
        self.assertEqual(cs.GetName(), "my_cs")
        self.assertEqual(cs.GetClass(), "some_class")
        self.assertTrue(cs.HasLabel('tag'))
        self.assertFalse(cs.HasLabel('tag2'))

        # test id, class, and label settings
        cs = uConfigSection(None, "my_cs:my_id:tag", {'over':99, 'foo':'yes', '*id':'id2', '*class':'some_class'})
        self.assertEqual(cs.GetId(), "id2")
        self.assertEqual(cs.GetName(), "my_cs")
        self.assertEqual(cs.GetClass(), "some_class")
        self.assertTrue(cs.HasLabel('tag'))
        self.assertFalse(cs.HasLabel('tag2'))

        # test id, class, and label settings
        cs = uConfigSection(None, "my_cs:my_id:tag, tag2", {'over':99, 'foo':'yes', '*id':'id2', '*class':'some_class'})
        self.assertEqual(cs.GetId(), "id2")
        self.assertEqual(cs.GetName(), "my_cs")
        self.assertEqual(cs.GetClass(), "some_class")
        self.assertTrue(cs.HasLabel('tag'))
        self.assertTrue(cs.HasLabel('tag2'))

        # test multiple labels
        cs = uConfigSection(None, "my_cs:my_id", {'over':99, 'foo':'yes', '*id':'id2', '*class':'some_class', '*label':'tag,tag2'})
        self.assertTrue(cs.HasLabel('tag'))
        self.assertTrue(cs.HasLabel('tag2'))

        # test override and default
        cs.add_defaults({'green':33})
        cs.add_overrides({'red':66, 'foo':77})
        self.assertEqual(cs.GetValue('over'), 99)
        self.assertEqual(cs.GetValue('green'), 33)
        self.assertEqual(cs.GetValue('red'), 66)
        self.assertEqual(cs.GetValue('foo'), 77)

        # test matches
        self.assertTrue(cs.IsMatch(Name='my_cs'))
        self.assertTrue(cs.IsMatch(Id='id2'))
        self.assertFalse(cs.IsMatch(Name='BAD', Id='id2'))
        self.assertFalse(cs.IsMatch(Name='my_cs', Id='BAD'))

        # test section specification
        config = uConfig()
        self.assertEqual(uConfig.ParseSpecification("section:id:label"), ['section','id','label'])
        self.assertEqual(uConfig.ParseSpecification(":id:label"), [None,'id','label'])
        self.assertEqual(uConfig.ParseSpecification("section::label"), ['section',None,'label'])
        self.assertEqual(uConfig.ParseSpecification("section:id:"), ['section','id',None])
        self.assertEqual(uConfig.ParseSpecification("::label"), [None,None,'label'])
        self.assertEqual(uConfig.ParseSpecification(":id:"), [None,'id',None])
        self.assertEqual(uConfig.ParseSpecification("section::"), ['section',None,None])
        self.assertEqual(uConfig.ParseSpecification("section:id"), ['section','id',None])
        self.assertEqual(uConfig.ParseSpecification("section:"), ['section',None,None])
        self.assertEqual(uConfig.ParseSpecification(":id"), [None,'id',None])
        self.assertEqual(uConfig.ParseSpecification("section"), ['section',None,None])
        
    def test_config_parameters(self):
        argv = ['foo.py', 'target', 'p1=v1', 's2.p2=v2', '::l3.p3=v3', ':i4.p4=v4', 's5:i5:l5.p5=v5', 's6::.p6=v6', ':s7:.p7=v7']
        cp = uConfigParameters(argv)
        self.assertEqual(cp.TestParam(argv[2]), [None, None, None, 'p1', 'v1'])
        self.assertEqual(cp.TestParam(argv[3]), ['s2', None, None, 'p2', 'v2'])
        self.assertEqual(cp.TestParam(argv[4]), [None, None, 'l3', 'p3', 'v3'])
        self.assertEqual(cp.TestParam(argv[5]), [None, 'i4', None, 'p4', 'v4'])
        self.assertEqual(cp.TestParam(argv[6]), ['s5', 'i5', 'l5', 'p5', 'v5'])
        self.assertEqual(cp.TestParam(argv[7]), ['s6', None, None, 'p6', 'v6'])
        self.assertEqual(cp.TestParam(argv[8]), [None, 's7', None, 'p7', 'v7'])

        argv = ['every=where', 'section_a.value_1=over1', 'section_b.foo', '$la.foo=over2', ':b99.foo=over3']
        params = uConfigParameters(argv)
        invalid_params = params.GetInvalidParams()
        self.assertEqual(len(invalid_params), 1)
        self.assertTrue('section_b.foo' in invalid_params)
        config2 = uConfig(self.config_ini, params)
        self.assertEqual(config2.GetSectionValue('*root', 'every'),'where')
        self.assertEqual(config2.GetSectionValue('section_a', 'value_1'),'over1')
        self.assertEqual(config2.GetSectionValue('section_b', 'foo'),'X')
        self.assertEqual(config2.GetSectionValue('lala_99', 'foo'),'over2')
        self.assertEqual(config2.GetSectionById('b99').GetValue('foo'),'over3')

        # test section specifications
        self.assertEqual(config2.GetSectionValue('section_b:b99', 'something'),'nothing')
        self.assertEqual(config2.GetSectionValue(':b99', 'something'),'nothing')
        self.assertEqual(config2.GetSectionValue('::ysome_1', 'fruit'),'raspberry')
        self.assertEqual(config2.GetSectionValue('lala_99::zsome_2', 'fruit'),'raspberry')
        self.assertEqual(config2.GetSectionValue(':xor99:zsome_2', 'fruit'),'raspberry')
        self.assertEqual(config2.GetSectionValue('lala_99:xor99:zsome_2', 'fruit'),'raspberry')

        config2 = uConfig(self.config_ini, argv)
        self.assertEqual(config2.GetSectionValue('*root', 'every'),'where')
        self.assertEqual(config2.GetSectionValue('section_a', 'value_1'),'over1')
        self.assertEqual(config2.GetSectionValue('section_b', 'foo'),'X')
        self.assertEqual(config2.GetSectionValue('lala_99', 'foo'),'over2')
        self.assertEqual(config2.GetSectionById('b99').GetValue('foo'),'over3')

        # test list to dict parameter conversion
        pdict = params.ExtractDict()
        self.assertEqual(pdict, {'every':'where', 'value_1':'over1', 'foo':'over3'})
        params = uConfigParameters(pdict)
        self.assertEqual(params.GetNamedParameters('every')[0], [None, None, None, 'every', 'where'])
        params = uConfigParameters(pdict, Section="blue")
        self.assertEqual(params.GetNamedParameters('every')[0], ["blue", None, None, 'every', 'where'])
        params = uConfigParameters(pdict, Section="blue:red")
        self.assertEqual(params.GetNamedParameters('every')[0], ["blue", "red", None, 'every', 'where'])
        params = uConfigParameters(pdict, Section=":red")
        self.assertEqual(params.GetNamedParameters('every')[0], [None, "red", None, 'every', 'where'])

    def test_write_lines(self):
        config2 = uConfig(self.config_ini)
        lines = config2.BuildConfigLines(Resolve=False)
        self.assertEqual(len(lines), 85)
        self.assertTrue('dessert=baked [=fruit] [=>section_b:foo.chaos] [=] pie' in lines)
        config2.WriteConfigLines(r"test\output\test-config-resolve.ini")
        self.assertFailureCodes(config2, ["[E10]", "[E10]"])
        config2.WriteConfigLines(r"test\output\test-config-original.ini", Resolve=False)
        self.assertEqual(len(config2.GetFailures()), 0)

        self.assertTrue(self.compare_ini_lines("test_merge.ini"))
        self.assertTrue(self.compare_ini_lines("test_expand.ini"))

    def compare_ini_lines(self, in_filename):
        test_filepath = os.path.join(r"test\lines", in_filename)
        output_filepath = self.config2lines(in_filename)
        try:
            f = open(test_filepath, "r")
            test_lines = f.readlines()
            f.close()
            f = open(output_filepath, "r")
            output_lines = f.readlines()
            f.close()
        except:
            return False
        return (test_lines == output_lines)
    
    def config2lines(self, in_filename):
        input_filepath = os.path.join(r"test\files", in_filename)
        output_filepath = os.path.join(r"test\output", in_filename)
        print(f'>> Reading {input_filepath}')
        config = uConfig(input_filepath)
        print(f'>> Writing {output_filepath}')
        config.WriteConfigLines(output_filepath)
        return output_filepath

    def test_config_failures(self):
        config_ini = self.GetFilepath("does_not_exist.ini")
        config = uConfig(config_ini)
        self.assertTrue(config.HasFailures())
        self.assertEqual(len(config.GetFailures(False)), 1)
        self.assertFailureCodes(config, ["[F01]"])
        self.assertFalse(config.HasFailures())
        self.assertEqual(len(config.GetFailures()), 0)

        config_ini = self.GetFilepath("test_failures.ini")
        config = uConfig(config_ini)
        self.assertTrue(config.HasFailures())
        self.assertEqual(len(config.GetFailures(False)), 2)
        self.assertFailureCodes(config, ["[F03]", "[F02]"])
        self.assertFalse(config.HasFailures())
        self.assertEqual(len(config.GetFailures()), 0)
