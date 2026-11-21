# Laptop Hardware Market Analyzer (console program)
# Choose a few preferences, see matching laptop records, and save four charts.
# Prices are the recorded dataset values in Price_INR (not current shop prices).

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")                       # save charts as files, no pop-up windows
import matplotlib.pyplot as plt

# 1. Settings: files, folders, limits and chart colours
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_FOLDER, "cleaned_laptopData.csv")
CHART_FOLDER = os.path.join(BASE_FOLDER, "charts")
RESULT_FOLDER = os.path.join(BASE_FOLDER, "results")
MAX_SHOW = 10                               # laptops listed / drawn in chart 1
RAM_CHOICES = [4, 8, 16, 32]
BUDGET_BANDS = [                            # (label, lowest price, highest price)
    ("Under 30,000", 0, 29999.99),
    ("30,000 - 49,999", 30000, 49999.99),
    ("50,000 - 79,999", 50000, 79999.99),
    ("80,000 - 119,999", 80000, 119999.99),
    ("120,000 and above", 120000, 10 ** 9),
]
NEON = "#39ff14"
DARK_GREEN = "#008f11"
GRID_GREEN = "#0d3b0d"
PRICE_LABEL = "Recorded price (Price_INR, dataset value)"


# 2. Small helper functions for the terminal
def heading(text):
    print()
    print("=" * 60)
    print(text)
    print("=" * 60)


def ask_number(prompt, low, high):
    # Keep asking until the user types a whole number from low to high
    while True:
        answer = input(prompt).strip()
        if answer.isdigit() and low <= int(answer) <= high:
            return int(answer)
        print("Please type a number from", low, "to", high)


def ask_price(prompt):
    # Keep asking until the user types a valid price
    while True:
        answer = input(prompt).strip().replace(",", "")
        try:
            value = float(answer)
            if value >= 0:
                return value
        except ValueError:
            pass
        print("Please type a price such as 40000")


def money(value):
    return format(value, ",.0f")


# 3. Load the cleaned CSV and check the columns we need
def load_data():
    if not os.path.exists(CSV_FILE):
        raise SystemExit("Could not find cleaned_laptopData.csv next to this program.")
    df = pd.read_csv(CSV_FILE)
    needed = ["Company", "TypeName", "Cpu", "RAM_GB", "Gpu", "Price_INR"]
    for column in needed:
        if column not in df.columns:
            raise SystemExit("Missing column in CSV: " + column)
    df = df.dropna(subset=needed)           # only drop rows missing these columns
    # GPU category = first word of the Gpu text (Intel, Nvidia, AMD, ARM)
    df["GpuCategory"] = df["Gpu"].str.split().str[0]
    return df


# 4. Filtering: apply the choices; "skip" leaves one filter out
def apply_filters(df, choices, skip=""):
    result = df
    if choices["brand"] is not None and skip != "brand":
        result = result[result["Company"] == choices["brand"]]
    if choices["ram"] is not None and skip != "ram":
        result = result[result["RAM_GB"] >= choices["ram"]]
    if choices["gpu"] is not None and skip != "gpu":
        result = result[result["GpuCategory"] == choices["gpu"]]
    if choices["budget"] is not None and skip != "budget":
        low, high = choices["budget"]
        result = result[(result["Price_INR"] >= low) & (result["Price_INR"] <= high)]
    return result


# 5. Questions
def choose_brand(df):
    heading("Step 1 of 4: Brand")
    brands = df["Company"].value_counts().index.tolist()
    print("1. Any brand")
    for i in range(len(brands)):
        print(str(i + 2) + ".", brands[i], "(" + str(len(df[df["Company"] == brands[i]])) + " laptops)")
    number = ask_number("Your choice: ", 1, len(brands) + 1)
    if number == 1:
        return None
    return brands[number - 2]


def choose_ram():
    heading("Step 2 of 4: Minimum RAM")
    print("1. Any RAM")
    for i in range(len(RAM_CHOICES)):
        print(str(i + 2) + ". " + str(RAM_CHOICES[i]) + " GB or more")
    number = ask_number("Your choice: ", 1, len(RAM_CHOICES) + 1)
    if number == 1:
        return None
    return RAM_CHOICES[number - 2]


def choose_gpu(df):
    heading("Step 3 of 4: GPU category (first word of the GPU name)")
    gpus = df["GpuCategory"].value_counts().index.tolist()
    print("1. Any GPU")
    for i in range(len(gpus)):
        print(str(i + 2) + ".", gpus[i], "(" + str(len(df[df["GpuCategory"] == gpus[i]])) + " laptops)")
    number = ask_number("Your choice: ", 1, len(gpus) + 1)
    if number == 1:
        return None
    return gpus[number - 2]


def choose_budget(available):
    # "available" = laptops that already fit brand, RAM and GPU choices
    heading("Step 4 of 4: Budget (recorded dataset prices, INR)")
    print("Laptops available so far:", len(available))
    print("Price range of these laptops:", money(available["Price_INR"].min()),
          "to", money(available["Price_INR"].max()))
    print()
    for i in range(len(BUDGET_BANDS)):
        label, low, high = BUDGET_BANDS[i]
        count = len(available[(available["Price_INR"] >= low) & (available["Price_INR"] <= high)])
        print(str(i + 1) + ".", label, "(" + str(count) + " laptops)")
    any_number = len(BUDGET_BANDS) + 1
    custom_number = len(BUDGET_BANDS) + 2
    print(str(any_number) + ". Any budget (" + str(len(available)) + " laptops)")
    print(str(custom_number) + ". Custom range")
    number = ask_number("Your choice: ", 1, custom_number)
    if number == any_number:
        return None
    if number == custom_number:
        low = ask_price("Lowest price: ")
        high = ask_price("Highest price: ")
        while high < low:
            print("Highest price must not be smaller than lowest price.")
            high = ask_price("Highest price: ")
        return (low, high)
    return (BUDGET_BANDS[number - 1][1], BUDGET_BANDS[number - 1][2])


# 6. Show and save the matches
def show_matches(matches):
    heading("Matching laptops")
    print("Matches found:", len(matches))
    shown = matches.sort_values("Price_INR").head(MAX_SHOW)
    if len(matches) > MAX_SHOW:
        print("Showing the", MAX_SHOW, "lowest recorded prices (all matches are saved).")
    print()
    print("No. Brand     Type               RAM    CPU                         GPU                        Price (INR)")
    print("-" * 111)
    number = 1
    for _, row in shown.iterrows():
        print(str(number).ljust(3), row["Company"][:8].ljust(8), row["TypeName"][:18].ljust(18),
              (str(int(row["RAM_GB"])) + " GB").ljust(6), row["Cpu"][:27].ljust(27),
              row["Gpu"][:26].ljust(26), money(row["Price_INR"]).rjust(10))
        number = number + 1


def save_results(matches):
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    path = os.path.join(RESULT_FOLDER, "matching_laptops.csv")
    matches.drop(columns=["GpuCategory"]).to_csv(path, index=False)
    print("\nSaved all", len(matches), "matching rows to:", path)


def no_match_help(df, choices):
    heading("No laptops match all your choices")
    print("Laptops found if ONE choice is relaxed (others kept):")
    names = {"brand": "Brand", "ram": "Minimum RAM", "gpu": "GPU category", "budget": "Budget"}
    options = []
    for key in ["brand", "ram", "gpu", "budget"]:
        if choices[key] is not None:
            count = len(apply_filters(df, choices, skip=key))
            print("  - Remove", names[key] + ":", count, "laptops")
            options.append((count, names[key]))
    options.sort(reverse=True)
    print()
    useful = [o for o in options if o[0] > 0]
    if len(useful) == 0:
        print("Relaxing one choice is not enough. Try changing two choices.")
    else:
        print("Most useful change:", useful[0][1], "(" + str(useful[0][0]) + " laptops).")
        if len(useful) > 1:
            print("Next best:", useful[1][1], "(" + str(useful[1][0]) + " laptops).")


# 7. Charts (black background, green elements)
def style_chart(fig, ax, title, xlabel, ylabel):
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    ax.set_title(title, color=NEON, fontsize=12)
    ax.set_xlabel(xlabel, color=NEON)
    ax.set_ylabel(ylabel, color=NEON)
    ax.tick_params(colors=NEON)
    for side in ax.spines.values():
        side.set_color(DARK_GREEN)
    ax.grid(color=GRID_GREEN)
    ax.set_axisbelow(True)


def save_chart(fig, name):
    os.makedirs(CHART_FOLDER, exist_ok=True)
    path = os.path.join(CHART_FOLDER, name)
    fig.savefig(path, dpi=150, facecolor="black")
    plt.close(fig)
    return path


def chart_1_prices(matches):
    top = matches.sort_values("Price_INR").head(MAX_SHOW)
    labels = []
    for i, (_, row) in enumerate(top.iterrows()):
        labels.append(str(i + 1) + ". " + row["Company"] + " " + row["TypeName"] + " " + str(int(row["RAM_GB"])) + "GB")
    title = "Recorded Prices of Matching Laptops"
    if len(matches) > MAX_SHOW:
        title = "Recorded Prices: " + str(MAX_SHOW) + " Lowest-Priced of " + str(len(matches)) + " Matches"
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(labels, top["Price_INR"], color=DARK_GREEN, edgecolor=NEON)
    ax.invert_yaxis()
    for i in range(len(top)):
        ax.text(top["Price_INR"].iloc[i], i, " " + money(top["Price_INR"].iloc[i]), color=NEON, va="center", fontsize=8)
    style_chart(fig, ax, title, PRICE_LABEL, "Laptop (brand, type, RAM)")
    ax.set_xlim(0, top["Price_INR"].max() * 1.15)
    fig.tight_layout()
    return save_chart(fig, "chart1_recorded_prices.png")


def hardware_tier(ram, gpu_category):
    # Rough estimate: RAM points (1-4) + GPU points (1-3)
    if ram < 8:
        ram_points = 1
    elif ram < 16:
        ram_points = 2
    elif ram < 32:
        ram_points = 3
    else:
        ram_points = 4
    if gpu_category == "Nvidia":
        gpu_points = 3
    elif gpu_category == "AMD":
        gpu_points = 2
    else:
        gpu_points = 1                      # Intel and other
    total = ram_points + gpu_points
    if total <= 3:
        return "Basic"
    if total <= 5:
        return "Mid-range"
    return "High-end"


def chart_2_tiers(matches):
    tiers = []
    for _, row in matches.iterrows():
        tiers.append(hardware_tier(row["RAM_GB"], row["GpuCategory"]))
    order = ["Basic", "Mid-range", "High-end"]
    counts = [tiers.count(name) for name in order]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(order, counts, color=DARK_GREEN, edgecolor=NEON)
    for i in range(len(order)):
        ax.text(i, counts[i], str(counts[i]), color=NEON, ha="center", va="bottom")
    style_chart(fig, ax, "Estimated Hardware Tier of Matches\n(rough estimate - NOT benchmark performance)",
                "Estimated tier", "Number of matching laptops")
    fig.text(0.5, 0.01, "Rule: RAM points (<8GB=1, 8GB=2, 16GB=3, 32GB+=4) + GPU points (Intel/other=1, AMD=2, Nvidia=3).\n"
             "Total 2-3 = Basic, 4-5 = Mid-range, 6-7 = High-end.", color=NEON, ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    return save_chart(fig, "chart2_estimated_tier.png")


def chart_3_ram_median(matches):
    median_by_ram = matches.groupby("RAM_GB")["Price_INR"].median()
    count_by_ram = matches["RAM_GB"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(median_by_ram.index, median_by_ram.values, color=NEON, marker="o", linewidth=2)
    for ram in median_by_ram.index:
        ax.text(ram, median_by_ram[ram], "  n=" + str(count_by_ram[ram]), color=NEON, fontsize=8)
    ax.set_xticks(list(median_by_ram.index))
    style_chart(fig, ax, "Median Recorded Price by RAM Size\n(substitute chart - the dataset has no battery-life data)",
                "RAM (GB)", "Median " + PRICE_LABEL)
    fig.tight_layout()
    return save_chart(fig, "chart3_median_price_by_ram.png")


def chart_4_gpu_median(matches):
    median_by_gpu = matches.groupby("GpuCategory")["Price_INR"].median().sort_values()
    count_by_gpu = matches["GpuCategory"].value_counts()
    labels = [name + "\n(n=" + str(count_by_gpu[name]) + ")" for name in median_by_gpu.index]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(labels, median_by_gpu.values, color=DARK_GREEN, edgecolor=NEON)
    style_chart(fig, ax, "Median Recorded Price by GPU Category\n(substitute chart - the dataset has no ROI data)",
                "GPU category (n = number of matching laptops)", "Median " + PRICE_LABEL)
    fig.tight_layout()
    return save_chart(fig, "chart4_median_price_by_gpu.png")


# 8. Run one search from start to finish
def run_search(df):
    choices = {"brand": None, "ram": None, "gpu": None, "budget": None}
    choices["brand"] = choose_brand(df)
    choices["ram"] = choose_ram()
    choices["gpu"] = choose_gpu(df)
    available = apply_filters(df, choices)
    if len(available) == 0:
        no_match_help(df, choices)              # budget step is pointless with 0 laptops
        return
    choices["budget"] = choose_budget(available)
    matches = apply_filters(df, choices)
    if len(matches) == 0:
        no_match_help(df, choices)
        return
    show_matches(matches)
    save_results(matches)
    paths = [chart_1_prices(matches), chart_2_tiers(matches),
             chart_3_ram_median(matches), chart_4_gpu_median(matches)]
    print("Saved 4 charts:")
    for path in paths:
        print("  -", path)


# 9. Main menu
def main():
    df = load_data()
    heading("LAPTOP HARDWARE MARKET ANALYZER")
    print("Loaded", len(df), "laptop records. Prices are recorded dataset values (INR),")
    print("not current shop listings.")
    while True:
        print("\n1. New search\n2. Quit")
        if ask_number("Your choice: ", 1, 2) == 2:
            print("Goodbye!")
            print("Enjoy your new laptop!")
            break
            
        run_search(df)


try:
    main()
except (EOFError, KeyboardInterrupt):
    print("\nProgram stopped.")
