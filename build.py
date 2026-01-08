#!/usr/bin/env -S uv run --script

import re

def main():
    input_file_name = "qcmx.sty"
    output_file_name = "quantumcubemodel.sty"
    with open(input_file_name, "r", encoding="utf-8") as input_file:
        with open(output_file_name, "w", encoding="utf-8") as output_file:
            for line in input_file.readlines():
                m = re.match(r".*\\input\{(?P<file>.*)\}", line)
                if m:
                    with open(m[1], "r", encoding="utf-8") as f:
                        output_file.write("\n")
                        output_file.write(f"%region FILE: {m[1]}")
                        output_file.write("\n")
                        f_lines = [l.replace("#", "##") for l in f.readlines()]
                        output_file.writelines(f_lines)
                        output_file.write("\n")
                else:
                    output_file.write(line)

if __name__ == "__main__":
    main()