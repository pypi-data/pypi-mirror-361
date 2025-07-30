"""
Command line interface for WAV Finder.
"""

import argparse
import sys
from .finder import WavFinder


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Find WAV files from URLs or local paths",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wav-finder https://example.com/audio-files/
  wav-finder /path/to/audio/directory
  wav-finder /path/to/single/file.wav
        """
    )
    
    parser.add_argument(
        'path',
        help='URL or local path to search for WAV files'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file to save results (optional)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Create WAV finder instance
    finder = WavFinder()
    
    if args.verbose:
        print(f"Searching for WAV files in: {args.path}")
    
    # Find WAV files
    wav_files = finder.find_wav_files(args.path)
    
    if args.verbose:
        print(f"Found {len(wav_files)} WAV file(s)")
    
    # Output results
    if wav_files:
        if args.output:
            # Save to file
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    for wav_file in wav_files:
                        f.write(f"{wav_file}\n")
                print(f"Results saved to: {args.output}")
            except IOError as e:
                print(f"Error writing to file {args.output}: {e}")
                sys.exit(1)
        else:
            # Print to stdout
            for wav_file in wav_files:
                print(wav_file)
    else:
        print("No WAV files found.")
        sys.exit(1)


if __name__ == '__main__':
    main() 