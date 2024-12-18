# peripage-python - python library for peripage thermal printers
# Copyright (C) 2020-2023  bitrate16 (pegasko)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import asyncio


async def main():
    import argparse
    import sys
    import peripage
    import PIL.Image

    parser = argparse.ArgumentParser(
        description='Print on a Peripage printer via bluetooth')
    parser.add_argument(
        '-m', '--mac',
        help='Bluetooth MAC address of the printer',
        required=True,
        type=str
    )
    parser.add_argument(
        '-c', '--concentration',
        help='Concentration value for printing (temperature)',
        choices=[0, 1, 2],
        metavar='[0-2]',
        type=int,
        default=0
    )
    parser.add_argument(
        '-b', '--break',
        dest='break_size',
        help='Size of the break inserted after printed image or text',
        choices=range(256),
        metavar='[0-255]',
        type=int,
        default=0
    )
    parser.add_argument(
        '-p', '--printer',
        help='Printer model selection',
        choices=peripage.PrinterType.names(),
        type=str,
        required=True
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-t', '--text',
        help='ASCII text to print. Text must be ASCII-safe and will be filtered for invalid characters',
        type=str
    )
    group.add_argument(
        '-s', '--stream',
        help='Print text received from STDIN, line by line. Text must be ASCII-safe and will be filtered for invalid characters',
        action='store_true'
    )
    group.add_argument(
        '-i', '--image',
        help='Path to the image for printing',
        type=str
    )
    group.add_argument(
        '-q', '--qr',
        help='String to convert into a QR code for printing',
        type=str
    )
    group.add_argument(
        '-e', '--introduce',
        help='Ask the printer to introduce itself',
        action='store_true'
    )
    group.add_argument(
        '-tf', '--textfile',
        help='Path of the txt file to print',
        type=str
    )
    parser.add_argument(
        '-fo', '--fontfile',
        help='Font file to use when printing txt file',
        type=str
    )
    parser.add_argument(
        '-fs', '--fontsize',
        help='Font size to use when printing txt file',
        type=int,
        default=20
    )
    parser.add_argument(
        '-lb', '--linebreak',
        help='Line break to use when printing txt file',
        type=int,
        default=2
    )

    args = parser.parse_args()

    # Open connection
    printer = peripage.Printer(args.mac, peripage.PrinterType[args.printer])
    await printer.connect()
    await printer.reset()

    # Act based on args
    if 'introduce' in args and args.introduce:

        # print('Hello, my name is Harold..')
        device_full = await printer.getDeviceFull()
        print(device_full.decode('ascii'))
        await printer.disconnect()
        sys.exit(0)
        
    elif 'textfile' in args and args.textfile is not None:
        await printer.setConcentration(args.concentration)
        text_file = args.textfile
        font_file = args.fontfile
        font_size = args.fontsize
        line_break = args.linebreak
        await printer.printTxtFile(text_file, font_file, font_size, line_break, 0.01, resample=PIL.Image.Resampling.BOX)

        if args.break_size > 0:
            await printer.printBreak(args.break_size)

        await printer.disconnect()

        sys.exit(0)

    elif 'stream' in args and args.stream:

        await printer.setConcentration(args.concentration)

        while True:
            try:
                line = input().rstrip()

                await printer.printlnASCII(line)

            except EOFError:
                # Input closed ^d^d
                break

        if args.break_size > 0:
            await printer.printBreak(args.break_size)

        await printer.disconnect()

        sys.exit(0)

    elif 'text' in args and args.text is not None:

        await printer.setConcentration(args.concentration)

        text = args.text.rstrip()

        if len(text) > 0:
            await printer.printASCII(text)
            await printer.flushASCII()

        if args.break_size > 0:
            await printer.printBreak(args.break_size)

        await printer.disconnect()

        sys.exit(0)

    elif 'image' in args and args.image is not None:

        await printer.setConcentration(args.concentration)

        try:
            img = PIL.Image.open(args.image)
        except:
            print(f'Failed to open image {args.image}')

        await printer.printImage(img, resample=PIL.Image.Resampling.BOX)

        if args.break_size > 0:
            await printer.printBreak(args.break_size)

        await printer.disconnect()

        sys.exit(0)

    elif 'qr' in args and args.qr is not None:

        await printer.setConcentration(args.concentration)

        await printer.printQR(args.qr)

        if args.break_size > 0:
            await printer.printBreak(args.break_size)

        await printer.disconnect()

        sys.exit(0)

    else:

        print('How did you get there?')

if __name__ == '__main__':
    asyncio.run(main())
