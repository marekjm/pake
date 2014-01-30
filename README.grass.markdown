## Description

Grass is a very simple and primitive language used to drive PAKE.
Its sole purpose is to expose PAKE API to developers (including main programmer) and
separate fast-changing, alpha-state internals from mostly solid UI.


#### Compiled or interpreted

The language is quasi-compiled. Majority of things (e.g. type checking, correctness of references etc.) is resolved during the stage of
translation form source code to a form that can bu supplied to runner.
The term *quasi-compiled* is used because the language is also not interpreted in a classic meaning of this term.


#### Sources of input

All input is known at the beginning of translation stage.
There is no `cin`, `getline()`, `input()` or any other mechanism to supply data at runtime.
This is the first major limitation of the language.
However, it is justified when the domain of Grass is taken into account.


#### Modularization

Grass has full, and very flexible, support for modularized programs.
However, due to the early stage of development and the design of the language
programs which are very granular can take relatively big amounts of memory to compile.

This is because all references and values are resolved immediately after they are found.
When, for example, translator encounters function call and sees that one of the parameters is given a reference as
an argument it immediately looks for the value of this reference (there is no *resolving* stage).
Such behaviour means that all files that are being `import`-ed are compiled before they are put into
main compilation trunk.

0.  Grass compiles file `foo.grass`,
0.  file `foo.grass` imports file `bar.grass` (-> compilation branch #1),
0.  Grass stops compilation of `foo.grass` and compiles `bar.grass`,
0.  file `bar.grass` imports file `baz.grass` (-> compilation branch #1.1),
0.  Grass stops compilation of `bar.grass` and compiles `baz.grass`,
0.  compilation of `bar.grass` is restored at the point where compiler encountered import of `baz.grass` (-> compilation branch #1),
0.  compilation of `foo.grass` is restored at the point where compiler encountered import of `bar.grass` (-> compilation main trunk),
0.  file `foo.grass` imports file `baz.grass` (-> compilation branch #2),
0.  compilation of `foo.grass` is restored at the point where compiler encountered import of `baz.grass` (-> compilation main trunk),
0.  compilation is finished,

This approach raises two problems:

* compilation units are not independent,
* when, during one compilation, two differet files import another file this another file is compiled twice (this does not occur when file is imported twice from the same file),

To solve this problems linking mechanism should be introduced, what will be possible after the method of storing compiled form of Grass source code is developed.
This would also require separation of the resolving stage from translation stage.


----

## Features

Here are described current features of the Grass metalanguage.

----

### Comments

Grass supports two types of comments:

* inline: starting with `//` token and going until first newline `\n` is found,
* block: starting with `/*` token and going until `*/` closing token is found,

Block comments can be inserted in very strange places like function parameters list:

```
function void foo(string s /* this is typed parameter */, undefined u /* and this is untyped parameter */);
```

This will not throw errors during compilation as
translator MUST strip comments and whitespace before it starts compilation.

---

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

----

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
bar = "bar";        /* illegal, will throw compilation error:
                     * cannot assign value with type `string` to name with declared type `bool`
                     */

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

----

### Modifiers

Modifiers are inserted between the defining keyword and type declaration inside declaration of a name.
Here is a list of all modifiers available in Grass (NI means it is not yet implemented, i.e. will be accepted but
will not affect behaviour of the compiler):

* `guard` (NI): prevent name from being deleted,
* `hard` (NI): applies only to variables, make the type stronger - prevents redeclarations,
* `infer` (NI): applies only to variables, make the variable switch types dynamically - changing its type to the type of the value it holds in given moment,

The `infer` and `string` modifiers do not make sense when passed togeher and
translator should throw a compilation error when they both are given to one name.

**Syntax when using modifiers**

The syntax is more restrictive when modifiers are used, i.e. type declaration CANNOT be omitted.
To give the example: `var foo = true;` is legal syntax but `var infer foo = true;` is not.
This is due to the internal working of the compiler.

Lets say there is a need to create a variable that will hold `string` and then a `bool` value.
This can be achieved oth with redeclarations aor `infer` modifier.

*With redeclarations:*

```
var string foo;
foo = "this is true";   // type: string

/* some code */

var bool foo;   // redeclaration to change type to bool, `foo = true;` would be illegal
foo = true;     // type: bool
```

*With `infer` modifier:*

```
var infer string foo;
foo = "this is true";       // legal, types match

/* some code */

foo = true;  // also legal, because of the `infer` modifier
```

**Modifiers can be removed by redeclaring the variable without them.**
Note, however, hat `strong` modifier prevents redeclarations so in this case a variable must be `delete`-ed first.


*Creating a datapiece name which value and type cannot be changed, and which cannot be deleted*

```
const guard bool truth = true;
```

*Creating a datapiece name which type cannot be changed, and which cannot be deleted*

```
var guard hard bool spam = "with eggs";

spam = 'with ham';  // OK, it's a variable - value still can be changed
var spam;           // compilation error: `strong` prevents redeclarations
delete spam;        // compilation error: `guard` prevents from being deleted
```

*Creating a datapiece name that adjusts its type dynamically*

The `infer` modifer allows for changing type of the variable without redeclaring it.

```
var infer something;    // type: undefined or void

something = true;   // type: bool
something = "spam"; // type: string
```

----

### Functions

Keyword: `function`  
Syntax: `function [modifiers...] name ( [[type] parameter,]... ) [{}] ;`

Given the fact that Grass doesn't currently (2014-01-28) have any concpet of flow-control structures function body is not compiled and
thus not used.
Functions in Grass act as a way of exposing other program's internals - and to act as a separation layer and API.
Actual implementations of declared functions are written in real language (e.g. Python) for which a Grass bridge exists.

However, Grass will perform all necessary type-checking and parameter/arguments validation so if the API is properly exposed,
Grass output can be usually executed by runner without further validation (apart from necessary conversion between Grass datatype representations and
the target language datatype representations).

*Various ways of declaring functions:*

```
function void foo ();           // no parameters

function void foo (x);          // one parameter with undefined type and no default value

function void foo (string x);   // one parameter with defined type and no default value

function void foo (x="");       // one parameter with undefined type and set default value

function void foo (string x="");    // one parameter with defined type and set default value   
```

When function parameter is declared with an undefined type, type-checking can be *considered disabled* for this parameter as
names with undefined type accept value of any type.
However, a parameter with defined type will not accept value with undefined type.
Parameter can be set as accepting arguments with undefined type by omitting type declaration or explicitly defining type as `undefined`.

----

### Function calls

One of the most important features of Grass.
After compilatio, function calls are executed by runner written in target language.

**Passing parameters**

When calling a function parameters can be passed to it in several ways.
The way of passing a parameter does not affect type checking mechanism.

*Unnamed*

Parameter names are resolved based on he parameter name order.

```
function void f(x, y, z);

f(0, 1, 2);  // x: 0, y: 1, z: 2
```

*Named*

Parameter names are taken from the call tokens.

```
function void f(x, y, z);

f(x=0, y=1, z=2);
```

*Mixed*

Parameter names are resolved based on the parameter order set by the declaration, and partially taken from call toknes.
One restriction of this style of calling is that unnamed parameter MUST NOT appear after named parameter (as it breaks the reliablility of
parameter order).

```
function void f(x, y, z);

f(0, 1, z=2);   // legal
f(0, y=1, z=2); // legal
f(x=0, 1, z=2); // illegal
```

**Default parameters**

Parameters may be ommited in call when they have default value set (it's in such cases assumed that this
parameter takes default value set in declaration).

```
function void f(bool truth = true);

f();  // legal, `truth` is assumed to be `true`
```

**Invalid calls**

Invalid calls are caught at compile time which ensures validity and safety of the generated pseudo-executable code (list of calls).
There are several reasons which make a call invalid.

* too many parameters: when an unexpected number of parameters is passed to a function,
* missing parameters: when a parameter is left without value,
* unknown parameters: when a function gets a parameter with unknown name (usually caused by typos),
* invalid parameter types: most obvious error - when a type of given value does not match declared type of a parameter,

```
function void foo(bool truth, string answer = "");

foo(true, "", 0);       // too much parameters
foo();                  // missing (without value) parameter: truth
foo(truth="true");      // invalid type
foo(spam="with eggs");  // unknown parameter
```

----

### Namespaces

Keyword: `namespace`  
Syntax: `namespace [modifiers...] name { ... };`

Grass understands the concept of namespace.
Namespaces can be nested and maximal nest level is undefined.

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

----

### Deleting names

Keyword: `delete`  
Syntax: `delete reference;`

This keyword is used to delete previously declared names.
There are currenlty no restrictions on what can be deleted (even whole namespaces) as long as `delete` points to valid reference.

It is possible to redeclare constants using `delete` keyword:

```
const string foo = "foo";   // declare `foo` as a constant string
delete foo;                 // free the name
const bool foo = true;      // redeclare `foo` as constant bool
```

----

### Importing

Keyword: `import`  
Syntax: `import "path";`

The `"path"` is a string containing path to the file which should be imported.
Importing means:

* read the file the path points to,
* compile it,
* cache compiled result in case next import points to the same file,
* copy requested elements from imported file to the one being compiled,

Import can go two ways: either importing everyhting or just specific element of the imported file.

Importing *everything* means copying every variable, constant, function etc. from the imported file to the one being compiled. 
Syntax for such import is very straightforward:

```
import "path/to/source/file.grass";
```

Importing specific elements requires additional code:

```
import "path/to/source/file.grass" namespace Foo;   // import only namespace `Foo`


import "path/to/source/file.grass" function bar;    // import only function `bar`
import "path/to/source/file.grass" var baz;         // import only variable `baz`
import "path/to/source/file.grass" const bax;       // import only constant `bax`
```

When importing variables, functions and constants you do not declare their type or modifiers and
doing so result in an error.


----

## Type system

Grass uses strong, static type system to verify function calls being made.
Type checking can be disabled in function declarations by specifying parameter type as
`undefined` or omiting type declaration (type is then assumed to be `undefined`i).

It is sometimes useful to disable type-checking in functions but is mostly useless
when declaring variables and constants -- references with undefined type are usually rejected
and giving such datapiece a value does not override it's type declaration.


&nbsp;

----

Copyright (c) 2014 Marek Marecki  
Grass is licensed under GNU GPL v2, v3 or any later version of this license.
