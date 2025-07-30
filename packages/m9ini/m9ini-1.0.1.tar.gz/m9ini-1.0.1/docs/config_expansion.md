# uConfig Section Expansion

Sections may be expanded versions of other sections using section expansion.

This feature allows new sections to be created dynamically when a configuration is loaded.  The header of the expanded sections can be derivations of the base section using field replacement.

## Expansion use cases

There are multiple ways to use section expansion
- Create a new section that extends the properties of a base section
- Create multiple derivations based on a base section (or sections)
- Create multiple section derivations without a base section

The number of new sections created is the number of base sections times the number of derivations.
- Base sections are sections that match a section specification
- Derivations are one of:
  - An pipe-delimited list of values (eg. "1|2|three")
  - A reference to an external text block, section, or list property bounded by pipes (eg. "|SomeSection:myid|")
  - A numerical sequence bounded by pipes (eg. "|1-4+1|")

Properties in the base section can be accessed directly using "base." notation, or directly from the section if the property doesn't exist in the expanded section.  A property of the same name on the expanded section overrides the base section value.

In the example below, the base section specification finds 2 "Rock" sections.  The section definition expands by 3 Colors and 2 Size properties, resulting in 12 sections (2x3x2).  String replacement is used to calculate the id of the created sections, and "base" is used to refer to the base section.

```ini
# [Rock] is a section specification, identifying a base section; in this case, there are 2 base sections found with a section name of "Rock"
# Color has 3 variations
# Size has 2 variations
# Number of dynamic sections created are: 2 * 3 * 2 = 12
# During dynamic section expansion, name and id may use string replacement
[MySection:[=base.Type]_[=Color]_[=Size]] => [Rock]
Color=red|black|grey
Size=small|large
# these two are equivalent because "Type" is inherited from the base section
Describe1=[=Color] [=Type] rock
Describe2=[=Color] [=base.Type] rock

[Rock:rock_1]
Type=Granite

[Rock:rock_2]
Type=Quartz
```

It is not necessary to have a base section.  Section expansion can be accomplished through variation only.

```ini
# [] means no base section
# creates 3 sections, based on Color variations
[MySection:[=Color]] => []
Color=red|black|grey
```

Derivation may also be based on a text block or list field in another section.

```ini
# creates 6 sections, based on Color and Size variations (3 * 2)
# Color variations are read from a text block
[MySection:my_id] => []
Color=|:color_list|
Size=small|large

[[Colors:color_list]]
red
black
grey
```

## Backwards references

As stated above, an expanded section inherits properties from base sections, and a property defined in an expanded section overrides a property of the same name in the base section.

However, a reference in a base-level property will attempt to resolve locally before checking expanded sections.

```ini
[MySection] => [BaseSection]
Over1=Black
Over3=Blue

[BaseSection]
Over1=Red
Over2=Pink
BaseTest1=[=Over1]
BaseTest2=[=Over2]
BaseTest3=[=Over3]

# [=>MySection.BaseTest1] = Red -- base property takes precident
# [=>MySection.BaseTest2] = Pink -- use base property
# [=>MySection.BaseTest3] = Blue -- use expanded section property through a backwards reference because there is no base property of this name
```

This phenomenon is described in the [substitution documentation](config_subst.md#backwards-references-in-substitution).

## Expansion header syntax

An expanded section is defined using the following notation:
- **`[{section-specification}] => [{base-specification}]`**
- **`[{section-specification}] => []`**

**`{section-specification}`** is a specification in the form `{section}:{id}:{label}` where:
- All these components are optional
- Replacement syntax can refer to current section properties, base section properties, and external references
- `{label}` may contain multiple labels (comma-separated)

**`{base-specification}`** is a specification in the form `{section}:{id}:{label}` where:
- All these components are optional
- If no components are specified (`[]`), no base section will be used
- Replacement syntax is not permitted
- `{label}` may only contain a single label

If a specification is provided, but no base section is found, then no sections are created, resulting in this failure message:
- *"[F10] Base section not found for section expansion"*

## Section property access

Expanded sections support normal property access in the configuration file format or programmatically using **GetValue()** and **GetSectionValue()**.

In addition to normal property access, expanded sections support the following:
- Header component replacements are performed at the time the section is created
- All properties in the base section that are not defined in the expanded section are accessible as though they were in the expanded section
- If a property is defined in the expanded section with the same name as the base section, it overrides the base section value
- Base section properties can be accessed directly using the "base" property as a link to the base section

```ini
[MySection] => [BaseSection]
Field2=green

[BaseSection]
Field1=red
Field2=blue

# [=>MySection.Field1] evaluates to "red"
# [=>MySection.Field2] evaluates to "green"
# [=>MySection.base.Field2] evaluates to "blue"
```

Note that base section header components can be accessed using system defined properties:
- [=base.*name]
- [=base.*id]
- [=base.*class]

## Property expansion (variations)

In addition to expanding base sections, derivations of expanded sections can be created by property variations.  The values used in this rotation may be specified as:
- an internal list of values (pipe-delimited)
- a list of values from another property in this section (comma-delimited)
- a list of values from a property in another section (comma-delimited)
- all properties from another section
- all lines from a text block
- a numerical sequence formula

All these examples, except for pipe-delimited, a single reference must be wrapped in pipes (`|{reference}|`)

A numerical sequence is in one of the these formats.
- `{start}-{end}:{step}`: a sequence of `{step}` float values, evenly distributed from `{start}` to `{end}`, and including both
- `{start}-{end}+{increment}`: start with `{start}`, then increment by `{increment}` until reaching `{end}`

A base section is not required for property expansion.  If they are used together, the number of derivations multiply.

For simplicity, the below examples use property expansion without a base section.  All examples below produce the same results, which is 3 sections with the ids: "c_red", "c_green", "c_blue".

```ini
# an internal list of values
[MySection:c_[=Color]] => []
Color=red|green|blue
```

```ini
# a list of values from another property in this section
[MySection:c_[=Color]] => []
Color=|=MyList|
MyList=red,green,blue
```

```ini
# a list of values from a property in another section
[MySection:c_[=Color]] => []
Color=|=>MyData.MyList|

[MyData]
MyList=red,green,blue
```

```ini
# all properties from another section
[MySection:c_[=Color]] => []
Color=|MyData|

[MyData]
Color1=red
Color2=green
Color3=blue
```

```ini
# all lines from a text block
[MySection:c_[=Color]] => []
Color=|MyData|

[[MyData]]
red
green
blue
```

```ini
# a step-based numerical sequence
[MySection] => []
Number=|1-3:5|
# yields the sequence: 1, 1.5, 2, 2.5, 3
```

```ini
# an increment-based numerical sequence
[MySection] => []
Number=|1-30+5|
# yields the sequence: 1, 6, 11, 16, 21, 26
```

## Expanding on expanded sections

The ordering of sections and expanded sections in a configuration file is not relevant.  Section matching rules are applied after the file is loaded, and as sections are created from expanded section definitions.  Given this, expanded sections may also be derived off of expanded sections.

The below example results in 6 `[MySection]` sections.

```ini
[MySection] => [BaseSection]
Size=small|large

[BaseSection:base_[=Color]] => []
Color=|MyColors|

[[MyColors]]
red
green
blue
```
