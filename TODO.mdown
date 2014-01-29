## Networking and data distribution

0.  management of aliens should be moved to `network` part of backend before creating a set of requests in transaction runner,

----

## Scripting (transactions) interface

Scripting interface should support only features required for transaction-system inside PAKE and
nothing more.

Features to be implemented:

0.  (**DONE**) variable declarations - `var foo;`,
0.  (**DONE**) variable definitions - `var foo = "foo"`;
0.  (**DONE**) constants - `const foo = "foo";`,
0.  (**DONE**) referencing variables and constants,
0.  (**DONE**) function declarations (but not definitions),
0.  (**DONE**) default parameter in function declarations,
0.  (**DONE**) function calls - `foo(0)`,
0.  (**DONE**) named and unnamed parameters in function calls,
0.  classes to contain functions, variables and constants,
0.  (**DONE**) namespaces (classes?) to enable such function calls as `pake.node.init()`,

Features **not to** be implemented:

0.  `if` and `else` flow-controls,
0.  loops (be it `for` or `while`),
0.  `switch` statement,
0.  math-like expressions (addition, multiplication etc.),
