
## Architecture Diagram
This diagram shows the top-level dependencies of the `src` module.

```mermaid
graph TD;
    src --> typer;
    src --> subprocess;
    src --> dotenv;
    src --> google;
    src --> os;
    src --> ast;
    src --> generator;
    src --> parser;
    src --> pathlib;

