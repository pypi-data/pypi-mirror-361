import html_compose.live as live

live.server(
    # counter.py contents:
    #
    # from time import sleep, time
    # start = time()
    # while True:
    #     now = time()
    #     print(int(now - start))
    #     sleep(1)
    daemon=live.ShellCommand("python3 counter.py"),
    daemon_delay=1,
    conds=[
        live.WatchCond(
            path_glob="src/**/*.py", action=live.ShellCommand("date")
        ),
        live.WatchCond(
            path_glob="./static/sass/**/*.scss",
            action=live.ShellCommand(
                ["sass", "--update", "static/sass:static/css"]
            ),
            no_reload=True,
        ),
        live.WatchCond(path_glob="./static/css/", action=None, delay=0.5),
    ],
)
