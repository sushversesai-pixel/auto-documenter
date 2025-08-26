
## Architecture Diagram
This diagram shows the top-level dependencies of the `src` module.

```mermaid
graph TD;
    src --> subprocess;
    src --> parser;
    src --> generator;
    src --> google;
    src --> os;
    src --> dotenv;
    src --> ast;
    src --> pathlib;
    src --> typer;

