# all functions must be inside a class to avoid cluttering the global namespace because of the way we are forced to load scripts
class Cheatil:
    @staticmethod
    def patchClass(_class: type, overrides: dict) -> type:
        class_name = f"Patched{_class.__name__}"
        class_attributes = {**_class.__dict__}
        for key, value in overrides.items():
            if key in class_attributes:
                class_attributes[f"original_{key}"] = class_attributes[key]
            class_attributes[key] = value
        
        # Create a new class using the type() function
        patched_class = type(class_name, (_class,), class_attributes) # <--- thanks ChatGPT for this witchcraft
        
        return patched_class