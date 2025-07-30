## What's a project?

- Context: Path of the project
- Tasks: List of tasks
- Events:
- Timeline:
- Outline:

```yaml
_variables_:
    event:
        title:
        date:
            _schema_: "{date}[#{time}]"
        category:
            _doc_: "An item in outline."
context:
    _schema_: "{path}"
events:
    _schema_: "[{event.category}.]{event.title}"
outline:
    _schema_: "[{category}/]"
```

```yaml
context: "work.projects"
outline:
    core:
    utils:
    journal:
todo:
    - What is a project? #status.design
    - journal: Add support for `_dir_.yaml`, directory metadata file
    - core: Implement schema validation (apischema or pydantic)
    - journal: Excape rich notation in tasks values `[]` #type.fix #status.design
    - utils: Flatten/fold directory contents
    - core: |
          Support `#needs` tag for dependencies
          searching for all the tasks with said category above the task itself
          top tasks should be prioritized.
    - journal: Support basic markdown parsing for task contents
timeline:
    2025-03-15:
        - core: Initial implementation
    2025-03-21:
        - core: Generalized subparser creation from submodules' public functions #type.fix
```

# Development choices

## Dependencies

| Name | URL                                                  | Complexity/Size | Auto Generation |
|------|------------------------------------------------------|:---------------:|:---------------:|
| tap  | https://github.com/swansonk14/typed-argument-parser/ |   Multi file    |       Yes       |
| plac | https://github.com/ialbert/plac/                     |   Single file   |       Yes       |
| fire | https://github.com/google/python-fire/               |   Multi file    |       Yes       |