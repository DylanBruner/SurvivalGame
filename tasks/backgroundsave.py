from util.myenvironment import Environment

def task(env: Environment) -> None:
    if hasattr(env.viewport, "save"):
        env.viewport.save.save()