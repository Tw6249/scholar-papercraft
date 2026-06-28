from pathlib import Path


def main() -> None:
    Path("figures").mkdir(exist_ok=True)
    Path("figures/ablation.pdf").write_bytes(b"%PDF-1.4\n")


if __name__ == "__main__":
    main()

