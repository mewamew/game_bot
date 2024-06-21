import yaml

with open("config.yaml", "r") as conf:
    config_content = yaml.safe_load(conf)
    for key, value in config_content.items():
      globals()[key] = value

def edit_config(key, value):
    with open("config.yaml", "r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if f"{key}:" in line:
            lines[i] = line.replace(line.split(":")[1].strip().strip('"'), f"{value}")

    with open("config.yaml", "w") as file:
        file.writelines(lines)
