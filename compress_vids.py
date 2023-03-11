''' Useful project links for FFMPEG options:
https://unix.stackexchange.com/questions/28803/how-can-i-reduce-a-videos-size-with-ffmpeg
https://ottverse.com/change-resolution-resize-scale-video-using-ffmpeg/
'''

import os
import errno
import argparse
import time
import subprocess
import shutil

from pymediainfo import MediaInfo


# ############################# Constants ###############################


ALLOWED_SCALES = [
    'half',
    'third',
    'quarter',
    'fifth'
]


# ############################# Methods ###############################


def create_directory(directory):
    ''' Creates a directory if it does not already exist.
    '''
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def vprint(verbose, *args, **kwargs):
    ''' Prints only if verbose is True.
    '''
    if verbose:
        print(*args, **kwargs)


def compress_file(infile, outfile, minsize, c_args, verbose=False):
    ''' Parses and compresses known image format files above a specified
        minimum size.

    Args:
        infile: Input file path.
        outfile: Output file path (including name).
        minsize: Minimum file size to compress (in bytes). Files below
            minimum size are copied directly.
        c_args: Compression args for ffmpeg.
        verbose: Verbosity. Default = False.
    '''
    # Check if video file
    fileInfo = MediaInfo.parse(infile)
    status = False
    for track in fileInfo.tracks:
        if track.track_type == "Video":
            status = True
            break

    # Copy non-video files directly
    if not status:
        vprint(verbose, f"Skipping {infile}: Not a video file")
        shutil.copy2(src=infile, dst=outfile)
        return

    # Check for minimum size
    insize = os.path.getsize(infile)
    if insize <= minsize:
        vprint(verbose, f"Skipping {infile}: Size {insize} \
            less than minsize {minsize}")
        shutil.copy2(src=infile, dst=outfile)
        return

    # Compress video file
    vprint(verbose, f"Compressing {infile} into {outfile}")
    argslist = []
    argstring = " ".join([k + " " + v for k, v in c_args.items()])
    subprocess.call(f'ffmpeg -i "{infile}" {argstring} "{outfile}"',
        shell=True)


def compress_dir(indir, outdir, minsize, recursive, c_args, verbose=False):
    ''' Parses and compresses all image format files above a specified
        minimum size in a directory.

    Args:
        indir: Input directory.
        outdir: Output directory.
        minsize: Minimum file size to compress (in bytes). Files below
            minimum size are copied directly.
        recursive: If True, subdirectories are parsed recursively, else
            they are copied.
        c_args: Compression args for ffmpeg.
        verbose: Verbosity. Default = False.
    '''
    create_directory(outdir)
    for name in os.listdir(indir):
        inpath = os.path.join(indir, name)
        outpath = os.path.join(outdir, name)
        if os.path.isfile(inpath):
            compress_file(inpath, outpath, minsize, c_args, verbose)
        elif recursive:
            compress_dir(inpath, outpath, minsize, recursive, c_args, verbose)
        else:
            shutil.copytree(src=inpath, dst=outpath, symlinks=True,
                            ignore_dangling_symlinks=True)
    vprint(verbose, 'Compressed directory {} into {}'.format(indir, outdir))


def main(args):
    ''' Runs the main logic of the tool.

    Args:
        args: Arguments.
    '''
    # Process output path
    if args.out is None:
        args.out = args.data
    if os.path.isdir(args.data):
        create_directory(args.out)

    # Process compression args
    if args.scale is None:
        c_args = {
            '-vcodec': args.vcodec,
            '-crf': args.crf,
            '-vf': args.vf
        }
    else:
        if args.scale == 'half':
            factor = 4
        elif args.scale == 'third':
            factor = 6
        elif args.scale == 'quarter':
            factor = 8
        else: # args.scale == 'fifth'
            factor = 10
        c_args = {
            '-vcodec': args.vcodec,
            '-crf': args.crf,
            '-vf': f'"scale=trunc(iw/{factor})*2:trunc(ih/{factor})*2"'
        }

    # Compress files
    if os.path.isfile(args.data):
        compress_file(args.data, args.out, args.minsize, c_args, args.verbose)
    else:
        compress_dir(args.data, args.out, args.minsize, args.recursive,
                     c_args, args.verbose)

    print('Successfully compressed: {} into {}'.format(args.data, args.out))


# ############################# Entry Point ###############################


if __name__ == '__main__':
    # Initial time
    t_init = time.time()

    # Parse arguments
    parser = argparse.ArgumentParser(description='Compress videos using \
        ffmpeg.')
    parser.add_argument('-d', '--data',
                        help='Input file/directory.')
    parser.add_argument('-o', '--out',
                        help='Output file/directory. Default: Same as \
                            input file/directory.',
                        default=None)
    parser.add_argument('-m', '--minsize',
                        help='Minimum size of a video file to compress (in bytes). \
                            Default = 0.',
                        type=int, default=0)
    parser.add_argument('-rec', '--recursive',
                        help='Recursively process subdirectories if input \
                            is a directory.',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='Increase verbosity.',
                        action='store_true')
    parser.add_argument('-vcodec', '--vcodec',
                        help='Video codec, passed directly to ffmpeg. Default: \
                        libx265', type=str, default='libx265')
    parser.add_argument('-crf', '--crf',
                        help='Contant Rate Factor. Lower CRF values correspond to \
                        higher bitrates, and hence produce higher quality videos. \
                        A reasonable range for H.265 codec may be 24 to 30.',
                        type=str, default='24')
    parser.add_argument('-s', '--scale',
                        help='Down-scaling factor from {}. This argument, if \
                        provided, will override the scale arguments provided via \
                        -vf argument.'.format(ALLOWED_SCALES),
                        choices=ALLOWED_SCALES, default=None)
    parser.add_argument('-vf', '--vf',
                        help='ffmpeg style scaling specifications.',
                        type=str, default=None)
    args = parser.parse_args()

    # Call main method
    main(args)

    # Final time
    t_final = time.time()
    print('Progam finished in {} secs.'.format(t_final - t_init))
