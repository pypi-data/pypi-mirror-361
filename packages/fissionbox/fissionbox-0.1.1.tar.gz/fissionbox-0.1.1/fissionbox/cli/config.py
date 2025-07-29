import os

FISSIONBOX_HOST = os.getenv("FISSIONBOX_HOST", "https://api.fissionbox.ai")
FISSIONBOX_API_KEY = os.getenv(
    "FISSIONBOX_API_KEY", # this is jwt token for dev environment
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJuYW1lc3BhY2VfaWQiOiJkZXYifQ.Rfjf4fAXrvN0xAlQytHSgVuzNJf3pPz1CHVGuvUPU8c",
)