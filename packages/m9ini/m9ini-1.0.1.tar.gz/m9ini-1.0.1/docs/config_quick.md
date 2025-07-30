# m9ini Quick Reference

## Basic Info

| Syntax | Examples | Notes | Docs |
| ----- | ----- | ----- | ----- |
| `# {comment}`<br>`; {comment}` | `# my comment`<br>`; my comment` | A comment line is ignored. | [include](../README.md#include-files) |
| `@{inifile}` | `@myini`<br>`@myini.ini`<br>`@subfolder\myini` | Include an ini file.<br>Path and extension are optional. | [comments](../README.md#comments) |

## Section Header

| Syntax | Examples | Notes | Docs |
| ----- | ----- | ----- | ----- |
| `[{section}:{id}:{labels}]` | `[MySection:MyId:label1,label2]`<br>`[MySection:MyId]`<br>`[:MyId]` | All elements are optional.<br>Id need not be unique.<br>Replacement only allowed in expanded sections. | [sections](../README.md#config-sections) |
| `[[{section}:{id}:{labels}]]` | `[[MyTextBlock:MyId:label1,label2]]` | A text block is followed by a sequence of lines.<br>A text block does not contain properties. | [textblocks](../README.md#text-block-sections) |
| `[{section}:{id}:{labels}] => [{section}:{id}]` | `[MySection] => [BaseSection]`<br>`[MySection] => []` | Create a multitude of sections using section expansion. See section expansion below. | [expansion](config_expansion.md#expansion-header-syntax) |

## Section Properties

| Syntax | Examples | Notes | Docs |
| ----- | ----- | ----- | ----- |
| `*id={value}` | `*id=SuperId` | Reserved keyword that overrides the section id. | [sections](../README.md#config-sections) |
| `*name={value}` | `*name=MyName` | Reserved keyword that overrides the section name. | [sections](../README.md#config-sections) |
| `*class={value}` | `*class=MyClass` | Reserved keyword that specifies a class name.<br>By default, the section class is the section name. | [sections](../README.md#config-sections) |
| `{name}={value}` | `MyColor=red` | A simple property value. |  |
| `{name}={value1},{value2},..,{valueN}` | `MyColorList=red,green,blue` | A list of values. |  |
| `{property}=>{section}:{id}` | `Link=>OtherSection:SomeId`<br>`MyLink=>:some_id` | A property that links to another section based on a section specification.  | [links](config_slinks.md#section-link-properties) |

## Replacement Syntax

| Syntax | Examples | Notes | Docs |
| ----- | ----- | ----- | ----- |
| `[={property}]` | `MyDescription=Color is [=MyColor]` | Replace with a local properties value.<br> | [substitution](config_subst.md#basic-substitution) |
| `[=base.{property}]` | `MyDescription=Color is [=base.MyColor]` | Replace with a base property value.<br>Used in section expansion. | [exuse](config_expansion.md#expansion-use-cases) |
| `[=>{section}:{id}.{property}]` | `MyProp=Access [=>OtherSection.Prop1]` | Access a property in another section using a section specification. | [substitution](config_subst.md#basic-substitution) |
| `[={link}.{property}]` | `MyProp=Access [=Link.Prop1]`<br>`MyProp=Access [=Link.OtherLink.Prop2]` | Access a property in another section through a link.<br>If the property is a link, this pattern may continue. | [links](config_slinks.md#section-link-properties) |
| `${property}` | `MyProp=Access [=>OtherSection:$local_id.Prop1]`<br>`MyProp=Access [=>:my_id.$local_prop]`<br>`Link=>OtherSection:$local_id` | Within a section specification, $ may be used to replace part of the specification with the value of a local property. | [indirect](config_slinks.md#indirect-property-reference) |
| `[={property}.?]` | `Prop1=Random color is [=MyColorList.?]` | Select a random entry from a list. | [random](config_subst.md#substitution-with-random-selection) |
| `[=>{section}:{id}.?]` | `MyProp=Access [=>OtherSection.?]` | Select a random property from a section.<br>If section is a text block, select a random line. | [random](config_subst.md#substitution-with-random-selection) |
| `[=>{section}:{id}.?.?]` | `MyProp=Access [=>OtherSection.?.?]` | Select a random property from a section, then a random entry from the property, assuming it is a list. | [random](config_subst.md#substitution-with-random-selection) |

## Override Sections

| Syntax | Examples | Notes | Docs |
| ----- | ----- | ----- | ----- |
| `[*default:{section}:{id}:{labels}]` | `[*default:MySection]`<br>`[*default::MyId]` | In this context, `{section}:{id}:{labels}` is called a \"section specification\".<br>Properties of this section are available for all sections that match the specification unless the section has the same property, which takes precedence.| [override](../README.md#default-and-override-rules) |
| `[*override:{section}:{id}:{labels}]` | `[*default:MySection]`<br>`[*default::MyId]` | Properties of this section are available for all sections that match the specification, and will take precedence over any section properties.| [override](../README.md#default-and-override-rules) |
| `*level={number}` | `*level=3`<br>`*level=-9` | When multiple *default or *override sections match a section, and provide a property value, the first takes precedence.<br> *level specifies a priority (instead of using the first).<br>Lowest level takes priority.<br>When not specified, *level is 0. | [override](../README.md#default-and-override-rules) |

## Section Expansion

| Syntax | Examples | Notes | Docs |
| ----- | ----- | ----- | ----- |
| `[{section}:{id}:{labels}] => [{section}:{id}]` | `[MySection] => [BaseSection]`<br>`[MySection] => [:MyId]` | Create an expanded selection based on another section.<br>Properties are inherited from the base section.<br>Inherited properties may be overriden by local properties.<br>Number of sections created based on number of base sections * number of property variations. | [expansion](config_expansion.md#expansion-header-syntax) |
| `[{section}:{id}:{labels}] => [{section}:{id}]` | `[MySection:Id[=base.*id]] => [BaseSection]`<br>`[MySection:[=MyColor]_[=base.color]] => [:MyId]` | Substitution can be used on the left side of an expanded section equation. | [exuse](config_expansion.md#expansion-use-cases) |
| `[{section}:{id}:{labels}] => []` | `[MySection] => []` | Create an expanded selection with no base section.<br>Number of sections created based on number of property variations. | [expansion](config_expansion.md#expansion-header-syntax) |
| `{property}={value1}\|{value2}\|..\|{valueN}` | `MyColor=red\|green\|blue` | Create property variations with specified values. | [exvar](config_expansion.md#property-expansion-variations) |
| `{property}=\|={property}\|` | `MyColor=\|=MyColorList\|` | Create property variations from a local list property.<br>Follows rules of `[= ]` syntax. | [exvar](config_expansion.md#property-expansion-variations) |
| `{property}=\|=>{section}:{id}.{property}\|` | `MyColor=\|=>OtherSection.Prop1\|` | Create property variations from an external list property.<br>Follows rules of `[=> ]` syntax. | [exvar](config_expansion.md#property-expansion-variations) |
| `{property}=\|{section}:{id}\|` | `MyColor=\|OtherSection.SomeId\|` | Create property variations using all properties from another section, or all lines from a text block. | [exvar](config_expansion.md#property-expansion-variations) |
| `{property}=\|{begin}-{end}:{steps}\|` | `MyValue=\|1.0-2.5:4\|` | Create property variations with a numerical sequence, dividing evenly based on steps. | [exvar](config_expansion.md#property-expansion-variations) |
| `{property}=\|{begin}-{end}+{increment}\|` | `MyValue=\|1-3+0.2\|` | Create property variations with a numerical sequence, by incrementing using specified value. | [exvar](config_expansion.md#property-expansion-variations) |
