import sys
import yaml
from .evaluator import run_evaluation

def main(argv=None):
    cfg = yaml.safe_load(open("config.yaml"))
    mode = cfg["mode"]
    # you can accept args to override mode/map
    run_evaluation(cfg)

if __name__ == "__main__":
    sys.exit(main())
