# PNGer

**PNGer is a python script used to convert files into a png file that most websites will accept**

```bash
$ shasum README.md 
96313bbb41092391c6df854d0bf6c9b7e1fe71fd  README.md
$ python pnger.py -i README.md -o testing.png
$ python pnger.py -i testing.png -o test.txt -u
$ shasum test.txt 
96313bbb41092391c6df854d0bf6c9b7e1fe71fd  test.txt
```

The outfile of an unpng'd file that was png'd with this program has an identical shasum.
