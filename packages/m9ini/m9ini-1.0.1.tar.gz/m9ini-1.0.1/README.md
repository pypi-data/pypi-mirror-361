# m9ini Configuration Library

**m9ini** is a python library for reading configuration files bases on the INI format.

This library has many advanced features, including:
- Sections can be identified by name, class, or label
- Rules for default and overriding property values
- Name-value sections and text-block sections
- String substitution using properties in the same or other section
- Object-oriented section inheritance and expansion
- Robust features for programmatic access

An easy-to-use demonstration of these features is found at [m9ini-demo](https://github.com/MarcusNyne/m9ini-demo).

## Advanced feature reference

This page contains information about basic configuration file features.

Advanced features are found on other doc pages:
- [Substitution](docs/config_subst.md): Replace placeholder strings with section property values
- [Section linking](docs/config_slinks.md): Establish links and references to other sections
- [Section expansion](docs/config_expansion.md): Dynamically generate section variations
- [Programmatic access](docs/config_prog.md): Access configuration files from Python
- [Quick reference](docs/config_quick.md): Syntax quick reference
- [Troubleshooting](docs/config_troubles.md): Tips for troubleshooting syntax or runtime issues
- [Error messages](docs/config_errors.md): A list of error messages with troubleshooting tips

## Config File Format

```ini
@<ini-filepath>
; includes another configuration file

setting=value
# global settings (before any section headers)

[<section>]
# section name, which is the default "class name"
[<section>:<id>]
# section with id
[<section>:<id>:<label1>,<label2>, .. ,<labelN>]
# section with id and label(s)
[*default:<section>:<id>:<labels>]
# default values for a section
[*override:<section>:<id>:<labels>]
# override values for a section

# section header overrides
*id=<id> # section id (defaults to id from section header)
*class=<class> # section class (defaults to name from section header)
*label=<labels> # one or more labels as a comma-delimited list

# section property
setting=value

# link to another section
other_section=><section>:<id>:<label>

# a text block is a section without name-values, just a list of strings
[[<section>:<id>:<labels>]]
line 1
line 2
line 3

# dynamically create N sections based on (the number of base sections) * (the number of property variations)
# => [] contains rules for matching a base section (can be blank)
# properties are inherited from the base section
# setting values containing a pipe ("|") define property variations
[<section>:<id>:<labels>] => [<section>:<id>]
setting=value1|value2
```

### Include files

The syntax to include another ini file is: `@<ini_file>`.  The ".ini" extension is optional.

If an include file is not found, the entire load will failure.  Information about missing include files is available from [**GetFailures()**](config_troubles.md#error-access).

If an include file is referenced more than once (or recursively), a warning is issued, but the load operation continues.  The include file is only loaded once.

```ini
# these lines are equivalent
@myfile
@myfile.ini
# you may specify a path to the file
@subfolder\myfile

# in this example, myfile.ini is only loaded once even though it is included twice, with the following warning
# [F06] Warning: Duplicate/recursive include file reference detected
```

### Comments

Comments may begin with `#` or `;`.

```ini
# a comment
; a comment
```

### Config sections

A section header is specified in square brackets and includes a section name followed by an optional id and list of labels in the format `[<name>:<id>:<labels>]`.
- `<name>`: represents a section "class".  Sections with similar purpose and properties should have the same name.
- `<id>`: an identifier.  Not required to be unique.
- `<label>`: a comma-delimited list of labels

Config sections contain name-value pairs.  There are three reserved values:
- `*id` is synonomous with the section id
- `*class` may specify a class value (defaults to section name)
- `*label` contains a comma-delimited list of labels

After the INI file is read, sections can be accessed by name, id, or label using a "section specification".

```ini
# these are some examples of section headers
[section_a]
[section_b:my_id]
[section_c::label1,label2]
[section_d]
*id=my_id
[section_e:some_id]
*class=my_class
*label=label1,label2
```

### Section specification

A section specification is a rule that matches one or more configuration sections based on the section *name*, *id*, and/or *label* as a string in this format: `<name>:<id>:<label>`.  Any or all components of the section specification can be specified left to right.  For example: `<name>`, `<name>:<id>`, or `<name>:<id>:<label>`.

The following combinations are supported:
  - `<name>`
  - `<name>:<id>`
  - `:<id>`
  - `:<id>:<label>`
  - `::<label>`
  - `<name>:<id>:<label>`
  - `<name>::<label>`

If any of these start with $, it is interpreted as "starts with".  When multiple parts are specified, all parts must be satisfied.  An empty specification matches all sections.

### Text block sections

A text block is a section that is read as many lines under the section header without any properties.

The section header of a text block follows the same identification rules as a normal section header, but is wrapped with double brackets.

```ini
[[mytext:text_id]]
line 1
another line
# comments are ignored

blank line above is captured
```

### Default and override rules

Default and override values may be specified with a "section specification" in the section header.

Section header rules are specified as `<name>:<id>:<label>`, with all these being optional.  When multiple are specified, all must be true.  When none are specified, all sections match.

For example: `[*default:$mycl::mylabel]` will provide default values for all sections that start with "mycl" and have the label "mylabel".

For example: `[*override::myid]` will provide override values for all sections with the id "myid".

- A property need not exist in a target section for the property to be added by a default or override rule
- When a property is found in multiple default or override sections, the first to appear will take priority
- A "*level" property may be added to a default or override section to set the priority level
  - The default priority is 0
  - Lower levels take priority
  - Priorities may be negative

```ini
[*default:MySection]
One=Bananas
Two=Strawberries
Three=Peaches

[MySection]
One=Red
Two=Blue

[*default:MySection]
Three=Black

[*override:MySection]
Two=Violet

[*override:MySection]
*level=-1
Two=Pink

# [=>MySection.One] is "Red"
# [=>MySection.Two] is "Pink"
# [=>MySection.Three] is "Peaches"
```
