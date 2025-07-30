from mooch import Settings

defaults = {}
defaults["settings.mood"] = "happy"
defaults["settings.volume"] = 50

settings = Settings(".mooch-example/settings.toml", defaults)

print("Current Settings:")
print(f"Mood: {settings.get('settings.mood')}")
print(f"Volume: {settings.get('settings.volume')}")

settings["settings.volume"] = 75

print("Updated Settings:")
print(f"Mood: {settings.get('settings.mood')}")
print(f"Volume: {settings.get('settings.volume')}")
