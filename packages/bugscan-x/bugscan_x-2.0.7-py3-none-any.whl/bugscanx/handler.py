def run_1():
    from bugscanx.modules.scanners import host_scanner
    host_scanner.main()


def run_2():
    from bugscanx.modules.scrapers.subfinder import subfinder
    subfinder.main()


def run_3():
    from bugscanx.modules.scrapers.iplookup import iplookup
    iplookup.main()


def run_4():
    from bugscanx.modules.others import file_toolkit
    file_toolkit.main()


def run_5():
    from bugscanx.modules.scanners import port_scanner
    port_scanner.main()


def run_6():
    from bugscanx.modules.others import dns_records
    dns_records.main()


def run_7():
    from bugscanx.modules.others import host_info
    host_info.main()


def run_8():
    from bugscanx.modules.others import help
    help.main()


def run_9():
    from bugscanx.modules.others import update
    update.main()
