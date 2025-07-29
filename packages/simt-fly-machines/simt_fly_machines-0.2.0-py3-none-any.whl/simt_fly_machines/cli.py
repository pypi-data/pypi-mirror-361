# mypy: disable-error-code="import-untyped"
import fire
from simt_fly_machines.api import API

def main():
    fire.Fire(API)


if __name__ == "__main__":
    main()
