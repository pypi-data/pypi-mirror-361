# How to get involved

Take a look at [the issues page](https://github.com/bvn-architecture/Reggie/issues), maybe someone already wants to do this, maybe you could team up?

If you want to make a new checker, they live in the `src\reggie\checkers` folder, and `template_checker.py` will give you a place to start. Once it works, uncomment the `@register_checker` line and it'll be sucked into the main code.

If you want to debug locally, you can add this to your `.vscode/launch.json` file and it'll give you an entry point.

```json
{
      "name": "Debug Reggie - Full Workflow",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/debug_reggie.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      },
      "justMyCode": false,
      "stopOnEntry": false
    },
```

To install locally, to test in a different project:

```
pip install -e .
```

(from inside this folder)
