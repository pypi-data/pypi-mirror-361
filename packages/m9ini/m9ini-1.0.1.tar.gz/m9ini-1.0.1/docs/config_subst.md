# uConfig Substitution

## Basic substitution

You may perform in-line substitution in configuration files using the following notation:

**`[={name}]`**: Replace with the value of the named property in this section

**`[=>{section}:{id}.{name}]`**: Replace with the value of a named field in another section
- `{section}` is an optional section name
- `{id}` can be a section id, or a property in this section with the section id to use
- `{name}` is a property name in the other section

If there are multiple section matches, the first match will be used.

If the specification does not match:
- The placeholder will remain in place to assist in identifying the source of the failure
- A failure will be added to [**GetFailures()**](config_troubles.md#error-access).

```ini
[Container]
material = copper
flower_id = lily
# this example uses a direct reference to a property in another section
first = [=>Flower:rose.description] in a [=material] vase
# this example uses an id from a property named flower_id
second = [=>Flower:flower_id.description] in a [=material] vase
# this example uses the internal property, id only
third = [=>:flower_id.description] in a [=material] vase

# this example demonstrates a replacement within a replacement
long_description = [=>:rose.description]

[Flower:rose]
color = red
description = A dozen [=color] roses

[Flower:lily]
color = orange
description = Tall fresh [=color] lily
```

## Real-time nature of substitution

Because substitutions are evaluated during run-time, references in `[*override]` or `[*default]` sections are evaluated in the context of the the section it is applied to, even when the property isn't defined for the section.

```ini
[*default:Bird]
Description=A [=Color] bird

[Bird:b1]
Color=red

[Bird:b2]
Color=blue

# [=>Bird:b1.Description] resolves to "A red bird"
```

## Backwards references in substitution

When referencing a property in another section, if that property contains any unresolved properties, there will be an attempt to find substituted properties in the source section containing the reference.

This applies to:
- Direct references (`[=>{section}.{property}]`)
- [Section links](config_slinks.md) (`{link}=>{section}`)
- [Expanded base sections](config_expansion.md) (`[=base.{property}]`)

In other cases, it may be more intuitive for source values to override target values, but when using backwards references, source values are only used when a target section property is not found.

```ini
[SourceSection]
Size=large
Color=blue
Test1=[=>OtherSection.Target1]
Test2=[=>OtherSection.Target2]

[OtherSection]
Target1=[=Size]
Target2=[=Color]
Color=red

# [=>SourceSection.Test1] resolves to "large" -- because Size property is not in target, so the source is used
# [=>SourceSection.Test2] resolves to "red" -- because Size property is in target
```

## Substitution with random selection

You may use substitution to select a random element from a list, text block, or section by appending ".?".

**uConfig** uses a caching mechanism that guarentees a consisstent result for a properties that contain random elements (`.?`).

- **`[={name}.?]`**: Select a random element from a list (comma-delimited)
- **`[=>{section}:{id}.?]`**: Select a random property from a config section, or a random line if the section is a text block
- **`[=>:{id}.?]`**: Same as above, but with id only
- **`[=>{section}:{id}.{name}.?]`**: Select a random element from a list (comma-delimited), from a config section
- **`[=>:{id}.{name}.?]`**: Same as above, but with id only

```ini
[Flower:my_flower]
Type=Rose,Iris,Lily
Description=[=>Color:my_colors.?] [=Type.?]

[[Colors:my_colors]]
Red
Black
Purple
Yellow
```

## Extending random selection

You may select a random element from a random property or text block line using this syntax.

- **`[=>{section}:{id}.?.?]`**: Select a random element from a list (comma-delimited), from a random config section
- **`[=>:{id}.?.?]`**: Same as above, but with id only

Depending on whether the referenced section is a text block, a random property or random line is selected.

```ini
[Flower:my_flower]
Random=A strange, [=>:my_colors.?.?] flower
Burning=A [=>:my_colors.Hot.?] flower
Frozen=A [=>:my_colors.Cold.?] flower

[Palette:my_colors]
Hot=Red,Orange,Yellow
Cold=Blue,Violet,Cyan
Muted=Black,White,Gray
```

## Formatting strings with substitution

The method **FormatString()** can be used to perform string replacements (`[= ]`) on an input string.

This is available for both **uConfigSection** and **uConfig**.
- **uConfigSection**: this is the context for properties
- **uConfig**: the root section is the context for properties
- Pointer syntax doesn't rely on context, so will return values in any context (`[=> ]`)

**FormatString(self, *Value*:str, *Raw*:bool=False, *Params*:dict=None, *Empty*:bool=False)**
- **Value**: string to perform replacements
- **Raw**: only use section properties and ignore defaults, overrides, parameters, and base sections
- **Params**: provide overrides for section values
- **Empty**: when *True*, token is replaced with an empty string on error; typical errors include:
  - Replacement token is an invalid format
  - A specified section or property was not found
