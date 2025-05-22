#!/usr/bin/env python3
"""
PNGer: A Python script to hide files within a pseudo-PNG structure and extract them.

This script allows embedding an arbitrary file into a carrier file that mimics a
PNG image by prepending a standard PNG header. It can also extract the original
file from such a carrier PNG.
"""
import sys
import argparse

# Standard PNG header and a minimal IEND chunk, used to make the output look like a PNG.
FAKE_IMAGE_HEADER = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52\x00\x00\x00\x80\x00\x00\x00\x44\x08\x02\x00\x00\x00\xc6\x25\xaa\x3e\x00\x00\x00\xc2\x49\x44\x41\x54\x78\x5e\xed\xd4\x81\x06\xc3\x30\x14\x40\xd1\xb7\x34\xdd\xff\xff\x6f\xb3\x74\x56\xea\x89\x12\x6c\x28\x73\xe2\xaa\x34\x49\x03\x87\xd6\xfe\xd8\x7b\x89\xbb\x52\x8d\x3b\x87\xfe\x01\x00\x80\x00\x00\x10\x00\x00\x02\x00\x40\x00\x00\x08\x00\x00\x01\x00\x20\x00\x00\x04\x00\x80\x00\x00\x10\x00\x00\x02\x00\x40\x00\x00\x08\x00\x00\x01\x00\x20\x00\x00\x00\xd4\x5e\x6a\x64\x4b\x94\xf5\x98\x7c\xd1\xf4\x92\x5c\x5c\x3e\xcf\x9c\x3f\x73\x71\x58\x5f\xaf\x8b\x79\x5b\xee\x96\xb6\x47\xeb\xf1\xea\xd1\xce\xb6\xe3\x75\x3b\xe6\xb9\x95\x8d\xc7\xce\x03\x39\xc9\xaf\xc6\x33\x93\x7b\x66\x37\xcf\xab\xbf\xf9\xc9\x2f\x08\x80\x00\x00\x10\x00\x00\x02\x00\x40\x00\x00\x08\x00\x00\x01\x00\x20\x00\x00\x04\x00\x80\x00\x00\x10\x00\x00\x02\x00\x40\x00\x00\x08\x00\x00\x01\x00\x20\x00\x00\x8c\x37\xdb\x68\x03\x20\xfb\xed\x96\x65\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"
CHUNK_SIZE = 4096  # 4KB chunks for file operations

def pngit(input_path, output_path):
    """
    Embeds the content of input_path into output_path, prepending a fake PNG header.

    Args:
        input_path (str): Path to the input file to be hidden.
        output_path (str): Path to the output file which will appear as a PNG.

    Raises:
        SystemExit: If file operations fail due to FileNotFoundError, PermissionError,
                    or other IOErrors.
    """
    try:
        with open(output_path, "wb") as output_file:
            output_file.write(FAKE_IMAGE_HEADER)
            with open(input_path, "rb") as input_file:
                while True:
                    chunk = input_file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    output_file.write(chunk)
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied. Check read/write permissions for '{input_path}' or '{output_path}'.")
        sys.exit(1)
    except IOError as e:
        print(f"An I/O error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

def unpngit(input_path, output_path):
    """
    Extracts the hidden file from a pseudo-PNG file created by pngit.

    It skips the FAKE_IMAGE_HEADER and writes the remaining data to output_path.

    Args:
        input_path (str): Path to the input pseudo-PNG file.
        output_path (str): Path to the output file where extracted data will be saved.

    Raises:
        SystemExit: If file operations fail due to FileNotFoundError, PermissionError,
                    or other IOErrors, or if the input file is smaller than the header.
    """
    header_length = len(FAKE_IMAGE_HEADER)
    try:
        with open(input_path, "rb") as input_file:
            # Check if the file is at least as long as the header
            input_file.seek(0, 2) # Seek to end of file
            file_size = input_file.tell()
            if file_size < header_length:
                print(f"Error: Input file '{input_path}' is smaller than the PNG header. Cannot be an unpng target.")
                sys.exit(1)
            input_file.seek(header_length) # Skip the header

            with open(output_path, "wb") as output_file:
                while True:
                    chunk = input_file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    output_file.write(chunk)
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied. Check read/write permissions for '{input_path}' or '{output_path}'.")
        sys.exit(1)
    except IOError as e:
        print(f"An I/O error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

def main():
    """
    Parses command-line arguments and calls the appropriate function (pngit or unpngit).
    """
    parser = argparse.ArgumentParser(
        description='Embeds a file within a fake PNG or extracts it.',
        formatter_class=argparse.RawTextHelpFormatter # To keep usage examples formatted
    )
    parser.add_argument(
        '-i', '--input',
        help='The input file.\nFor pnging: the file to hide.\nFor unpnging: the file to extract from (the .png).',
        required=True
    )
    parser.add_argument(
        '-o', '--output',
        help='The output file.\nFor pnging: the new .png file.\nFor unpnging: the extracted original file.',
        required=True
    )
    parser.add_argument(
        '-u', '--unpng',
        action='store_true',
        help='Use this flag to unpng (extract from) a file that looks like a png.'
    )

    args = parser.parse_args()

    # Re-print usage if arguments are not logical (though argparse required=True handles most of this)
    # This is a fallback or for more complex validation if needed in the future.
    if not args.input or not args.output: # Should be caught by required=True
        print("Usage:")
        print("\tpython pnger.py -i <from_file> -o <to_file>")
        print("\tpython pnger.py -i <from_file.png> -o <to_file_extracted> -u")
        print("Example (hiding a file):")
        print("\tpython pnger.py -i NSASecrets.txt -o NSASecrets.png")
        print("Example (extracting a file):")
        print("\tpython pnger.py -i NSASecrets.png -o NSASecrets_recovered.txt --unpng")
        sys.exit(1)


    if args.unpng:
        unpngit(args.input, args.output)
    else:
        pngit(args.input, args.output)

if __name__ == '__main__':
    main()
