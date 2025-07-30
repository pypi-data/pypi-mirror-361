# uConfig Troubleshooting

This page describes troubleshooting techniques.

A list of substitution errors and their meaning can be found here:
- [uConfig Errors](config_errors.md)

## Printing errors

There are two categories of errors:
- *Load errors*: when loading a configuration file; error codes start with *[F]*
- *Access errors*: when accessing configuration values; error codes start with *[E]*

By default, errors are not printed.  To enable printing of errors to the console, call **PrintFailures()**.

**uConfig.PrintFailures(Print=*True*, PrintColor=*True*)**
- Enables the printing of failures for all configuration instances
- **Print**: turns printing on or off
- **PrintColor**: when printing is on, prints in color

## Error access

Error messages are queued within the **uConfig** object, and accessed using these methods.

**HasFailures()**
- Returns *True* if there are failures, including load failures

**GetFailures(Reset=*True*)**
- Returns a list of failures since the last load
- Returns an empty list if there are no failures
- If **Reset** is *True*, the failure status will be reset

Errors may result from loading a file or performing substitution during property access.

## Inspecting configuration

A list of lines in configuration (ini) format may be extracted for a configuration section or the entire configuration.

**uConfigSection.BuildConfigLines(*Raw*=False, *Resolve*=True)**
- Returns a list of lines describing the section in configuration format
- **Raw**: only properties and values in the original section will be included (do not apply defaults, overrides, or parameters)
- **Resolve**: when *True*, property substitutions will be performed.  Any values that are not substituted will be because of failures

**uConfig.BuildConfigLines(*Resolve*=True)**
- Returns a list of lines describing the entire configuration, in configuration format
- **Resolve**: when *True*, property substitutions will be performed.  Any values that are not substituted will be because of failures
- When **Resolve** is **True**, defaults, overrides, and parameters are applied, and these sections are not included
- When **Resolve** is **False**, defaults, overrides, and parameters are not applied and there will be an attempt to represent these as their own sections

[Link properties](config_slinks.md) will be represented as the section header of the referenced section.

## Writing configuration

A configuration can be written to a file.  This is helpful for trouble-shooting, and to have a record of the configuration for an operation involving section expansion and random substitutions.

**uConfig.WriteConfigLines(*Filepath*, *Resolve*=True, *Overwrite*=True, *Failures*=True)**
- Writes a configuration file
- **Resolve** is as described for **BuildConfigLines()**
- **Filepath** may include {YMD} and {TSM} placeholders
- **Overwrite**: When *True*, any existing file is truncated and overwritten.  Otherwise, will append to an existing file
- **Failures**: When *True*, a text block is written to the end of the file including any substitution failures; ignored when **Resolve** is *False*
- Returns *False*, or the filepath of the file that was written
