from util.myenvironment import Environment

def task(env: Environment) -> None:
    """
    A task that gets registered in the main file
    """
    if hasattr(env.viewport, "save"):
        env.viewport.save.save()