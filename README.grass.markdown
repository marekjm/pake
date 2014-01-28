## Description

Grass is a very simple and primitive language used to drive PAKE.
Its sole purpose is to expose PAKE API to developers (including main programmer) and
separate fast-changing, alpha-state internals from mostly solid UI.

----

## Features


### Constants

Keyword: `const`  
Syntax: `const [modifiers...] [type] name = value;`

Setting a constant creates new name in given namespace.
The only syntax that is possible with constants is declaration with instant definition,
uninitialized constant declarations are illegal.

```
const string foo = "foo";
const bool truth = true;

const string spam;  // illegal, will throw compilation error
```

Constants cannot be redefined or redeclared:

```
const bool truth = true;
truth = false;              // illegal, will throw compilation error

const string truth = "ultimate";    // illegal, will throw compilation error
```


### Variables

Keyword: `var`  
Syntax: `var [modifiers...] [type] name [= value];`

Setting a variable creates new name in given namespace.
Grass variables are *much* more flexible than constants and have several features:

* declarations: setting a name with or without declared type,
* definitions: giving a value to the name,
* redeclarations: giving the name a new type (drops previously stored value if any),
* redefinitions: giving the name a new value,

Definitions and redefinitions must set values with types matching declared type of a name.

Grass translator supports instant definitions after both declarations and redeclarations.

**Examples:**

*Declarations:*

```
var foo;            // omitting type declaration gives the name undefined type
var undefined bar;  // long form of `var bar;`

var string baz;     // declares type of the foo as `string`
```

*Definitions:*

```
var foo;
foo = "foo";        // legal: undefined-type name can take a value of any type

var bool bar;
bar = "bar";        // illegal, will throw compilation error: cannot assign value with type `string` to name with declared type `bool`

var string s;
s = "something";    // legal: value's type matches declared type of the name
```

*Instant definitions:*

```
var undefined foo = "foo";  // legal: undefined-type name takes all types

var bool bar = true;        // legal: value's type matches declared type of the name

var bool baz = "something"; // illegal, will throw compilation error: value's type does not match declared type of the name
```

*Redefinitions:*

```
var foo;
foo = "string";
foo = false;

var string bar;
bar = "bar";
bar = false;        // illegal, types don't match

var string baz = "string";
baz = "other string";
baz = false;        // illegal, types don't match
```

*Redeclarations:*

```
var foo = "foo";        // type: undefined, value: "foo"
var string foo;         // type: string, value: none (redeclarations drop values)
foo = "foo";
var string foo;         // type: string, value: none (redeclarations drop values even if redeclaed to the same type)
var bool foo = true;    // type: bool, value: true (instant definitions are possible with redeclarations)
```



### Namespaces

Grass understands the concept of namespace.
Namespaces are created using `namespace` keyword and can be nested.
Maximal nest level is undefined.

Namespace begins with `namespace` keyword, followed by name, followed by body enclosed in
curly braces, and ends with a semicolon.

Global file is compile as a top-level namespace.

Namespaces can contain every other concept understood by Grass.
However, although compiled, function calls in nested namespaces are not executed.

**Examples:**

*Creating empty namespace:*

```
namespace Foo {};
```

*Creating nestaed namespaces:*

```
namespace Foo {
    namespace Bar {
        namespace Baz {
        };

        namespace Bay {
        };
    };
};
```


### Type system

Grass uses strong, static type system to verify function calls being made.
Type checking can be disabled in function declarations by specifying parameter type as
`undefined` or omiting type declaration.

It is sometimes useful to disable type-checking in functions but is mostly useless
when declaring variables and constants -- references with undefined type are usually rejected
and giving such datapiece a value does not override it's type declaration.

**Examples:**

*Creating variables with undefined type and void value:*

```
var undefined foo;
var bar;
```

*Creating variables with undefined type and giving them a value:*

```
var undefined foo = "foo";
var bar = "bar";
var undefined baz;
var bay;

baz = "baz";
bay = "bay";
```

*Changing type of a variable (a.k.a. redeclaration):*

```
var foo;        // type: undefined, value: none
foo = "foo";    // type: undefined, value: "foo" (string)

// redeclarations drops previously stored value
var string foo; // type: string, value: none
foo = "foo";    // type: string, value: "foo" (string)

var bool foo = false;   // type: bool, value: false (bool)
```

*Changing value of a variable:*

```
var undefined foo;
foo = "foo";    // OK, undefined type accepts everything
foo = false;    // also legal, as the type of a variable is not overridden

var string foo;
foo = "foo";    // legal type of a value matches type of a variable
foo = true;     // illegal, would throw compilation error as type of value doesn't match type of the variable

var bool foo;
foo = true;     // legal, because type of variable has been changed
```

*Changing types of constants:*

```
const string foo = "foo";
const bool foo = true;      // illegal, constant with this name was already declared

delete foo;     // free the name
const bool foo = true;      // legal, as the foo has been deleted and the name was freed
```
