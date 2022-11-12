from browserexport.browsers.common import (
    handle_path,
    Paths,
)


from browserexport.browsers.chromium import Chromium

# https://arc.net/
class Arc(Chromium):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                # macOS only browser, so no linux/darwin distinction
                "darwin": "~/Library/Application Support/Arc/User Data/",
            },
            browser_name=cls.__name__,
        )
