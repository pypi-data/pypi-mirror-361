# uConfig Programmatic Access

## Reading Configuration

### Load config file

Configuration is loaded either during instantiation, or by calling **LoadFile()**.

**uConfig(*Filepath*=None, *Parameters*=None)**
- Construct a configuration object, and load the specified configuration file
- Parameters is a **uConfigParameters** object that contains overrides for configuration values, or a list of configuration parameters.
- Parameters is ignored when Filepath is not specified

**LoadFile(*Filepath*, *Parameters*=None)**
- Load a configuration file with optional **Parameters**
- Returns *True* on success, or *False* on failure.

**HasFailures()**
- Returns *True* if there are failures, including load failures

**GetFailures(Reset=*True*)**
- Returns a list of failures since the last load
- Returns an empty list if there are no failures
- If **Reset** is *True*, the failure status will be reset

```python
from m9lib import uConfig, uConfigParameters

# use the constructor
cfg = uConfig("config.ini")

# use the LoadFile() method
cfg = uConfig()
params = uConfigParameters(["name=value", "section.name=value", "section:id:label.name=value"])
success = cfg.LoadFile("config.ini", params)
if success is False:
  print('load has failed')

# check for failures
if cfg.HasFailures():
  print('this is another way to check for failures')
  for failure in cfg.GetFailures():
    print(failure)
```

### Access values

Access methods can be found on both the **uConfig** and **uConfigSection** classes.  _None_ is returned when a value is not found. **uConfig** methods access `*root` section values.  The `*root` section has values that come before any section headers are specified.

- **HasValue(*Name*, *Raw*=False)**: Returns _True_ if the value was provided in configuration
- **GetValue(*Name*,*Default*=None,*Raw*=False)**: Value as a string
- **GetBool(*Name*,*Default*=None)**: Returns _True_ when value is "true", case insensitive; otherwise _False_
- **GetNumber(*Name*,*Default*=None)**: Returns value as an int.  Returns _False_ when value does not convert to int
- **GetFloat(*Name*,*Default*=None)**: Returns value as a float.  Returns _False_ when value does not convert to float
- **GetList(*Name*,*Separator*=',')**: Returns delimited values as a list

**uConfig** also has quick methods for accessing section values directly.  If there are multiple sections with the same name, accesses the first one.

- **HasSectionValue(*Section*,*Name*,*Default*=None,*Raw*=False)**
- **GetSectionValue(*Section*,*Name*,*Default*=None,*Raw*=False)**
- **GetSectionBool(*Section*,*Name*,*Default*=None)**
- **GetSectionNumber(*Section*,*Name*,*Default*=None)**
- **GetSectionFloat(*Section*,*Name*,*Default*=None)**
- **GetSectionList(*Section*,*Name*,*Separator*=',')**

*Section* can be a section specification.  *Default* is returned if there is no value.  When *Raw* is true, defaults, overrides, and parameters are not applied.

For convenience, the root section can be accesed by using a *Section* of `*root`.

The priority order of a returned value is:
  1. A parameter from uConfigParameters
  2. An `[*override]` section in the configuration file
  3. A section value
  4. A `[*default]` section in the configuration file

When a configuration property appears in configuration but is blank, **HasValue()** will return *True* and **GetValue()** will return an empty string.

```ini
[MySection]
# property specified but is blank
MyProp=
```

### Section access

**uConfigSection** objects can be accessed by calling:

- **CountSections(*Name*=None,*Id*=None,*Label*=None)**: Returns a count of sections that satisfy some combination of section name, id, or label
- **GetSection(*Name*=None,*Id*=None,*Label*=None,*Index*=0)**: Specify any combination of section name, id, or label.  If there are multiple sections that satisfy the condition, use index to iterate

Helper methods are provided that provide simpler access, but ultimately resolve to calls to **GetSection()**.

- **GetRootSection()**: Access root values (defined before any section headers)
- **GetSectionById(*Id*)**: Return a section by id
- **GetSectionByIndex(*Name*,*Index*=0)**: Return a section by name, iterating via index

Return a list of sections.

- **GetSections(*Name*=None,*Id*=None,*label*=None)**: Returns a list of sections that satisfy some combination of section name, id, or label
- **GetSectionsBySpec(*Specification*)**: Returns a list of sections that satisfy a section specification of `<name>:<id>:<label>`

### uConfigSection methods

- **GetConfig()**: Returns the **uConfig** this section belongs to
- **GetId()**: Returns the id (or *None*)
- **GetName()**: Returns the section name
- **GetClass()**: Returns the class.  This is the same as the name, unless **\*class=** is used
- **GetSpecification()**: Combines id and name into a specification in the format `<name>:<id>`
- **HasLabel(*Label*)**: Returns *True* when the section has the specified label
- **IsMatch(*Name*=None,*Id*=None,*Label*=None)**: Returns *True* when section satisfies some combination of section name, id, or label

The section also has the normal property access methods.
- **HasValue(*Name*, *Raw*=False)**
- **GetValue(*Name*)**
- **GetBool(*Name*)**
- **GetNumber(*Name*)**
- **GetFloat(*Name*)**
- **GetList(*Name*,*Separator*=',')**

**GetPropertyNames(*Raw*=False, *ExcludeStar*=True)**
- Returns a *list* of all property names in this section
- If **Raw** is *True*, does not apply parameters, overrides, or defaults
- Special "star" properties will be excluded unless **ExcludeStar** is *False*

**GetProperties(*Raw*=False, *Resolve*=True)**
- Returns a dict containing all section properties after applying parameters, overrides, and defaults
- *Raw*: When *True*, does not apply parameters, overrides, or defaults
- *Resolve*: When *True*, resolves substitutions and references
- Includes special "star" properties

Any defaults, overrides, or parameters set at the **uConfig** level still apply to **uConfigSection**.

### Text block sections

**IsTextBlock()** returns *True* if the section is a text block.

**GetTextBlock()** returns a list of strings if the section is a text block.  Each string is a line of the text block.

## Overriding Config values with Parameters

There will be cases where you would like to specify or override configuration values from a command line execution without editing a config file.  This is accomplished using configuration parameters.

Configuration parameters override name-value pairs according to section matching rules, using a section specification.

When combined with a name-value pair, the full specification for a config parameter is: `<name>:<id>:<label>.<name>=<value>`.

Here are some examples:
- `p1=v1`
- `mysection:myid:mylabel.p1=v1`
- `mysection.p1=v1`
- `:myid.p1=v1`
- `::mylabel.p1=v1`
- `mysection::mylabel.p1=v1`

### uConfigParameters

Instantiate **uConfigParameters** by passing in a list of config parameters in the form `<name>:<id>:<label>.<name>=<value>`).

If there are badly formatted or invalid parameters, they can be accessed by calling **GetInvalidParams()**

A **uConfigParameters** are passed into **uConfig** when loading a file.  Parameters that match a section specification will override matching section values.

**uConfigParameters(*Parameters*, *Section*=None)**
- When *Parameters* is a *list* of config parameters, *Section* is ignored
- When *Parameters* is a *dict* of name-value pairs, *Section* may contain a section specification that will be applied to each value-pair.

```python
# a fully formed set of config parameters
params = uConfigParameters(["mysection.one=first", "mysection.two=second"])

# this is equivalent
params = uConfigParameters({'one':'first', 'two':'second'}, "mysection")
```

### Creating merged sections

New sections can be created by merging a combination of existing sections and dictionaries together.

**NewMergedSection(*Header*, *First*, *Second*, *Third*=None, *Raw*=False, *Resolve*=True)**
- **Header**: A header in the standard format of `{section}:{id}:{labels}`
- **First**, **Second**, **Third** can be **uConfigSection** or *dict*
- Properties of **Second** will be merged into **First**.  Existing fields will not be overwritten
- Properties of **Third** will then be merged.  This is optional
- **Raw**: When *True*, only native properties of sections are merged (no defaults, overrides, parameters, etc)
- **Resolve**: When *True*, substitutions are performed before the merge; otherwise substitution formulas remain in the property value

The newly merged section is added to configuration.  All default, override, and parameter overrides are performed.  The section may be accessed programmatically and via substitution, just like any other section.

### Adding and modifying properties

Section properties can be manipulated after configuration is loaded.  This only applies to native properties.  Defaults and overrides are applied on top of native properties automatically.

**ClearProperty(*Name*)**
- Clears a property

**SetProperty(*Name*,*Value*)**
- Sets a property value
- If **Value** is *None*, the property will be cleared
- **Value** is converted to a string

**SetLink(*Name*, *Section*)**
- Sets a link property
- **Section** must be a **uConfigSection**
- Links can be used in property substitutions

```ini
[MySection]
Flower=Roses

[OtherSection]
Color=Red
```

```python
config = uConfig("test.ini")
section1 = config.GetSection("MySection")
section2 = config.GetSection("OtherSection")

section1.SetLink("MyLink", section2)
section1.SetProperty("Description", "[=Flower] are [=MyLink.Red]")

print(config.GetSectionValue("MySection", "Description")) # outputs "Roses are Red"
```

## Use example

```ini
# save these contents to config.ini
g1 = top level

[section_a]
# another way to describe section header
*id = id_222
*label = mytest,testtwo
x=1
y=2
z=3

[section_a:id_555:mytest]
z=7

[section_b:id_333]
mylist = seven,ate, nine

[*override:section_a]
# override values for section a
y=99

[*default:::mytest]
# default values for sections with label "mytest"
extra=data 123
```

```python
from m9lib import uConfig, uConfigParameters

# override parameters.  the first is a root value (no section specified); the second targets sections with the label "testtwo"
params = uConfigParameters(["g2=two", "::testtwo.r=rrrrrrrrrrrrr"])

# load the configuration file
cfg = uConfig("config.ini", params)

print('g1 = '+cfg.GetValue('g1')) # "top level"
print('g1 = '+cfg.GetSectionValue('*root', 'g1')) # "top level"

# note that when there are multiple section_a, GetSectionValue() only returns the first one
print('x = '+cfg.GetSectionValue('section_a', 'x')) # 1
print('y = '+cfg.GetSectionValue('section_a', 'y')) # 99; from *override
print('z = '+cfg.GetSectionValue('section_a', 'z')) # 3

# returns a list of uConfigSection
sections = cfg.GetSections(Name='section_a')
for section in sections:
    print(f"name={section.GetName()} id={section.GetId()} x={section.GetValue('x')} y={section.GetValue('y')} z={section.GetValue('z')}")
    # name=section_a id=id_222 x=1 y=99 z=3
    # name=section_a id=id_555 x=None y=99 z=7

# test that parameters override is working
print('g2 = '+cfg.GetValue('g2')) # "two"
print('r = '+cfg.GetSectionById('id_222').GetValue("r")) # "rrrrrrrrrrrrr"
print(cfg.GetSectionById('id_222').GetProperties()) # display all properties
```
