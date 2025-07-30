# uConfig Section Linking

## Section link properties

A property may be established that represents a link to another section.  Once the link is established, properties of the linked section can be accessed in replacement syntax.

The syntax to create a property link is highly flexible.  Follow one of these patterns, depending on your needs.  If multiple sections match, only the first is linked.

- **`{property}=>{section}`**: Link to a remote section (by name)
- **`{property}=>{section}:{id}`**: Link to a remote section (with id)
- **`{property}=>:{id}`**: Link to a remote section (by id)

Replacements are valid within this syntax.

```ini
# section linking examples
[MySection]
Link1=>OtherSection
Link2=>OtherSection:sid
Link3=>:sid

# this is equivalent
sid_property=sid
Link4=>:[=sid_property]

# these are all equivalent
Example1=[=Link4.PickColor]
Example2=[=Link4.Colors.?]
Example3=[=>:sid.Colors.?] # this is replacement using a section reference (see below)

[OtherSection:sid]
PickColor=[=Color.?]
Colors=Red,Yellow,White
```

If you wish to start a property value with `>`, simply add a space.

```ini
[MySection]
# this is a link
Link1=>OtherSection
# this is a value (not a link)
Prop1= >OtherSection
```

## Section reference replacement

Sections may be referenced in replacements by using a `[=> ]` instead of `[= ]`.  If multiple sections match, only the first is used.
- `[= ]`: a reference to a property in this section
- `[=> ]`: a reference to a property in another section

The following syntax is supported.
- **`[=>{section}:{id}.{property}]`** Replace with a property in another section
- **`[=>{section}.{property}]`** Replace with a property in another section (by section name)
- **`[=>:{id}.{property}]`** Replace with a property in another section (by id)

```ini
# section reference example
[MySection]
Example3=[=>:sid.Colors.?]

[OtherSection:sid]
Colors=Red,Yellow,White
```

## Indirect property reference

Local properties may be referenced in replacement syntax using a dollar-sign ($) within an external reference or section link.

Indirect references are valid when replacing a section, id, or property.

This is a powerful feature when used with [Section expansion](config_expansion.md).

```ini
[MySection]
sectionname=Other
mysection=[=sectionname]Section
myid=[=>Colors.?]
myfield=Fruit
# Prop1 and Prop2 are equivalent
Prop1=[=>OtherSection:red.Fruit]
Prop2=[=>$mysection:red.Fruit]
# Prop3 selects a random section using a text block
Prop3=[=>OtherSection:$myid.Fruit]
# Prop3 and Prop4 are equivalent
Prop4=[=>OtherSection:$myid.$myfield]

[[Colors]]
red
blue

[OtherSection:red]
Fruit=Strawberry

[OtherSection:blue]
Fruit=Blueberry
```

Here is an example using section expansion.

```ini
[MySection] => [MyBase]
SomeId=[=base.color_id]
ExampleColor=[=>MyLookup:$SomeId.Color]

[MyBase:base_1]
color_id=id_1

[MyBase:base_2]
color_id=id_2

[MyLookup:id_1]
Color=red

[MyLookup:id_2]
Color=blue
```

## Link property vs. replacement

Note the similarity between a link property and a replacement containing a section reference:
- Link property syntax: `{property}=>{section}:{id}`
- Replacement with section reference: `{property}=some text [=>{section}:{id}.{name}] :)`

A link property can be thought of as a reference to a section, and is not intended to evaluate to a value, since it is a link to a section.  If a link property is printed, it will display as a section header.

Replacement happens within the context of a string.  The string may contain multiple replacements.  For this reason, the replacement should resolve to a property value, not a section reference.  If there is an attempt to perform a replacement with a link (section reference), an error message will be added to the configuration list of errors.  Thus, the following syntax is not supported:
- An invalid replacement using a section reference: `{property}=some text [=>{section}:{id}] :)`

Here is an example that uses a link property to another section:

```ini
[MySection]
# link to another section
MyLink=>OtherSection
Description1=This replacement is invalid: [=MyLink]
Description2=This replacement is good: [=MyLink.Color]

[OtherSection]
Color=Red
```

## Backwards references

Property references in property values accessed via links or direct references will attempt to resolve locally.  However, if a property could not be resolved, their will be an attempt to resolve the property reference using a source section.  This is called a "backwards reference".

```ini
[MySection]
Over1=Black
Over3=Blue
Test1=[=>OtherSection.ExtTest1]
Test2=[=>OtherSection.ExtTest2]
Test3=[=>OtherSection.ExtTest3]

[OtherSection]
Over1=Red
Over2=Pink
ExtTest1=[=Over1]
ExtTest2=[=Over2]
ExtTest3=[=Over3]

# [=>MySection.BaseTest1] = Red -- linked section property takes precident
# [=>MySection.BaseTest2] = Pink -- use linked section property
# [=>MySection.BaseTest3] = Blue -- use source section property through a backwards reference
```

This phenomenon is described in the [substitution documentation](config_subst.md#backwards-references-in-substitution).

## Chaining links

Once links are established, they can be chained together with other links or substitutions as long as the last element in the chain is a property.

```ini
# a chain linking example
[MySection]
Animal_ids=cat,mouse
LinkId=[Animal_ids.?]
AnimalLink=>Animal:[=LinkId]
AnimalDescription=[=AnimalLink.Description]

[Animal:cat]
ColorLink1=>Colors
Name=Cat
Description=[=ColorLink1.?] [=Name]

[Animal:mouse]
ColorLink2=>Colors:cid
Name=Mouse
Description=[=ColorLink2.?] [=Name]

[[Colors:cid]]
Brown
White
Black
Orange
```

```ini
# this example combines the link into a single chained replacement
[MySection]
AnimalLink=>Animal:cat
AnimalColor=[=AnimalLink.ColorLink1.ColorList.?]

[Animal:cat]
ColorLink1=>Colors
Name=Cat

[Colors:cid]
ColorList=Brown,White,Black,Orange
```

## Text block access

Text blocks do not have properties, so an attempt to access a text box using a property will result in an error.

However, text blocks can be accessed by index, starting at 0

```ini
[MySection]
Box=A [=>:colors.1] box

[[MyTextBlock:colors]]
Red
Green
Blue

# [=>MySection.Box] resolves to "A Green box"
```

## Programmatic access to section links

The configuration methods **GetValue()** and **GetSectionValue()** will always return a string.  If the property being accessed is a link, the string will be a representation of the section header.

If you wish to access the **uConfigSection** object, use the following methods:
- **GetLink(*Name*, *Raw*=False)**
- **GetSectionLink(*Section*, *Name*, *Raw*=False)**

```ini
[MySection]
BoxColor=>:colors

[MyTextBlock:colors]
ColorList=Red,Green,Blue
```

```python
section = config.GetSectionValue("MySection", "BoxColor")
# section is "[MyTextBlock:colors]"

section = config.GetSectionLink("MySection", "BoxColor")
# section is a uConfigSection object
value = section.GetValue("ColorList")
# value is "Red,Green,Blue"
```