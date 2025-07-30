import logging
import sys

logging.basicConfig(stream=sys.stdout)


class Parser:
    def __init__(self, debug=False) -> None:
        self.params = dict()
        logging. = logging.getLogger("fodcm")
        if debug is True:
            logging..setLevel(logging.DEBUG)
        else:
            logging..setLevel(logging.INFO)
        self.lines = []
        # consoleHandler = logging.StreamHandler()
        # consoleHandler.setLevel(logging.DEBUG)

        # create formatter
        # formatter = logging.Formatter(
        #     "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        # )

        # add formatter to ch
        # consoleHandler.setFormatter(formatter)

        # add ch to logger
        # logging..addHandler(consoleHandler)

    def parse(self, filename):
        f = open(filename, "r")
        text = f.read()
        f.close()

        self.lines = text.splitlines()
        # drop comments
        # drop empty line
        # replace \t with space

        while len(self.lines) != 0:
            line = self.lines.pop(0)

            if line == "":
                continue

            if line[0] == "*":
                continue

            # logging..info('Line:%s',line)
            # print('Line:', line)

            self.process(line)

        return self.params

    def process(self, line):
        line = line.replace("\t", "")
        # logging..debug('Process:%s', line)
        tokens = line.split(" ")

        match tokens[0]:
            case "KONSERVIERUNG_FORMAT":
                logging..debug("KONSERVIERUNG_FORMAT:%s", tokens[1])
                self.params["version"] = tokens[1]
            case "FESTWERT":
                self.festwert(tokens)
            case "FESTWERTEBLOCK":
                self.festwertblock(tokens)
            case "KENNLINIE":
                self.kennlinie(tokens)
            case "KENNFELD":
                self.kennfeld(tokens)
            case "FESTKENNLINIE":
                self.festkennlinie(tokens)
            case "FESTKENNFELD":
                self.festkennfeld(tokens)
            case "GRUPPENKENNLINIE":
                self.gruppenkennlinie(tokens)
            case "GRUPPENKENNFELD":
                self.gruppenkennfeld(tokens)
            case "STUETZSTELLENVERTEILUNG":
                self.stuetzstellungverteilung(tokens)
            case "FUNKTIONEN":
                self.funktionen(tokens)
            case "VARIANTENKODIERUNG":
                self.variantenkondierung(tokens)
            case "MODULKOPF":
                self.modulkopf(tokens)
            case "LANGNAME":
                logging..debug("LANGNAME:%s", tokens[1])
                return tokens[1]
            case "END":
                return "END"
            case _:
                return

    def festwert(self, tokens):
        res = dict()
        res["NAME"] = tokens[1]
        logging..debug("FESTWERT:%s", res["NAME"])
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))
        #    res[data[0]]=data[1]
        #    data=self.process(self.lines.pop(0))
        # return res

    def festwertblock(self, lines):
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))

    def kennlinie(self, lines):
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))

    def kennfeld(self, lines):
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))

    def festkennlinie(self, lines):
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))

    def festkennfeld(self, lines):
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))

    def gruppenkennlinie(self, lines):
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))

    def gruppenkennfeld(self, tokens):
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))

    def stuetzstellungverteilung(self, lines):
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))

    def funktionen(self, lines):
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))

    def variantenkondierung(self, lines):
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))

    def modulkopf(self, lines):
        data = self.process(self.lines.pop(0))
        while data != "END":
            data = self.process(self.lines.pop(0))
