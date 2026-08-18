class LightController:
    GESTURE_ACTIONS = {
        "palm": "on",
        "fist": "off",
        "two": "toggle",
    }

    def handle(self, gesture):
        return self.GESTURE_ACTIONS.get(gesture)