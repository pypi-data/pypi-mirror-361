# uConfig Errors

Errors during execution are stored to a failure queue, and may be accessed programmatically.
- [**GetFailures()**](config_troubles.md#error-access)

Errors fall into two categories.
- [Load errors](config_errors#load-errors)
- [Substitution errors](config_errors#substitution-errors)

## Load errors

### [F01] Config file not found
- Specified configuration file does not exist
  
### [F02] Failed loading configuration file
- A general error indicating there was a failure while loading the file

### [F03] Unable to locate configuration file
- An include file referenced by `@` notation was not located
- Include file rules are found [here](../config.md#include-files)
- If an include file is missing, the entire load will fail
```ini
@this_file_does_not_exist.ini
```

### [F04] Invalid section header prefix (section ignored)
- Section header prefixs are special, system-defined values that start with *
- The only accepted prefixes are `*default` and `*override`
```ini
[*something:this is not a valid prefix]
```

### [F05] Invalid section header (section ignored)
- A config line starts with `[`, but does not match a section header format
- The entire section and its contents will be ignored
```ini
[$%  This header has invalid characters]
Prop1=yes

[This: header has: too many: colons]
Prop1=yes
```

### [F06] Warning: Duplicate/recursive include file reference detected
- There is a circular or duplicate reference to an include file
- The file will only be loaded once, but otherwise the config file will continue to load

## Section expansion errors (during load)

### [F10] Base section not found for section expansion
- This occurs during [section expansion](config_expansion.md)
- No sections could be found that match the base specification, located in the second brackets pair
```ini
[MyExpansion] => [not:found]
```

### [F11] Section expansion field using |reference| must be a section, text block, or evaluate to a string property
- This occurs during [section expansion](config_expansion.md)
- When referencing a property, use `=` or `=>` within the pipes
- When referencing a section or text block, only provide the section specification
```ini
# this the correct way to reference a property for section expansion
[First_Good] => []
Color=|=Colors|
Colors=red,green,blue

# this INCORRECT
[First_Bad] => []
Color=|[=Colors]|
Colors=red,green,blue

# this is the correct way to reference a text block
[Second_Good] => []
Color=|MyColors|
Colors=red,green,blue

# this INCORRECT
[Second_Bad] => []
Color=|=>MyColors|
Colors=red,green,blue

[[MyColors]]
red
green
blue
```

### [F12] Section expansion field is invalid, begin must be less than end
- A numerical sequence during section expansion is specified as `|{start}-{end}:{step}|` or `|{start}-{end}+{increment}|`
- `{start}` is not less than `{end}`
```ini
[MyExpansion] => []
sequence=|10-1+1|
```

### [F13] Section expansion field is invalid numerical iteration
- A numerical sequence during section expansion is specified as `|{start}-{end}:{step}|` or `|{start}-{end}+{increment}|`
- Syntax for section expansion was incorrect
```ini
[MyExpansion] => []
sequence=|1-5|
```

## Substitution errors

These happen during calls to access section properties, not when loading a file.

### [E01] Link does not specify a valid section
- When defining a section link, no sections match the specification
- A section link follows this syntax: `{property}=>{section}:{id}`

### [E02] Link is not a valid specification
- Section link syntax is incorrect

### [E03] Replacement is a link to a section without any property specified
- A link was used in a replacement when a property is required
- `{property}=[=>{section}:{id}]` will cause this error (note the lack of a property)
- This scenario is discussed at length in [uConfig section linking](config_slinks.md)
```ini
[MySection]
# no property is specified when using a section reference
Prop1=[=>:myid]

[OtherSection:myid]
Color=Red
```

### [E04] Replacement logic is not valid property syntax
- Within a substitution brackets, the syntax for accessing a property in this section was incorrect
- Property access is denoted by `[= ]`
- Basic property syntax is `[={property}]`

### [E05] Replacement logic is not valid pointer syntax
- Within a substitution brackets, the syntax for accessing a property in another section was incorrect
- Property access in another section is denoted by `[=> ]`
- Basic pointer syntax is `[=>{section}:{id}.{property}]`

### [E06] Random (text block contains no lines)
- Random syntax (`.?`) was used to reference a text block, but there is no data in the text block (no lines)
```ini
[MySection]
Prop1=[=>MyTextBlock.?]

[[MyTextBlock]]
```

### [E07] Random (section contains no properties)
- Random syntax (`.?`) was used to reference a section, but there were no properties in the section
```ini
[MySection]
Prop1=[=>OtherSection.?]

[OtherSection]
```

### [E08] Invalid index (of a text block)*
- A line of a text block can be accessed by index, with the first line being 0
- The provided index references a line that does not exist
```ini
[MySection]
Prop1=[=>MyTextBlock.5]

[[MyTextBlock]]
Red
Blue
Green
```

### [E09] Invalid property (of a text block)
- Text blocks are unlike sections in that they do not contain properties, just a list of lines
- Replacement syntax attempted to access a named property on a text block
```ini
[MySection]
Prop1=[=>MyTextBlock.Color]

[[MyTextBlock]]
Red
Blue
Green
```

### [E10] Section not found
- A referenced section was not found
```ini
[MySection]
# id not defined
Prop1=[=>:myid.Size]

[OtherSection]
Size=large
```

### [E11] Section property not found
- There was a reference to a property that does not exist
- *KNOWN ISSUE*: In the case of a backward-reference, this error will be triggered and then it may go on to resolve the property in an expanded section using a backward reference
```ini
[MySection]
Prop1=[=>:myid.Size]

[OtherSection:myid]
Color=Red
```

### [E12] Invalid property (of a string)
- There was an attempt to access a property of a string (another property)
- Only sections have properties (including links to sections)
```ini
[MySection]
Color=Red
Prop1=[=Color.Second]
```

### [E13] Property indirection failure ($)
- A property specified in a replacement string using $ syntax was not found
- Indirection means that the name of a section, id, or property is specified in a local property, instead of naming it directly
- Indirect property references are used in external section references `[=> ]`
```ini
[MySection]
# Note missing property OtherId
Prop1=[=>:$OtherId.Color]
# Note missing property Option
prop2=[=>:$myid.$Option]

[OtherSection:myid]
Color=Red
```

### [E14] Base section does not exist
- There was a reference to the base section where there is no base section
- "base" is a reserved keyword used to reference a base section
- Base sections are the right side of the following notation: `[] => []`
```ini
[MySection]
Prop1=[=base.Prop2]
```

### [E19] Detected recursive self-reference
- The configuration file contains recursive references
```ini
[MySection]
Prop1=[=Prop2]
Prop2=[=Prop1]
```

### [E20] Exceeded maximum reference depth
- Property references are extremely deep, which may indicate a configuration error or unexpected recursion
- Maximum reference depth is 9
