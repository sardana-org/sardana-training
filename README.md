# sardana-training
Sardana training materials (focused on developers)

The aim of the training is to exaplain the Sardana internals and to review all
the exisitng Sardana features.

The training materials contains:
* Jupyter notebooks with the theory and some code snippets
* practical examples of the controllers
  
The idea is to move as much as possible of this information to the [Sardana
documentation](http://www.sardana-controls.org)).

The recommended order of reviewing these materials is:
1. General
2. Pool
3. Controllers
4. Macroserver
5. Macros
6. Contributors

A short description of each of the notebooks can be found below.

1. General - exmplains all internals of the Sardana core. It starts from the
current implementation of the plugin system. Then it describes the core
classes of Sardana. In continuouation the Pool and MacroServer core components
are reviewed. At the end some miscellaneous topics are presented, for example
how Sardana uses threads to achieve concurrent behaviors.

2. Pool - reviews all the Pool elements like for example Pool moveables or
experimental channels and their interfaces. It also demonstrate how are they
used during the operations execution.

3. Controllers - demonstrates how to write your own controllers in order to
access a particular hardware or to achieve a specific calculation results for the
pseduo elements. This materials are supported by some examples of controllers
that can be found in the controllers sub-directory.

4. MacroServer - reviews all the macro features and describes the roles of
other MacroServer components. At the end the macro execution client
application, like Spock, are exmplained.

5. Macros - explains in more detail some macro features and demonstrates some
real examples of their use cases.

6. Contributors - teaches about the contributors tools and practices. It is
useful if you plan to get involved (more or less) in the project.

These materials were prepared in rush, so forgive the authors any mistakes/typos.
If so, don't forget to report them or just propose a pull request.
