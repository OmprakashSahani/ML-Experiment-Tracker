import json
import matplotlib.pyplot as plt
from pathlib import Path

runs_dir = Path("runs")

names = []
accuracy = []

for file in runs_dir.glob("*.json"):
    data = json.load(open(file))
    names.append(data["name"])
    accuracy.append(data.get("metrics", {}).get("accuracy", 0))

plt.figure(figsize=(6,4))
plt.bar(names, accuracy, color=["#4CAF50", "#2196F3"])
plt.title("Accuracy Comparison")
plt.ylabel("Accuracy")
plt.xlabel("Run")

Path("docs").mkdir(exist_ok=True)
plt.savefig("docs/accuracy.png")
print("Saved docs/accuracy.png")
