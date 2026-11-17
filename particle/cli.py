import argparse
import particle as m


def main():
    ap = argparse.ArgumentParser(description="粒子池与深度排序")
        ap.add_argument("--frames", type=int, default=60)
        ap.add_argument("--out", required=True)
    a = ap.parse_args()
        print("TODO")


if __name__ == "__main__":
    main()
