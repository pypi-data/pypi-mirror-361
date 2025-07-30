# Config Testing Notes

## 1. Defaults

- [1.1] Prefix is "*default"
- [1.2] Default value is applied, even when the value does not exist in the target section
- [1.3] When a value is found in multiple default sections, the first one wins

## 2. Overrides

## 3. Raw Access

## 4. Local property access

Code references a property in this section.

- [4.1] `[={property}]` Simple replacement using a local property
- [4.2] `[={property}.?]` Random list element of a local property
- [4.3] References cannot be embedded, but can chain

## 5. Section property access

Code references a property in another section.

- [5.1] `[=>{section}:{id}.{name}]` Simple replacement of a remote property
- [5.2] `[=>{section}:{id}.{name}.?]` Random list element of a remote property
- [5.3] `[=>:{id}.{name}]` Simple replacement of a remote property (id only)
- [5.4] `[=>:{id}.{name}.?]` Random list element of a remote property (id only)
- [5.5] `[=>{section}:{id}.?]` Random property of a remote section
- [5.6] `[=>{section}:{id}.?.?]` Random list element of a random property in a section
- [5.7] `[=>{section}:{id}.?]` Random line of a remote text block
- [5.8] `[=>{section}:{id}.?.?]` Random list element of a random line in a text block
- DELETE [5.9] All above scenarios where the id is not found, but `{id}` is a local property containing an id
- [5.11] `[=>${property}:{id}.{name}]` Section name redirect to a local property
- [5.12] `[=>{section}:${property}.{name}]` Section id redirect to a local property
- [5.13] `[=>{section}:{id}.${property}]` Property name redirect to a local property
  - If section is a property section: property name
  - If section is a text block: line index

Failures:
- Invalid syntax
- Section not found
- Section doesn't contain property
- A section reference wtihout a property is an invalid replacement since it cannot be converted to a string
  - For example: `[=>{section}]` or `[=>{section}:{id}]`
  - "Replacement is a link to a section without any property specified"

## 6. Section link properties

A property that acts as a link to a section

- [6.1] `{property}=>{section}` Link to a remote section
- [6.2] `{property}=>{section}:{id}` Link to a remote section (with id)
- [6.3] `{property}=>:{id}` Link to a remote section (id only)
- DELETE [6.4] `{property}=>{id}` Link to a remote section (id only)
- DELETE [6.5] `{section}=>{id}` Link to a remote section (property name is section name)
- DELETE [6.6] All above scenarios where the id is not found, but `{id}` is a local property containing an id
- [6.7] Where `{section}` or `{id}` contain replacements

- [6.11] `{property}=>${property}` Section name redirect to a local property
- [6.12] `{property}=>{section}:${property}` Section id redirect to a local property
- [6.13] `{property}=>:${property}` Section id redirect to a local property (id only)

- GetProperties links
  - Do we need prop name in value?
  - Convert back to original text

## 7. Indirect property access

Code references a property of another section through a link in this section.

- [7.1] `[={name}]` Simple replacement using a linked property
- [7.2] `[={name}.?]` Random list element of a linked property
