#!/usr/bin/env python3
"""
GitHub Contribution Generator
Target: 500-600 contributions per year
Automatically distributes naturally across months
"""

import os
import subprocess
from datetime import datetime, timedelta
import random


def calculate_yearly_distribution(start_date, end_date):
    """
    Calculate how many commits per year, accounting for partial years
    Target: 500-600 per full year
    """
    total_days = (end_date - start_date).days + 1
    years = total_days / 365.25

    # Random target between 500-600 per year
    target_per_year = random.randint(500, 600)
    total_target = int(years * target_per_year)

    return total_target, target_per_year


def distribute_monthly(start_date, end_date, total_target):
    """
    Distribute total commits across months naturally
    Smooth distribution with minimal gaps
    """
    monthly_targets = {}
    current = start_date
    months = []

    # Get all months in range
    while current <= end_date:
        month_key = (current.year, current.month)
        if month_key not in months:
            months.append(month_key)

        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)

    # Base amount per month
    base_per_month = total_target // len(months)
    remaining = total_target - (base_per_month * len(months))

    # Distribute with slight variation (±30% from base) for natural look
    for month_key in months:
        variation = random.uniform(0.7, 1.3)  # 70% to 130% of base
        month_target = int(base_per_month * variation)
        monthly_targets[month_key] = month_target

    # Distribute remaining commits
    while remaining > 0:
        month_key = random.choice(months)
        monthly_targets[month_key] += 1
        remaining -= 1

    # Ensure no month is too low (at least 60% of average)
    avg = total_target / len(months)
    for month_key in monthly_targets:
        if monthly_targets[month_key] < avg * 0.6:
            monthly_targets[month_key] = int(avg * 0.6)

    return monthly_targets


def create_commit(date_str, repo_path="."):
    """Create a single commit with specific date"""
    # Add line to file
    with open(os.path.join(repo_path, "contributions.txt"), "a") as f:
        f.write(f"{date_str}\n")

    # Git commit
    subprocess.run(["git", "add", "contributions.txt"],
                   capture_output=True, cwd=repo_path)

    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    subprocess.run(["git", "commit", "-m", "Contribution"],
                   env=env, capture_output=True, cwd=repo_path)


def main():
    print("=" * 60)
    print("GitHub Contribution Generator")
    print("Target: 500-600 contributions per year")
    print("=" * 60)

    # Get input
    start = input("\n📅 Start date (YYYY-MM-DD): ").strip()
    end = input("📅 End date (YYYY-MM-DD): ").strip()

    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    # Calculate targets
    total_target, per_year = calculate_yearly_distribution(start_date, end_date)
    monthly_targets = distribute_monthly(start_date, end_date, total_target)

    # Show summary
    print(f"\n{'=' * 60}")
    print("CONFIGURATION:")
    print(f"{'=' * 60}")
    print(f"  📅 Date range: {start} to {end}")
    print(f"  🎯 Target per year: ~{per_year} contributions")
    print(f"  📊 Total target: {total_target} contributions")
    print(f"  📆 Duration: {(end_date - start_date).days + 1} days")
    print(f"{'=' * 60}")
    print("\nPress ENTER to start...")
    input()

    # Initialize contributions file
    if not os.path.exists("contributions.txt"):
        with open("contributions.txt", "w") as f:
            f.write("# GitHub Contributions\n")
        subprocess.run(["git", "add", "contributions.txt"])
        subprocess.run(["git", "commit", "-m", "Initial commit"])
        print("✓ Initialized contributions file\n")

    total_created = 0
    current = start_date

    print("Starting generation...\n")

    # Process each month
    while current <= end_date:
        month_key = (current.year, current.month)
        month_name = current.strftime("%B %Y")

        # Get month boundaries
        month_start = current.replace(day=1)
        if current.month == 12:
            month_end = current.replace(day=31)
        else:
            next_month = current.replace(month=current.month + 1, day=1)
            month_end = next_month - timedelta(days=1)

        actual_start = max(current, month_start)
        actual_end = min(end_date, month_end)
        days_in_range = (actual_end - actual_start).days + 1

        # Get target for this month
        month_target = monthly_targets.get(month_key, 0)

        if month_target == 0:
            print(f"📅 {month_name}: Skipping (no commits)")
            current = actual_end + timedelta(days=1)
            continue

        print(f"📅 {month_name}: Target {month_target} commits over {days_in_range} days")

        # Distribute commits across days - more consistent, fewer gaps
        daily_commits = []
        remaining = month_target

        # First pass: give each day at least 1 commit (75% of days)
        for i in range(days_in_range):
            if random.random() < 0.75 and remaining > 0:  # 75% of days have activity
                commits = 1
                daily_commits.append(commits)
                remaining -= commits
            else:
                daily_commits.append(0)

        # Second pass: add more commits naturally
        for i in range(days_in_range):
            if remaining <= 0:
                break

            if daily_commits[i] > 0:  # Days that already have commits
                # Add 1-3 more commits
                extra = random.randint(1, min(3, remaining))
                daily_commits[i] += extra
                remaining -= extra

        # Third pass: distribute any remaining
        while remaining > 0:
            day_idx = random.randint(0, days_in_range - 1)
            if daily_commits[day_idx] < 6:  # Cap at 6 per day for natural look
                daily_commits[day_idx] += 1
                remaining -= 1

        # Create commits
        day = actual_start
        month_created = 0

        for num_commits in daily_commits:
            for i in range(num_commits):
                # Random time (9 AM - 10 PM)
                hour = random.randint(9, 22)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                commit_time = day.replace(hour=hour, minute=minute, second=second)
                date_str = commit_time.strftime("%Y-%m-%d %H:%M:%S")

                create_commit(date_str)
                month_created += 1
                total_created += 1

                # Progress every 20 commits
                if total_created % 20 == 0:
                    print(f"  ✓ {total_created} commits created...", flush=True)

            day += timedelta(days=1)

        print(f"  ✅ {month_name}: {month_created} commits created\n")

        # Move to next month
        current = actual_end + timedelta(days=1)

    print("=" * 60)
    print(f"✅ COMPLETE!")
    print(f"   Total commits created: {total_created}")
    print(f"   Target was: {total_target}")
    print("=" * 60)
    print("\n📤 Next step: git push -f origin main")
    print("=" * 60)


if __name__ == "__main__":
    main()